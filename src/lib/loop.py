# -*- coding:utf-8 -*-
import myutils
import time
import multiprocessing
import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def process_loop(filepath_img,dict_conf):
    # 取得した画像を特徴抽出プログラムに渡して実行
    dir_img=os.path.dirname(filepath_input)
    filepath_output=dict_settings["filepath_ext"]
    list_opt=[]
    myutils.callproc_cyg(dict_conf["image_feature_extractor"]["path_exec"],list_opt)

    # 得た特徴をserver4recogにHTTPで渡す
    with open(filepath_output) as f:
        feature_extracted=f.open()
    list_group=[dict_conf[],dict_conf["recipe_id"],dict_conf["image_feature_extractor"]["default_group"]]
    json_data_re={"feature":feature_extracted,"id:":dir_img,"group":list_group,"name":dict_conf["recipe_id"]]}
    dict_query_re={"json-data":json.dumps(json_data_re)}
    result_recog=myutils.get_url_request(dict_conf["serv4recog"]["host"],dict_conf["serv4recog"]["port"],[dict_conf["serv4recog"][""]],dict_query_re)
    # result_recog=process_http(dict_settings["ip_recog"],dict_settings["port_recog"],PATH_HTTP_RECOG,dict_query_re) #jsonのハッシュ形式

    # 認識結果をCHIFFONにHTTPで渡す
    dict_query_ch={}
    process_http(dict_settings["ip_chiffon"],dict_settings["port_chiffon"],PATH_HTTP_CHIFFON,dict_query_ch)
    

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

