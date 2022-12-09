""" xml to trans dict"""
import json
from pathlib import Path
from collections import defaultdict, OrderedDict

import xmltodict  # 第三方库，需要 pip install

config_file = Path("config.json")


def main():
    """ main """
    # 这些文件夹中包含若干从 xTranslator 中导出的 XML 文件
    xml_folders, out_folder = get_config()

    # 1. xml to dict
    # pkg_data_dict[pkg][type_key] = [item,item,item,...]
    # pkg_data_dict[汉化包][类型] = [翻译信息,翻译信息,翻译信息,...]
    pkg_data_dict: dict = xml_to_dict(xml_folders)

    # 2. dict_by_pkg >> dict_by_type
    # dict[pkg][type][id] >> dict[type][id][pkg]
    trans_by_type = dict_to_trans_by_type(pkg_data_dict, out_folder)

    # 4. convert to machine use trans file
    # only keep en >> cn
    # en \t ank \t uno \t ...
    # to_type_trans_text(trans_by_type, out_folder)

    # write json file for every type
    # to_type_trans_files(simple_trans_dict, out_folder)
    to_type_trans_json(trans_by_type, out_folder)


def get_config() -> (dict, Path):
    """ load and check config file """
    if not config_file.exists():
        raise FileNotFoundError("未找到config.json文件，无法读取配置。")

    try:
        config: dict = json.loads(Path("config.json").read_text("UTF8"))
    except Exception as e:
        print("无法读取或解析JSON，请检查config.json文件")
        raise e

    if "xml_folders" not in config:
        raise ValueError("config.json格式错误，未找到 'xml_folders' 属性")
    if "output" not in config:
        raise ValueError("config.json格式错误，未找到 'output' 属性")

    xml_folders: dict = config["xml_folders"]
    out_folder = config["output"]

    for name, folder in xml_folders.items():
        if not Path(folder).exists():
            raise FileNotFoundError(f"未找到 {folder} 文件夹")

    if not Path(out_folder).exists():
        try:
            Path(out_folder).mkdir()
        except Exception as e:
            print(f"未找到 {out_folder} 文件夹，且无法创建")
            raise e

    return xml_folders, out_folder


def xml_to_dict(trans_xml_folders):
    """
    将所有文件中的 XML 文件转化为python dict

    return pkg_data_dict

    pkg_data_dict[pkg][type_key] = [item,item,item,...]
    pkg_data_dict[汉化包][类型] = [翻译信息,翻译信息,翻译信息,...]
    """
    pkg_data_dict = {}  # name: pkg_data

    for pkg_name, xml_folder in trans_xml_folders.items():
        print("process trans folder: ", xml_folder)

        """ pkg_data 一个汉化包的所有数据
        pkg_data[type_key][list of items]
        e.g. {
            FACT:FULL [item, item, ...]
            QUST:NNAM [item, item, ...]
            BOOK:FULL [item, item, ...]
        }
        """
        pkg_data = defaultdict(list)

        for xml_file in Path(xml_folder).iterdir():

            is_xml_file = xml_file.name.lower().endswith(".xml")
            if not is_xml_file:
                continue

            print("\t\tconvert xml to dict: ", xml_file)

            # 1. xml >> python dict
            xml_text = xml_file.read_text("UTF8")
            data_dict = xmltodict.parse(xml_text)

            dlc_name = data_dict["SSTXMLRessources"]["Params"]["Addon"]
            item_list = data_dict["SSTXMLRessources"]["Content"]["String"]

            # 2. xml dict >>>> pkg data dict
            #    list of item >>>> pkg_data[type][id]=item
            if isinstance(item_list, OrderedDict):
                type_key = item_list["REC"]
                if not isinstance(item_list["REC"], str):
                    type_key = item_list["REC"]["#text"]

                item_list["DLC"] = dlc_name
                item_list["PKG"] = pkg_name
                pkg_data[type_key].append(item_list)
            else:
                for item in item_list:
                    type_key = item["REC"]

                    if not isinstance(item["REC"], str):
                        type_key = item["REC"]["#text"]

                    item["DLC"] = dlc_name
                    item["PKG"] = pkg_name
                    pkg_data[type_key].append(item)

        pkg_data_dict[pkg_name] = pkg_data
    return pkg_data_dict


def dict_to_trans_by_type(pkg_data_dict, out_folder):
    """
    dict[pkg][type][id] >> dict[type][id][pkg]
    """
    trans_by_type = defaultdict(dict)
    for pkg, pkg_data in pkg_data_dict.items():
        for type_key, type_data in pkg_data.items():
            for item in type_data:
                key = item["DLC"] + "_" + item["@sID"]
                if key not in trans_by_type[type_key]:
                    trans_by_type[type_key][key] = {
                        "DLC": item["DLC"],
                        "@List": item["@List"],
                        "@sID": item["@sID"],
                        "EDID": item["EDID"],
                        "EN": item["Source"],
                    }
                    if not isinstance(item["REC"], str):
                        trans_by_type[type_key][key]["REC@id"] = item["REC"]["@id"]
                        trans_by_type[type_key][key]["REC@idMax"] = item["REC"]["@idMax"]
                trans_by_type[type_key][key][item["PKG"]] = item["Dest"]

    print("save full json file......")
    # save json file
    json_str = json.dumps(trans_by_type, ensure_ascii=False, indent=2)
    json_file = Path(out_folder) / "full_dict.json"
    json_file.write_text(json_str, encoding="UTF8")
    return trans_by_type


def to_type_trans_json(simple_trans_dict: dict, out_folder: str):
    """ trans dict to sub json file """
    print("convert and save type dict txt file......")
    out_folder: Path = Path(out_folder) / "type_trans_json"
    out_folder.mkdir(exist_ok=True)

    for type_key, type_data in simple_trans_dict.items():
        file_name = type_key.replace(":", "_") + ".json"
        file_path = out_folder / file_name
        file_path.write_text(json.dumps(type_data, indent=2, ensure_ascii=False), "UTF8")


def to_type_trans_text(simple_trans_dict, out_folder):
    """ trans dict to txt file """
    print("convert and save type dict txt file......")
    splitter = "\t"
    splitter_tag = "<tmp_tab>"
    out_folder = (Path(out_folder) / "type_trans_txt")
    out_folder.mkdir(exist_ok=True)
    for type_key, type_data in simple_trans_dict.items():
        type_file = out_folder / (type_key.replace(":", "_") + ".txt")

        file_str = ""
        for key, item in type_data.items():
            try:
                line = ""
                line += item["DLC"] + splitter_tag
                line += item["@List"] + splitter_tag
                line += item["@sID"] + splitter_tag
                line += item["EDID"] + splitter_tag
                line += item["EN"] if item["EN"] else " " + splitter_tag
                line += item["ANK"] if "ANK" in item and item["ANK"] else " " + splitter_tag
                line += item["Official"] if "Official" in item and item["Official"] else " " + splitter_tag
                line += item["Reconquista"] if "Reconquista" in item and item["Reconquista"] else " " + splitter_tag
                line += item["Unofficial"] if "Unofficial" in item and item["Unofficial"] else " " + splitter_tag

                line = line.replace('\t', "<tab>")
                line = line.replace("\n"+u'\u3000', "<break_line>")
                line = line.replace("\n", "<break_line>")
                line = line.replace(u'\u3000', "  ")
                line = line.replace(splitter_tag, splitter)
            except Exception as e:
                print(item)
                raise e

            file_str += line + "\n"
        type_file.write_text(file_str, "UTF8")


if __name__ == '__main__':
    main()
