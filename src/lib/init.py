# -*- coding:utf-8 -*-
import myutils

import argparse
import os
import csv
import subprocess

LIST_NAME_DIR_EXEC={
    "table_object_manager":["output_touch","output_release","output_rawimage"],
    "object_region_box_extractor":["output_touch","output_release"],
    "image_feature_extractor":["output_touch","output_release"],
    "serv4recog":["output_touch","output_release"],
    }

# 引数,設定ファイルから設定に関する辞書を作成
# 拡張子の組の文字列をリストに変換

def parse_args():
    parser_args=argparse.ArgumentParser("CHIFFONに用いられる各モジュールの連携用スクリプト")
    parser_args.add_argument("user_id",help="CHIFFONのユーザー名")
    parser_args.add_argument("grouptag",nargs="+",help="サンプルに付加するグループタグ")
    args_client=parser_args.parse_args()
    return vars(parser_args.parse_args())


def loadSettings(path_conf):
    dict_conf=parse_args()
    dict_conf_file=myutils.make_dict_conf(path_conf)
    dict_conf.update(dict_conf_file)

    dict_conf["table_object_manager"]["fileexts"]=dict_conf["table_object_manager"]["fileexts"].split(",")

    dict_conf["serv4recog"]["convtable"]={}
    filepath_table_csv=dict_conf["serv4recog"]["path_convtable"]
    with open(filepath_table_csv,"r") as f:
        reader_table=csv.reader(f,delimiter=",")
        for row in reader_table:
            dict_conf["serv4recog"]["convtable"][row[0]]=row[1]

    return dict_conf



# CHIFFONからsession_id,recipe_idを取得

def get_sessionid(dict_conf):
    url_session=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_sessionid"],dict_conf["user_id"]])
    session_id=myutils.get_session_id(url_session)
    print("session_id:{session_id}".format(session_id=session_id))
    return session_id


def get_recipeid(dict_conf,session_id):
    url_recipe=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_recipe"],session_id])
    recipe_id=myutils.get_recipe_id(url_recipe)
    print("recipe_id:{recipe_id}".format(recipe_id=recipe_id))
    return recipe_id


def getChiffonId(dict_conf):
    session_id=get_sessionid(dict_conf)
    recipe_id=get_recipeid(dict_conf,session_id)

    return (session_id,recipe_id)



# データ保存用ディレクトリの作成
# 辞書内のディレクトリ名も絶対パスに更新

def makeImageDir(dict_conf):
    for name_dir_exec in LIST_NAME_DIR_EXEC.keys():
        for name_dir_out in LIST_NAME_DIR_EXEC[name_dir_exec]:
            abspath_dir=os.path.join(dict_conf["chiffon_client"]["output_root"],dict_conf["session_id"],dict_conf[name_dir_exec][name_dir_out])
            myutils.makedirs_ex(abspath_dir)
            dict_conf[name_dir_exec][name_dir_out]=abspath_dir



# TableObjectManager起動

def make_list_args_TOM(dict_conf):
    if(dict_conf["product_env"]["use_cygpath"]=="1"):
        list_args_dir=[ "--output_dir_for_put",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["output_touch"]),
                        "--output_dir_for_taken",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["output_release"]),
                        "--output_dir_for_background",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["output_rawimage"]),
                        "--workspace_end_filename",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["workspace_end_filename"]),
                        # TODO use input param for debug only
                        "--input","C:\ChiffonClient\TableObjectManager\camA.mp4",
                        ]
    else:
        list_args_dir=[ "--output_dir_for_put",dict_conf["table_object_manager"]["output_touch"],
                        "--output_dir_for_taken",dict_conf["table_object_manager"]["output_release"],
                        "--output_dir_for_background",dict_conf["table_object_manager"]["output_rawimage"],
                        "--workspace_end_filename",dict_conf["table_object_manager"]["workspace_end_filename"],
                        # TODO use input param for debug only
                        "--input","C:\ChiffonClient\TableObjectManager\camA.mp4",
                        ]

    list_args_opt=dict_conf["table_object_manager"]["default_options"].split()
    list_args_TOM=list_args_dir+list_args_opt
    return list_args_TOM


def startTableObjectManager(dict_conf):
    list_args_TOM=make_list_args_TOM(dict_conf)
    if(dict_conf["product_env"]["enable_table_object_manager"]=="1"):
        # myutils.callproc_cyg(dict_conf["table_object_manager"]["path_exec"],list_args_TOM)
        p = subprocess.Popen(
            [dict_conf["table_object_manager"]["path_exec"]] + list_args_TOM,
            # stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    print("TableObjectManager is started.")
    return p
