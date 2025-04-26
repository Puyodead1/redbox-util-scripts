import base64
import json
import re
import uuid

from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import unpad


def guid_to_byte_array(guid_str):
    hex_str = re.sub(r"[{}-]", "", guid_str)
    bytes_data = bytes.fromhex(hex_str)
    part1 = bytes([bytes_data[3], bytes_data[2], bytes_data[1], bytes_data[0]])
    part2 = bytes([bytes_data[5], bytes_data[4]])
    part3 = bytes([bytes_data[7], bytes_data[6]])
    part4 = bytes_data[8:]
    return part1 + part2 + part3 + part4


class ByteArrayExtensions:
    m_keyValue_full = guid_to_byte_array("{776DA6AF-3033-43ee-B379-2D4F28B5F1FC}")
    m_initialVector_full = guid_to_byte_array("{F375D7E0-4572-4518-9C2F-E8F022F42AA7}")

    m_keyValue = m_keyValue_full
    m_initialVector = m_initialVector_full[:8]


def decrypt(input_array):
    padding_length = 8 - (len(input_array) % 8)
    if padding_length < 8:
        padded_input = input_array + (b"\0" * padding_length)
    else:
        padded_input = input_array

    cipher = DES3.new(ByteArrayExtensions.m_keyValue, DES3.MODE_CBC, ByteArrayExtensions.m_initialVector)

    decrypted_data = cipher.decrypt(padded_input)

    try:
        return unpad(decrypted_data, 8)
    except ValueError:
        return decrypted_data


with open("./data_files/46262057-f624-4bfd-8cca-a4914cd7be5f.dat", "r") as f:
    b64 = f.read()
    encrypted_data = base64.b64decode(b64)

    decrypted_data = decrypt(encrypted_data)

    decrypted_data = decrypted_data.decode()
    decrypted_data = json.loads(decrypted_data)
    print(json.dumps(decrypted_data, indent=4))
