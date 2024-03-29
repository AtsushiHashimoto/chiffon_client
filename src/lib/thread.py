# -*- coding:utf-8 -*-
import loop
import myutils

import multiprocessing
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


DIRNAME_LIST=["output_touch","output_release"]


def process_loop(filepath_img_masked,dict_conf):
    filepath_img=loop.getUnMaskedImage(filepath_img_masked,dict_conf)
    result_feature=loop.featureExtraction(filepath_img,dict_conf)
    result_recog=loop.sendToServer4recog(filepath_img,dict_conf,result_feature)
    loop.sendToChiffon(filepath_img,dict_conf,result_recog)


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
    for dirname in DIRNAME_LIST:
        observer_release.schedule(event_handler,dict_conf["table_object_manager"][dirname],recursive=True)
    observer_release.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer_release.stop()
    observer_release.join()
