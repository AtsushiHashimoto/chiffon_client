# -*- coding:utf-8 -*-
import lib.myutils
import lib.loop
import lib.init


if __name__=="__main__":

    # PATH_HTTP_RECOG="/ml/my_db/my_feature/svc/predict"
    PATH_CONFIG_CLIENT="chiffon_client.conf"

    # 設定用の辞書を作成(引数,設定ファイル)
    dict_conf=lib.init.load_settings(PATH_CONFIG_CLIENT)
    dict_conf["session_id"],dict_conf["recipe_id"]=lib.init.get_chiffonid(dict_conf)

    # ディレクトリ作成(TableObjectManager,FeatureExtractor),データ保存ディレクトリのパスを更新
    lib.init.makeImageDir(dict_conf)

    # TableObjectManager起動
    lib.init.startTableObjectManager(dict_conf)

    # ループ(画像取得->スレッド作成)
    lib.loop.makeNewThreads(dict_conf)
