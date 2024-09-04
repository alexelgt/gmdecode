import json
import os
import argparse
from subprocess import call

from google.protobuf import text_format
from google.protobuf import json_format

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

                # # BADGE_TYPE
                # for element in gamemaster_template_json:
                #     if "BADGE_" in element["templateId"] and isinstance(element["data"]["badgeSettings"]["badgeType"], int):
                #         print(element["templateId"], "=", element["data"]
                #               ["badgeSettings"]["badgeType"], ";")

                with open(gamemaster_json_output_file, 'w', encoding="utf-8") as f:
                    json.dump(gamemaster_template_json, f, indent=4)
            except:
                pass
    except:
        pass


if __name__ == "__main__":
    main()
