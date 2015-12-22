# -*- coding:utf-8 -*-
import os
import multiprocessing
import time
import urllib,urllib2
import sys
import argparse
import subprocess
import json
import ConfigParser
import xml.etree.ElementTree


'''

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
'''



if __name__=="__main__":

    PATH_BATCH_RUBY="batch_feature_extraction.rb"
    INT_CHECK=5
    PATH_HTTP_RECOG="/ml/my_db/my_feature/svc/predict"

    
    PATH_CONFIG_CLIENT="chiffon_client.conf"    
    dict_conf={}
    
    # 引数取得
    parser_args=argparse.ArgumentParser("CHIFFONに用いられる各モジュールの連携用スクリプト")
    parser_args.add_argument("user_id",help="CHIFFONのユーザー名")
    parser_args.add_argument("grouptag",nargs="+",help="サンプルに付加するグループタグ")
    args_client=parser_args.parse_args()
    dict_conf["user_id"]=args_client.user_id
    dict_conf["list_grouptags"]=args_client.grouptag

    # 設定ファイル読み込み
    config=ConfigParser.ConfigParser()
    config.read(PATH_CONFIG_CLIENT)
    for section in config.sections():
        dict_conf[section]={}
        for tuple_param in config.items(section):
            dict_conf[section][tuple_param[0]]=tuple_param[1]

    # CHIFFONからsession_id,recipe_idを取得
    # 
    # url_session_id="http://{ip}:{port}{path}".format(ip=dict_conf["chiffon_server"]["host"],port=dict_conf["chiffon_server"]["port"],path="/woz/session_id/{user_id}".format(user_id=dict_conf["user_id"]))
    url_session_id="http://chiffon.mm.media.kyoto-u.ac.jp/woz/session_id/guest"
    try:
        result_session_id=urllib2.urlopen(url_session_id)
    except:
        print("Error:{err_info}".format(err_info=sys.exec_info()[0]))
    session_id=result_session_id.readline().rstrip("\n")

    url_recipe_id="http://chiffon.mm.media.kyoto-u.ac.jp/woz/recipe/{session_id}".format(session_id=session_id)
    try:
        result_session_id=urllib2.urlopen(url_recipe_id)
    except:
        print("Error:{err_info}".format(err_info=sys.exec_info()[0]))
    elem_root=xml.etree.ElementTree.fromstring(result_session_id.read())
    recipe_id=elem_root.attrib["id"]

    

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
