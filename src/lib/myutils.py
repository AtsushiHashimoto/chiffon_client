import ConfigParser
import urllib2
import xml.etree.ElementTree
import os
import sys
import time
import subprocess
import datetime
import glob



def make_dict_conf(path_conf):
    dict_conf={}
    config=ConfigParser.ConfigParser()
    config.read(path_conf)
    for section in config.sections():
        dict_conf[section]={}
        for tuple_param in config.items(section):
            dict_conf[section][tuple_param[0]]=tuple_param[1]
    return dict_conf



def get_url_request(domain,port,list_path,dict_query=[]):
    path=os.path.join(*list_path)
    if len(dict_query)==0:
        query=""
    else:
        query="?"+"&".join(["{name}={value}".format(name=k,value=v) for k,v in dict_query.items()])
    return "http://{domain}:{port}{path}{query}".format(domain=domain,port=port,path=path,query=query)

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



def convert_to_cygpath(path):
    return subprocess.call(["cygpath","-w",path])

def callproc_cyg(path_exec,list_args):
    path_exec_cyg=convert_to_cygpath(path)
    list_cmd=[path_exec]+list_args
    return subprocess.call(list_cmd)



def get_files_from_exts(path_dir,list_exts):
    list_files=[]
    for ext in list_exts:
        list_file=glob.glob(path_dir+"/*{ext}".format(ext=ext))
        if not list_file is None:
            list_files.extend(list_file)
    return list_files
    


def get_time_stamp(str_fmt):
    time_now=datetime.datetime.now()
    return time_now.strftime(str_fmt)



def get_ext(filename):
    return os.path.splitext(filename)[-1].lower()



def makedirs_ex(path_dir):
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir)
        print("New directory '{path_dir}' was made.".format(path_dir=path_dir))
