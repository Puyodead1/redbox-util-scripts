import json
import re


def json_to_lua_table(data):
    if isinstance(data, dict):
        items = []
        for key, value in data.items():
            formatted_key = f'["{key}"]' if not key.isidentifier() else key
            items.append(f"{formatted_key} = {json_to_lua_table(value)}")
        return "{ " + ", ".join(items) + " }"

    elif isinstance(data, list):
        return "{ " + ", ".join(json_to_lua_table(item) for item in data) + " }"

    elif isinstance(data, str):
        return f'"{data}"'

    elif isinstance(data, bool):
        return "true" if data else "false"

    elif data is None:
        return "nil"

    else:
        return str(data)


if __name__ == "__main__":
    input_dict = {
        "box_office_gross": 133,
        "closed_captioned": False,
        "coming_soon_days": 0,
        "description": "When CIA Analyst Jack Ryan interferes with an IRA assassination, a renegade faction targets Jack and his family as revenge.\\r\\n\\r\\nRated R by the Motion Pictures of America for strong sexuality, and for language and violence.\\r\\n",
        "directors": ["Phillip Noyce"],
        "genres": {"1000": True, "1005": True, "1016": True},
        "image_file": "patriot_games.jpg",
        "long_name": "Patriot Games (Blu-ray)",
        "merchandise_date": "19920605000000",
        "national_street_date": "20241001000000",
        "number_of_players_text": "",
        "product_id": 915944,
        "product_type_id": 1,
        "rating_id": 8,
        "release_date": "19920605000000",
        "running_time": "01:57",
        "sell_thru": True,
        "sell_thru_new": False,
        "sellthru_date": "20241001000000",
        "sellthru_price": 0.0,
        "sort_date": "19920605000000",
        "sort_name": "Patriot Games (Blu-ray)",
        "starring": ["Harrison Ford", "Sean Bean", "Anne Archer"],
        "stars": 7,
        "studio": "Paramount",
    }
    # input_str = '{ "Oscar Dietz" , "Nicolas Bro" , "Samuel Ting Graf" }'

    lua_table = json_to_lua_table(input_dict)

    print(lua_table)
    # # Print the parsed results
    # for key, value in parsed_data:
    #     print(f"{key}: {value}")
