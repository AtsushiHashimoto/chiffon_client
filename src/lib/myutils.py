import ConfigParser
import urllib2
import xml.etree.ElementTree
import os
import sys

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def make_dict_conf(path_conf):
    dict_conf={}
    config=ConfigParser.ConfigParser()
    config.read(path_conf)
    for section in config.sections():
        dict_conf[section]={}
        for tuple_param in config.items(section):
            dict_conf[section][tuple_param[0]]=tuple_param[1]
    return dict_conf


def get_http_result(url):
    result=urllib2.urlopen(url)
    return result

def get_session_id(url):
    result=get_http_result(url)
    return result.readline().rstrip("\n")

def get_recipe_id(url):
    result=get_http_result(url)
    elem_root=xml.etree.ElementTree.fromstring(result.read())
    return elem_root.attrib["id"]


def makedirs_ex(path_dir):
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)


class ChangeHandler(FileSystemEventHandler):
    
    def on_created(self, event):
        if event.is_directory:
            return
        if getext(event.src_path) in ('.jpg','.png','.txt'):
            print('%s has been created.' % event.src_path)

