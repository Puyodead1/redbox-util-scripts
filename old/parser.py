import json
import re


def parse_string(input_str):
    if re.match(r"\{\s*(?:\"[^\"]*\"\s*,\s*)*(?:\"[^\"]*\"\s*)?\}", input_str):
        return re.findall(r'"([^"]+)"', input_str)
    # Remove the outer braces and trim whitespace
    input_str = input_str.strip("{} ")

    parsed_items = {}
    buffer = ""
    key = None
    in_string = False
    nested_count = 0

    # Split on commas, but handle nested structures
    i = 0
    while i < len(input_str):
        char = input_str[i]

        if char == '"':
            in_string = not in_string  # Toggle in_string flag

        # Track nested braces
        if char == "{" and not in_string:
            nested_count += 1
        elif char == "}" and not in_string:
            nested_count -= 1

        # If we encounter a comma and we are not inside a string or nested structure
        if char == "," and not in_string and nested_count == 0:
            if key is not None:
                value = buffer.strip()
                if re.match(r"\{\s*(?:\"[^\"]*\"\s*,\s*)*(?:\"[^\"]*\"\s*)?\}", value):
                    value = re.findall(r'"([^"]+)"', value)
                elif re.match(r"\{\s*(\[\d+\]\s*=\s*(true|false)\s*(,\s*)?)+\}", value):
                    value = value.strip("{} ")
                    value = re.sub(r"\[([0-9]+)\]\s*=\s*(true|false)", r"\1: \2", value)
                    value = value.replace("true", "True").replace("false", "False")
                    value = eval("{" + value + "}")
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1].replace('\\"', '"')  # Remove surrounding quotes
                else:
                    if value == "true" or value == "false":
                        value = value == "true"
                    # ints
                    elif value.isdigit():
                        value = int(value)
                    # floats
                    elif re.match(r"\d+\.\d+", value):
                        value = float(value)
                    # nil to null
                    elif value == "nil":
                        value = None

                parsed_items[key] = value

                key = None
                buffer = ""
            i += 1
            continue

        # Capture the key and value in the buffer
        if key is None:
            # If we have not started capturing a key yet, find one
            match = re.match(r"(\w+)\s*=\s*", input_str[i:])
            if match:
                key = match.group(1)
                # Move the index past the match
                i += len(match.group(0))
                continue

        buffer += char  # Append character to buffer
        i += 1

    # Capture the last key-value pair if exists
    if key and buffer:
        value = buffer.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')  # Remove surrounding quotes
        parsed_items[key] = value

    return parsed_items


def to_json(parsed_items):
    result = {}

    for k, v in parsed_items:
        if re.match(r"^{(.*)}$", v):
            result[k] = to_json(parse_string(v))
        result[k] = v


if __name__ == "__main__":
    input_str = '{ product_id = 2576 , stars = 1 , running_time = "01:26" , starring = { "Anna Faris" , "Seth Rogen" } , product_type_id = 2 , rating_id = 8 , long_name = "Observe And Report (Blu-ray)" , sort_name = "Observe And Report (Blu-ray)" , image_file = "308206812290A42CD78A352D02A9EB9C68F01D36.jpg" , description = "THIS IS A BLU RAY!  A BLU RAY DVD PLAYER IS REQUIRED! \\r\\n\\r\\nBargain hunters at Forest Ridge Mall get more than they bargained for: a chubby flasher in a ratty bathrobe. They\u2019re repulsed. Security guard Ronnie Barnhardt isn\u2019t: \u201cThis disgusting pervert is the best thing that ever happened to me!\u201d Catching the flasher may be his ticket to a real police job and to romance with a hot cosmetics-counter princess. Only one thing stands between Ronnie and destiny: a tall, handsome cop who actually knows what he\u2019s doing.\\r\\n\\r\\nRated R by the Motion Pictures of America for nudity, sexual situations, strong language, violence.\\r\\nWidescreen\\r\\nClosed Captioned" , genres = { [1004] = true , [1022] = true } , release_date = "20090922000100" , sell_thru = true , sell_thru_new = false , box_office_gross = 0 , directors = {  } , coming_soon_days = 0 , sort_date = "20090922000100" , national_street_date = "20240101000000" , closed_captioned = true , merchandise_date = "20090922000100" , number_of_players_text = "" , sellthru_date = "20240101000000" , sellthru_price = 0.00 , studio = "Warner Bros." }'
    # input_str = '{ "Oscar Dietz" , "Nicolas Bro" , "Samuel Ting Graf" }'

    parsed_data = parse_string(input_str)

    print(json.dumps(parsed_data, indent=4))
    # # Print the parsed results
    # for key, value in parsed_data:
    #     print(f"{key}: {value}")
