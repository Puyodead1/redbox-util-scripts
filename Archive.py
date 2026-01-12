# Represents an inventory.data file, ported from the original C# code with the addition of linear_search_for_product_id

from pathlib import Path
from datetime import datetime
from construct import Computed, Enum, Int8ul, Int32ul, Int64ul, Struct

from BinaryReaderCustom import BinaryReader

Barcode = Struct(
    "prefix" / Int8ul,
    "integer_part" / Int64ul,
    "barcode" / Computed(lambda ctx: f"{'0' * ctx.prefix}{ctx.integer_part}"),
)

Item = Struct(
    "barcode" / Barcode,
    "title_id" / Int32ul,
    "status_code"
    / Enum(
        Int8ul,
        Known=0,
        WrongTitle=1,
        Damaged=2,
        Thinned=3,
        PR1=4,
        PR2=5,
        Fraud=6,
        Rebalancing=7,
        Redeployment=8,
    ),
    "total_rental_count" / Int32ul,
)


def compress_barcode_to_bytes(barcode: str):
    """
    Compresses a barcode string into a Barcode structure

    :param barcode: barcode string
    :type barcode: str
    """
    prefix = len(barcode) - len(barcode.lstrip("0"))
    integer_part = int(barcode)
    return Barcode.build({"prefix": prefix, "integer_part": integer_part})


def compress_barcode_to_dict(barcode: str):
    """
    Compresses a barcode string into a Barcode dict

    :param barcode: barcode string
    :type barcode: str
    """
    prefix = len(barcode) - len(barcode.lstrip("0"))
    integer_part = int(barcode)
    return {"prefix": prefix, "integer_part": integer_part}


class Archive:
    def __init__(self, file_path):
        self.file_path = str(file_path)
        self.file = open(self.file_path, "rb+")
        self.reader = BinaryReader(self.file)

    def is_valid_archive(self):
        self.reader.seek(0)
        magic = self.reader.read_string(8, "ascii")
        version = self.reader.read_byte()
        return magic == "<~look~>" and version == 0

    def get_version(self):
        self.reader.seek(8)
        return self.reader.read_byte()

    def get_origin_machine(self):
        self.reader.seek(10)
        return self.reader.read_string(32, "ascii")

    def get_flags(self):
        self.reader.seek(9)
        return self.reader.read_byte()

    def get_created_on(self):
        self.reader.seek(42)
        return self.reader.read_string(14, "ascii")

    def get_number_of_records(self):
        file_size = Path(self.file_path).stat().st_size
        return (file_size - 312) // 18

    def read_barcode(self, index: int):
        self.reader.seek(312 + index * 18)
        prefix = self.reader.read_byte()
        code = self.reader.read_uint64()
        return Archive.decompress_barcode(prefix, code)

    def read_product_id(self, index: int):
        self.reader.seek(312 + index * 18 + 9)
        return self.reader.read_uint32()

    def find_index(self, barcode: str):
        start_index = 0
        end_index = self.get_number_of_records() - 1
        while start_index <= end_index:
            mid_index = (start_index + end_index) // 2
            current_barcode = self.read_barcode(mid_index)
            if current_barcode == barcode:
                return mid_index
            if current_barcode < barcode:
                start_index = mid_index + 1
            else:
                end_index = mid_index - 1
        return -1

    def read_inventory(self, index: int):
        self.reader.seek(312 + index * 18)
        return Archive.decode(self.reader.read(18))

    def write_inventory(self, index: int, item):
        self.reader.seek(312 + index * 18)
        self.reader.write(Item.build(item))

    def linear_search_for_product_id(self, product_id: int):
        total_records = self.get_number_of_records()
        for index in range(total_records):
            current_pid = self.read_product_id(index)
            if current_pid == product_id:
                return index
        return None

    def append_record(self, record: bytes):
        # move to EOF
        self.reader.seek(0, 2)
        # write the record data
        self.reader.write(record)

    def add_record(self, data):
        record = Item.build(data)
        self.append_record(record)

    def close(self):
        if self.file:
            self.file.close()

    def rebuild(self):
        """
        Rebuild the archive file in sorted order.
        WARNING: This reads entire file into memory!
        """

        output_path = self.file_path + ".tmp"

        print("Reading all records...")
        all_records = []
        total = self.get_number_of_records()

        for i in range(total):
            if i % 100000 == 0:
                print(f"Progress: {i:,}/{total:,}")
            all_records.append(self.read_inventory(i))

        print("Sorting records...")
        all_records.sort(
            key=lambda r: Archive.decompress_barcode(
                r.barcode.prefix, r.barcode.integer_part
            )
        )

        print("Writing sorted file...")
        # copy header
        self.reader.seek(0)
        header = self.reader.read(312)

        # update created on date to now
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        header = header[:42] + now_str.encode("ascii") + header[42 + 14 :]

        with open(output_path, "wb") as out:
            out.write(header)
            for record in all_records:
                out.write(Item.build(record))

        print(f"Rebuilt file written to temp file")
        # close current file
        self.close()
        # move old file to backup
        Path(self.file_path).rename(self.file_path + ".bak")
        # replace original file
        Path(output_path).rename(self.file_path)
        # reopen file
        self.file = open(self.file_path, "rb+")
        self.reader = BinaryReader(self.file)
        print("Rebuild complete.")

    @staticmethod
    def open(file_path):
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return Archive(file_path)

    @staticmethod
    def decompress_barcode(prefix: int, code: int):
        return f"{'0' * prefix}{code}"

    @staticmethod
    def decode(data):
        return Item.parse(data)
