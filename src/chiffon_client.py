# -*- coding:utf-8 -*-
import os
import multiprocessing
import time
import urllib,urllib2
import sys
import argparse
import subprocess
import json
import yaml


PATH_BATCH_RUBY="batch_feature_extraction.rb"
INT_CHECK=5
PATH_HTTP_RECOG="/ml/my_db/my_feature/svc/predict"
PATH_HTTP_CHIFFON=""


def process_http_recog(http_ip,http_port,http_path,dict_query):

    url_origin="http://{ip}:{port}{path}".format(ip=http_ip,port=http_port,path=http_path)
    url_query=url+"?"+urllib.urlencode(dict_query)
    result=urllib2.urlopen(url_query)
    return result


# 各画像毎に行う処理
def process_image(filepath_input,dict_settings):

    # 取得した画像を特徴抽出プログラムに渡して実行
    dir_img=os.path.dirname(filepath_input)
    filepath_output=dict_settings["filepath_ext"]
    subprocess.call(["ruby",PATH_RUBY_BATCH,dir_img,filepath_output])

    # 得た特徴をserver4recogにHTTPで渡す
    with open(filepath_output) as f:
        feature_extracted=f.open()

    json_data_re={"feature":feature_extracted,"id:":dir_img,"group":dict_settings["recipe"],"name":dict_settings["name_classifier"]}
    dict_query_re={"json-data":json.dumps(json_data_re)}
    result_recog=process_http(dict_settings["ip_recog"],dict_settings["port_recog"],PATH_HTTP_RECOG,dict_query_re) #jsonのハッシュ形式

    # 認識結果をCHIFFONにHTTPで渡す
    dict_query_ch={}
    process_http(dict_settings["ip_chiffon"],dict_settings["port_chiffon"],PATH_HTTP_CHIFFON,dict_query_ch)


class DirectoryManager():
    def __init__(self,path_dir_check):
        self.path_dir_check=path_dir_check
        self.sets_filepath=[]
        self.sets_filepath_before=[]

    def check_directory(self):
        sets_filepath_before=self.sets_filepath
        self.sets_filepath=set(os.listdir(self.path_dir_check))
        sets_newfilepath=self.sets_filepath.difference(sets_filepath_before)

        return list(sets_newfilepath)


if __name__=="__main__":

    # 引数:設定ファイルのパス
    parser_args=argparse.ArgumentParser("各モジュールの連携用スクリプト")
    parser_args.add_argument("file_settings",help="設定ファイルのパス")
    args_script=parser_args.parse_args()

    with open(args_script.file_settings) as f:
        dict_settings=yaml.load(f)


    '''
    dirman=DirectoryManager(dict_settings["dir_check"])
    while(True):
        list_newfilepath=dirman.check_directory()

        # ディレクトリから画像を取得
        for filepath in list_newfilepath:
            proc_file=multiprocessing.Process(target=process_image,args=(filepath,dict_settings))
            proc_file.start()

        time.sleep(INT_CHECK)
    '''
