# -*- coding:utf-8 -*-
import myutils
import time
import multiprocessing
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def process_loop(filepath_img,dict_conf):
    
    count=0
    while True:
        count+=1
        print("{0}:{1}".format(count,filepath_img))
        time.sleep(1)




class ChangeHandler(FileSystemEventHandler):

    def __init__(self,dict_conf):
        self.dict_conf=dict_conf
    
    def on_created(self, event):
        if event.is_directory:
            return
        if myutils.get_ext(event.src_path) in ('.jpg','png','.txt'):
            proc_loop=multiprocessing.Process(target=process_loop,args=(event.src_path,self.dict_conf))
            proc_loop.start()


def makeNewThreads(path_dir,dict_conf):
    event_handler=ChangeHandler(dict_conf)
    observer_release=Observer()
    observer_release.schedule(event_handler,path_dir,recursive=True)
    observer_release.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer_release.stop()
    observer_release.join()



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

