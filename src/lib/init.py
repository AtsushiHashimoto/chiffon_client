# -*- coding:utf-8 -*-
import myutils

import argparse
import os


def parse_args():
    parser_args=argparse.ArgumentParser("CHIFFONに用いられる各モジュールの連携用スクリプト")
    parser_args.add_argument("user_id",help="CHIFFONのユーザー名")
    parser_args.add_argument("grouptag",nargs="+",help="サンプルに付加するグループタグ")
    args_client=parser_args.parse_args()
    return vars(parser_args.parse_args())


# 引数,設定ファイルから設定に関する辞書を作成
# 拡張子の組の文字列をリストに変換
def load_settings(path_conf):
    dict_conf=parse_args()
    dict_conf_file=myutils.make_dict_conf(path_conf)
    dict_conf.update(dict_conf_file)
    dict_conf["table_object_manager"]["fileexts"]=dict_conf["table_object_manager"]["fileexts"].split(",")
    return dict_conf


# CHIFFONからsession_id,recipe_idを取得
def get_chiffonid(dict_conf):
    url_session=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_sessionid"],dict_conf["user_id"]])
    session_id=myutils.get_session_id(url_session)
    print("session_id:{session_id}".format(session_id=session_id))
    url_recipe=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_recipe"],session_id])
    recipe_id=myutils.get_recipe_id(url_recipe)
    print("recipe_id:{recipe_id}".format(recipe_id=recipe_id))
    return (session_id,recipe_id)


# データ保存用ディレクトリの作成,辞書のデータ保存ディレクトリの値を絶対パスに更新
def makeImageDir(dict_conf):
    list_name_dir_exec=["table_object_manager","image_feature_extractor"]
    list_name_dir_out=["output_touch","output_release"]
    dict_abspath={}
    for name_dir_exec in list_name_dir_exec:
        for name_dir_out in list_name_dir_out:
            path_dir=os.path.join(dict_conf["chiffon_client"]["output_root"],dict_conf["session_id"],dict_conf[name_dir_exec][name_dir_out])
            dict_conf[name_dir_exec][name_dir_out]=path_dir
            myutils.makedirs_ex(path_dir)


def startTableObjectManager(dict_conf):
    if(dict_conf["product_env"]["is_product"]=="1"):
        list_opt_dir=["-P",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["output_touch"]),"-T",myutils.convert_to_cygpath(dict_conf["table_object_manager"]["output_release"])]
    else:
        list_opt_dir=["-P",dict_conf["table_object_manager"]["output_touch"],"-T",dict_conf["table_object_manager"]["output_release"]]

    list_opt_default=dict_conf["table_object_manager"]["default_options"].split()
    list_opt=list_opt_dir+list_opt_default

    if(dict_conf["product_env"]["is_product"]=="1"):
        myutils.callproc_cyg(dict_conf["table_object_manager"]["path_exec"],list_opt)

    print("TableObjectManager is opened.")
