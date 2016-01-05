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
def load_settings(path_conf):
    dict_conf=parse_args()
    dict_conf_file=myutils.make_dict_conf(path_conf)
    dict_conf.update(dict_conf_file)
    return dict_conf


# CHIFFONからsession_id,recipe_idを取得
# IPで開けないっぽい？
def get_chiffonid(dict_conf):
    
    # url_session="http://{ip}:{port}{path}".format(ip=dict_conf["chiffon_server"]["host"],port=dict_conf["chiffon_server"]["port"],path="/woz/session_id/{user_id}".format(user_id=dict_conf["user_id"]))
    # url_session="http://133.3.251.221:8080/woz/session_id/guest"
    url_session="http://chiffon.mm.media.kyoto-u.ac.jp/woz/session_id/guest"
    session_id=myutils.get_session_id(url_session)    
    # print(session_id)

    url_recipe="http://chiffon.mm.media.kyoto-u.ac.jp/woz/recipe/{session_id}".format(session_id=session_id)
    recipe_id=myutils.get_recipe_id(url_recipe)
    return (session_id,recipe_id)


# データ保存用ディレクトリの作成
# ディレクトリ名指定方法は要修正
def makeImageDir(dict_conf,session_id):
    list_name_dir_exec=["table_object_manager","image_feature_extractor"]
    list_name_dir_out=["output_touch","output_release"]
    for name_dir_exec in list_name_dir_exec:
        for name_dir_out in list_name_dir_out:
            path_dir=os.path.join(dict_conf["chiffon_client"]["output_root"],session_id,dict_conf[name_dir_exec][name_dir_out])
            myutils.makedirs_ex(path_dir)
