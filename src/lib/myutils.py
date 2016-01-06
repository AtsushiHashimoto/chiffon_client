import ConfigParser
import urllib2
import xml.etree.ElementTree
import os
import sys
import time


def make_dict_conf(path_conf):
    dict_conf={}
    config=ConfigParser.ConfigParser()
    config.read(path_conf)
    for section in config.sections():
        dict_conf[section]={}
        for tuple_param in config.items(section):
            dict_conf[section][tuple_param[0]]=tuple_param[1]
    return dict_conf


def get_url_request(domain,port,list_path):
    path=os.path.join(*list_path)
    return "http://{domain}:{port}{path}".format(domain=domain,port=port,path=path)

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


def get_ext(filename):
    return os.path.splitext(filename)[-1].lower()

def makedirs_ex(path_dir):
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)
