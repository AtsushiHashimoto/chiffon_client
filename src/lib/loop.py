# -*- coding:utf-8 -*-
import myutils
import time
import multiprocessing
import os
import json
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def process_loop(filepath_img,dict_conf):
    # 取得した画像を特徴抽出プログラムに渡して実行
    dir_img=os.path.dirname(filepath_img)
    if os.path.abspath(os.path.dirname(filepath_img))==dict_conf["table_object_manager"]["output_touch"]:
        path_dir_feature=dict_conf["image_feature_extractor"]["output_touch"]
    elif os.path.abspath(os.path.dirname(filepath_img))==dict_conf["table_object_manager"]["output_release"]:
        path_dir_feature=dict_conf["image_feature_extractor"]["output_release"]
    # 出力ファイル名が不明
    filepath_output=os.path.join(path_dir_feature,dict_conf["image_feature_extractor"]["feature_name"])
    list_opt=[]
    myutils.callproc_cyg(dict_conf["image_feature_extractor"]["path_exec"],list_opt)

    # 得た特徴をserver4recogにHTTPで渡す
    # with open(filepath_output) as f:
    #    feature_extracted=f.open()
    feature_extracted=""
    list_group=[dict_conf["user_id"],dict_conf["recipe_id"],dict_conf["session_id"],dict_conf["image_feature_extractor"]["default_group"]]+dict_conf["grouptag"]
    json_data_re={"feature":feature_extracted,"id:":dir_img,"group":list_group,"name":dict_conf["recipe_id"]}
    dict_query_re={"json_data":json.dumps(json_data_re)}
    url_recog=myutils.get_url_request(dict_conf["serv4recog"]["host"],dict_conf["serv4recog"]["port"],[dict_conf["serv4recog"]["path"]],dict_query_re)
    print(url_recog)
    # result_recog=get_http_result(url_recog)

    # 認識結果をCHIFFONにHTTPで渡す
    dict_query_ch={}
    url_chiffon=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_receiver"]],dict_query_ch)
    print(url_chiffon)
    # get_http_result(url_chiffon)
    

class ChangeHandler(FileSystemEventHandler):
    def __init__(self,dict_conf):
        self.dict_conf=dict_conf
    
    def on_created(self, event):
        if event.is_directory:
            return
        if myutils.get_ext(event.src_path) in ('.jpg','png','.txt'):
            print("New File '{filepath}' was detected.".format(filepath=event.src_path))
            proc_loop=multiprocessing.Process(target=process_loop,args=(event.src_path,self.dict_conf))
            proc_loop.start()


def makeNewThreads(dict_conf):
    event_handler=ChangeHandler(dict_conf)
    observer_release=Observer()
    for dirname in ["output_touch","output_release"]:
        observer_release.schedule(event_handler,dict_conf["table_object_manager"][dirname],recursive=True)
    observer_release.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer_release.stop()
    observer_release.join()

