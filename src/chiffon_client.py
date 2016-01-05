# -*- coding:utf-8 -*-
import lib.myutils
import lib.loop
import os
import urllib,urllib2
import sys
import subprocess
import json
import argparse



if __name__=="__main__":

    # PATH_BATCH_RUBY="batch_feature_extraction.rb"
    INT_CHECK=5
    # PATH_HTTP_RECOG="/ml/my_db/my_feature/svc/predict"

    PATH_CONFIG_CLIENT="chiffon_client.conf"    
    dict_conf={}

    # 引数取得
    parser_args=argparse.ArgumentParser("CHIFFONに用いられる各モジュールの連携用スクリプト")
    parser_args.add_argument("user_id",help="CHIFFONのユーザー名")
    parser_args.add_argument("grouptag",nargs="+",help="サンプルに付加するグループタグ")
    args_client=parser_args.parse_args()
    dict_settings=vars(parser_args.parse_args())

    # 設定ファイル読み込み
    dict_conf=lib.myutils.make_dict_conf(PATH_CONFIG_CLIENT)
    dict_settings.update(dict_conf)
    
    # CHIFFONからsession_id,recipe_idを取得
    # IPで開けない？
    # url_session="http://{ip}:{port}{path}".format(ip=dict_conf["chiffon_server"]["host"],port=dict_conf["chiffon_server"]["port"],path="/woz/session_id/{user_id}".format(user_id=dict_conf["user_id"]))
    url_session="http://chiffon.mm.media.kyoto-u.ac.jp/woz/session_id/guest"
    # url_session="http://133.3.251.221:8080/woz/session_id/guest"
    session_id=lib.myutils.get_session_id(url_session)
    # print(session_id)
    url_recipe="http://chiffon.mm.media.kyoto-u.ac.jp/woz/recipe/{session_id}".format(session_id=session_id)
    recipe_id=lib.myutils.get_recipe_id(url_recipe)

    # ディレクトリ作成(TableObjectManager,FeatureExtractor)
    list_name_dir_exec=["table_object_manager","image_feature_extractor"]
    list_name_dir_out=["output_touch","output_release"]
    for name_dir_exec in list_name_dir_exec:
        for name_dir_out in list_name_dir_out:
            path_dir=os.path.join(dict_conf["chiffon_client"]["output_root"],session_id,dict_conf[name_dir_exec][name_dir_out])
            lib.myutils.makedirs_ex(path_dir)

    # TableObjectManager起動
    # 渡すディレクトリと返すファイルのパスは？
    '''
    PATH_TOM_U=""
    PATH_TOM_W=subprocess.call(["cygpath","-w",PATH_TOM_U])
    subprocess.call([PATH_TOM_W,dir_img,filepath_output])    
    '''

    # ループ(画像取得->スレッド作成)
    # "table_object_manager"は設定ファイルから得る or パスの末尾をカット
    path_dir_image_TOM=os.path.join(dict_conf["chiffon_client"]["output_root"],session_id,"table_object_manager")
    while(True):
        lib.loop.makeNewThreads(path_dir_image_TOM,dict_conf)
