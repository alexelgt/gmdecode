import json
import os
import argparse
from subprocess import call

from google.protobuf import text_format
from google.protobuf import json_format

from sharedmodules.pokemon.regex import MOVE_GYMS_REGEX, FAMILY_REGEX, EXTENDED_POKEMON_REGEX

parser = argparse.ArgumentParser()

parser.add_argument("-g", "--gamemaster_filename",
                    help="Game Master file name")

args = parser.parse_args()

RUN_FOLDER = os.path.dirname(__file__) + "/"

proto_filename = "gamemaster.proto"

files_folder = f"{RUN_FOLDER}files"
proto_folder = f"{files_folder}/protofiles"
gamemaster_input_folder = f"{files_folder}/gamemasterinput"
gamemaster_output_folder = f"{files_folder}/gamemasteroutput"

gamemaster_json_output_file = f"{RUN_FOLDER}GAME_MASTER.json"

pythonfiles_folder = f"{RUN_FOLDER}pyproto"

pogo_gm_protos_target = "POGOProtos.Rpc.DownloadGmTemplatesResponseProto"
pogo_ga_protos_target = "POGOProtos.Rpc.AssetDigestOutProto"

blocks_meta_info = [
    {
        "block_name": "POKEMON_ID_BLOCK",
        "block_elements": [],
        "regex_find": EXTENDED_POKEMON_REGEX,
        "string_find": None,
        "element_first_level": "pokemonExtendedSettings",
        "element_second_level": "uniqueId",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "FORM_BLOCK",
        "block_elements": [],
        "regex_find": EXTENDED_POKEMON_REGEX,
        "string_find": None,
        "element_first_level": "pokemonExtendedSettings",
        "element_second_level": "form",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "FAMILY_BLOCK",
        "block_elements": [],
        "regex_find": FAMILY_REGEX,
        "string_find": None,
        "element_first_level": "pokemonFamily",
        "element_second_level": "familyId",
        "enum_key_default_value": None,
        "enum_key_prefix": "FAMILY_",
        "enum_key_replace": [],
    },
    {
        "block_name": "MOVES_BLOCK",
        "block_elements": [],
        "regex_find": MOVE_GYMS_REGEX,
        "string_find": None,
        "element_first_level": "moveSettings",
        "element_second_level": "movementId",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "BADGE_TYPE_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "BADGE_",
        "element_first_level": "badgeSettings",
        "element_second_level": "badgeType",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "BUDDY_ACTIVITY_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "BUDDY_ACTIVITY_",
        "element_first_level": "buddyActivitySettings",
        "element_second_level": "activity",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "BUDDY_CATEGORY_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "BUDDY_CATEGORY_",
        "element_first_level": "buddyActivityCategorySettings",
        "element_second_level": "activityCategory",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "QUEST_TYPE_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "_EVOLUTION_QUEST",
        "element_first_level": "evolutionQuestTemplate",
        "element_second_level": "questType",
        "enum_key_default_value": "???",
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "QUEST_TYPE_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "QUEST_",
        "element_first_level": "questSettings",
        "element_second_level": "questType",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "ITEM_ID_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "ITEM_",
        "element_first_level": "itemSettings",
        "element_second_level": "itemId",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
    {
        "block_name": "ITEM_TYPE_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "ITEM_",
        "element_first_level": "itemSettings",
        "element_second_level": "itemType",
        "enum_key_default_value": "???",
        "enum_key_prefix": None,
        "enum_key_replace": ["ITEM_", "ITEM_TYPE_"],
    },
    {
        "block_name": "ITEM_CATEGORY_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "ITEM_",
        "element_first_level": "itemSettings",
        "element_second_level": "category",
        "enum_key_default_value": "???",
        "enum_key_prefix": None,
        "enum_key_replace": ["ITEM_", "ITEM_CATEGORY_"],
    },
    {
        "block_name": "LOCATION_CARD_BLOCK",
        "block_elements": [],
        "regex_find": None,
        "string_find": "LC_",
        "element_first_level": "locationCardSettings",
        "element_second_level": "locationCard",
        "enum_key_default_value": None,
        "enum_key_prefix": None,
        "enum_key_replace": [],
    },
]

# Regex to obtain enums data
# .*"(.*)".*\n\tpublic const.* = (\d{1,});
# .*".*POKEMON_(.*)".*\n\tpublic const.* = (\d{1,});
# .*".*(FAMILY_.*)".*\n\tpublic const.* = (\d{1,});
#   $1 = $2;


# .*".*(MOVE|VN_BM)_(.*)".*\n\tpublic const.* = (\d{1,});
#   $1_$2 = $3;

# RewardOneofCase
# .*RewardOneofCase (.*) = (\d{1,});
#   $1 = $2;


def read_txt_file(path_to_file):
    try:
        with open(path_to_file, 'r', encoding="utf-8") as txt_file:
            txt_data = txt_file.read()

            if txt_data == "":
                return None
            return txt_data
    except:
        return None


def main():
    try:
        gamemaster_filename = args.gamemaster_filename

        call(
            f'protoc --proto_path="{proto_folder}" --python_out="{pythonfiles_folder}" --pyi_out="{pythonfiles_folder}" {proto_filename}', shell=True)

        if gamemaster_filename:
            proto_file = f"{proto_folder}/{proto_filename}"

            gamemaster_output_file = f"{gamemaster_output_folder}/{gamemaster_filename}.txt"

            call(
                f'protoc --proto_path="{proto_folder}" --decode {pogo_gm_protos_target} "{proto_file}" <"{gamemaster_input_folder}/{gamemaster_filename}"> "{gamemaster_output_file}"', shell=True)

            try:
                from pyproto.gamemaster_pb2 import DownloadGmTemplatesResponseProto

                gamemaster_txt = read_txt_file(gamemaster_output_file)

                gamemaster_txt_parsed = text_format.Parse(
                    gamemaster_txt,
                    DownloadGmTemplatesResponseProto(),
                    allow_unknown_field=True
                )

                gamemaster_json_string = json_format.MessageToJson(
                    gamemaster_txt_parsed)

                gamemaster_json = json.loads(gamemaster_json_string)

                gamemaster_template_json = gamemaster_json["template"]
                gamemaster_template_json.sort(key=lambda x: x["templateId"])

                print(f"batchId: {gamemaster_json['batchId']}")
                print("-"*10)

                try:
                    for element in gamemaster_template_json:
                        for blocks_meta_element in blocks_meta_info:
                            try:
                                if blocks_meta_element["regex_find"] is not None:
                                    is_template_id = bool(
                                        blocks_meta_element["regex_find"].search(element["templateId"]))
                                elif blocks_meta_element["string_find"] is not None:
                                    is_template_id = blocks_meta_element["string_find"] in element["templateId"]
                                else:
                                    is_template_id = False

                                if blocks_meta_element["block_name"] == "POKEMON_ID_BLOCK":
                                    if "form" in element["data"][blocks_meta_element["element_first_level"]]:
                                        continue

                                if is_template_id and isinstance(
                                        element["data"][blocks_meta_element["element_first_level"]][blocks_meta_element["element_second_level"]], int):
                                    if blocks_meta_element["enum_key_default_value"]:
                                        enum_key = blocks_meta_element["enum_key_default_value"]
                                    elif blocks_meta_element["regex_find"] is not None:
                                        _, enum_key = blocks_meta_element["regex_find"].search(
                                            element["templateId"]).groups()
                                    else:
                                        enum_key = element["templateId"]

                                    if blocks_meta_element["enum_key_prefix"]:
                                        enum_key = blocks_meta_element["enum_key_prefix"] + enum_key

                                    if len(blocks_meta_element["enum_key_replace"]) == 2:
                                        enum_key.replace(
                                            *blocks_meta_element["enum_key_replace"])

                                    enum_value = element["data"][blocks_meta_element["element_first_level"]
                                                                 ][blocks_meta_element["element_second_level"]]

                                    blocks_meta_element["block_elements"].append({
                                        enum_key: enum_value
                                    })
                            except:
                                pass
                except:
                    pass

                with open(gamemaster_json_output_file, 'w', encoding="utf-8") as f:
                    json.dump(gamemaster_template_json, f, indent=4)

                blocks_missing_enums_info = [{
                    "block_name": blocks_meta_element["block_name"],
                    "block_elements": [dict(t) for t in {tuple(d.items()) for d in blocks_meta_element["block_elements"]}]
                } for blocks_meta_element in blocks_meta_info if len(blocks_meta_element["block_elements"]) > 0]

                for blocks_missing_enums_element in blocks_missing_enums_info:
                    print(blocks_missing_enums_element["block_name"])

                    for block_element in blocks_missing_enums_element["block_elements"]:
                        for enum_key, enum_value in block_element.items():
                            print(f'{enum_key} = {enum_value};')
            except:
                pass
    except:
        pass


if __name__ == "__main__":
    main()
