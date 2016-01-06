# -*- coding:utf-8 -*-
import lib.myutils
import lib.loop
import lib.init
import os
import urllib,urllib2
import sys
import subprocess
import json



if __name__=="__main__":

    # PATH_HTTP_RECOG="/ml/my_db/my_feature/svc/predict"
    PATH_CONFIG_CLIENT="chiffon_client.conf"


    # 設定用の辞書を作成(引数,設定ファイル)
    dict_conf=lib.init.load_settings(PATH_CONFIG_CLIENT)

    session_id,recipe_id=lib.init.get_chiffonid(dict_conf)

    # ディレクトリ作成(TableObjectManager,FeatureExtractor)
    lib.init.makeImageDir(dict_conf,session_id)

    # TableObjectManager起動
    # 実行ファイルのパス...設定ファイル？
    # 引数として何を渡す？
    # 画像保存先のディレクトリを渡す場合...複数？
    lib.init.startTableObjectManager(dict_conf)

    # ループ(画像取得->スレッド作成)
    lib.loop.makeNewThreads(dict_conf)

