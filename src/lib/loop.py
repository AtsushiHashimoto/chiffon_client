# -*- coding:utf-8 -*-
import myutils
import time
import multiprocessing
import os
import json
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer



# 取得した画像を特徴抽出プログラムに渡して実行
def feature_extract(filepath_img,dict_conf):
    path_dir_image=os.path.abspath(os.path.dirname(filepath_img))
    files_dir_image=myutils.get_files_from_exts(path_dir_image,dict_conf["table_object_manager"]["fileexts"])

    result_feature=[]
    for filepath_img in files_dir_image:
        if(dict_conf["product_env"]["is_product"]=="1"):
            list_opt=[myutils.convert_to_cygpath(filepath_img)]+dict_conf["image_feature_extractor"]["default_options"].split()
            result_feature.append(myutils.callproc_cyg(dict_conf["image_feature_extractor"]["path_exec"],list_opt))
        else:
            list_opt=[filepath_img]+dict_conf["image_feature_extractor"]["default_options"].split()
            result_feature.append(" ".join([dict_conf["image_feature_extractor"]["path_exec"]]+list_opt))

    return result_feature


# 得た特徴をserver4recogにHTTPで渡す
def send_to_server4recog(filepath_img,dict_conf,result_feature):
    if(dict_conf["product_env"]["is_product"]=="1"):
        with open(filepath_output) as f:
            feature_extracted=f.open()
    else:
        feature_extracted="".join(result_feature)

    dir_img=os.path.dirname(filepath_img)
    list_group=[dict_conf["user_id"],dict_conf["recipe_id"],dict_conf["session_id"],dict_conf["image_feature_extractor"]["default_group"]]+dict_conf["grouptag"]
    json_data_re={"feature":feature_extracted,"id:":dir_img,"group":list_group,"name":dict_conf["recipe_id"]}
    dict_query_re={"json_data":json.dumps(json_data_re)}
    url_recog=myutils.get_url_request(dict_conf["serv4recog"]["host"],dict_conf["serv4recog"]["port"],[dict_conf["serv4recog"]["path"]],dict_query_re)
    print(url_recog)

    if(dict_conf["product_env"]["is_product"]=="1"):
        result_recog=get_http_result(url_recog)
    else:
        result_recog=""
    return result_recog


# 認識結果をCHIFFONにHTTPで渡す
def send_to_chiffon(filepath_img,dict_conf,result_recog):
    dir_img=os.path.dirname(filepath_img)
    str_timefmt=dict_conf["chiffon_server"]["timestamp"]
    timestamp=myutils.get_time_stamp(str_timefmt)
    dict_string={"navigator":dict_conf["chiffon_server"]["navigator"],"action":{"target":result_recog,"name":dir_img,"timestamp":timestamp}}
    dict_query_ch={"session_id":dict_conf["session_id"],"string":json.dumps(dict_string)}
    url_chiffon=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_receiver"]],dict_query_ch)
    print(url_chiffon)

    if(dict_conf["product_env"]["is_product"]=="1"):
        get_http_result(url_chiffon)



def process_loop(filepath_img,dict_conf):
    result_feature=feature_extract(filepath_img,dict_conf)
    result_recog=send_to_server4recog(filepath_img,dict_conf,result_feature)
    send_to_chiffon(filepath_img,dict_conf,result_feature)



class ChangeHandler(FileSystemEventHandler):
    def __init__(self,dict_conf):
        self.dict_conf=dict_conf
    
    def on_created(self, event):
        if event.is_directory:
            return
        if myutils.get_ext(event.src_path) in self.dict_conf["table_object_manager"]["fileexts"]:
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

