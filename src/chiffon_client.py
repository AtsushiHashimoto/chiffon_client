# -*- coding:utf-8 -*-
import lib.init
import lib.thread

if __name__=="__main__":

    PATH_CONFIG_CLIENT="chiffon_client.conf"

    # 設定用の辞書を作成(引数,設定ファイル)
    dict_conf=lib.init.load_settings(PATH_CONFIG_CLIENT)
    dict_conf["session_id"],dict_conf["recipe_id"]=lib.init.get_chiffonid(dict_conf)

    # ディレクトリ作成(TableObjectManager,FeatureExtractor),データ保存ディレクトリのパスを更新
    lib.init.makeImageDir(dict_conf)

    # TableObjectManager起動
    lib.init.startTableObjectManager(dict_conf)

    # ループ(画像取得->スレッド作成)
    lib.thread.makeNewThreads(dict_conf)
