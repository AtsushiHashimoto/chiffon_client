# -*- coding:utf-8 -*-
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger("ChiffonClient")
logging.getLogger("requests").setLevel(logging.WARNING)

import lib.init
import lib.thread
import os

if __name__=="__main__":


    PATH_CONFIG_CLIENT="chiffon_client.conf"

    # 設定用の辞書を作成(引数,設定ファイル)
    # このとき拡張子の組の文字列をリストに変換
    dict_conf=lib.init.loadSettings(PATH_CONFIG_CLIENT)
    dict_conf["session_id"],dict_conf["recipe_id"]=lib.init.getChiffonId(dict_conf)

    # ディレクトリ作成(TableObjectManager,FeatureExtractorに用いる)
    # 同時に辞書のデータ保存ディレクトリの値を絶対パスに更新
    lib.init.makeImageDir(dict_conf)

    log_file_path = os.path.join(dict_conf["chiffon_client"]["output_root"],dict_conf["session_id"],dict_conf['table_object_manager']['output_log'])
    output_to = open(log_file_path, 'w')
    # TableObjectManager起動
    p = lib.init.startTableObjectManager(dict_conf, output_to)
    logger.info("Table Object Manager is started.")

    # ループ(画像取得->スレッド作成)
    try:
        lib.thread.makeNewThreads(dict_conf)
    except Exception:
        pass
    finally:
        logger.info("End")
        p.kill();
        output_to.flush();
        output_to.close();
