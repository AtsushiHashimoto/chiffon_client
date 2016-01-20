# -*- coding:utf-8 -*-
import myutils

import os
import json



# 取得した画像を特徴抽出プログラムに渡して実行

def make_results_FE(list_path_images,dict_conf):
    result_feature=[]
    for filepath_img in list_path_images:
        if(dict_conf["product_env"]["is_product"]=="1"):
            list_opt=[myutils.convert_to_cygpath(filepath_img)]+dict_conf["image_feature_extractor"]["default_options"].split()
            result_feature.append(myutils.callproc_cyg(dict_conf["image_feature_extractor"]["path_exec"],list_opt))
        else:
            list_opt=[filepath_img]+dict_conf["image_feature_extractor"]["default_options"].split()
            result_feature.append(" ".join([dict_conf["image_feature_extractor"]["path_exec"]]+list_opt))
    return result_feature


def featureExtraction(filepath_img,dict_conf):
    abspath_dir_image=os.path.abspath(os.path.dirname(filepath_img))
    list_path_images=myutils.get_files_from_exts(abspath_dir_image,dict_conf["table_object_manager"]["fileexts"])
    result_feature=make_results_FE(list_path_images,dict_conf)
    print("Feature extraction has been completed.")
    return result_feature



# 得た特徴をserver4recogにHTTPで渡す
def make_dict_query_s4r(filepath_img,feature_extracted,dict_conf):
    dir_img=os.path.dirname(filepath_img)
    list_group=[dict_conf["user_id"],dict_conf["recipe_id"],dict_conf["session_id"],dict_conf["image_feature_extractor"]["default_group"]]+dict_conf["grouptag"]
    dict_json_data={"feature":feature_extracted,"id:":dir_img,"group":list_group,"name":dict_conf["recipe_id"]}
    dict_query={"json_data":json.dumps(dict_json_data)}
    return dict_query
    

def make_url_server4recog(filepath_img,feature_extracted,dict_conf):
    dict_query=make_dict_query_s4r(filepath_img,feature_extracted,dict_conf)
    url_recog=myutils.get_url_request(dict_conf["serv4recog"]["host"],dict_conf["serv4recog"]["port"],[dict_conf["serv4recog"]["path"]],dict_query)
    return url_recog


def sendToServer4recog(filepath_img,dict_conf,result_feature):
    if(dict_conf["product_env"]["is_product"]=="1"):
        with open(filepath_output) as f:
            feature_extracted=f.open()
    else:
        feature_extracted="".join(result_feature)

    url_recog=make_url_server4recog(filepath_img,feature_extracted,dict_conf)
    print("URL(server4recog)..."+url_recog)

    if(dict_conf["product_env"]["is_product"]=="1"):
        result_recog=myutils.get_http_result(url_recog)
    else:
        result_recog=""
    print("Recognition by server4recog has been completed.")

    return result_recog



# 認識結果をCHIFFONにHTTPで渡す

def make_dict_query_ch(filepath_img,result_recog,dict_conf):
    dir_img=os.path.dirname(filepath_img)
    timestamp=myutils.get_time_stamp(dict_conf["chiffon_server"]["timestamp"])
    dict_string={"navigator":dict_conf["chiffon_server"]["navigator"],"action":{"target":result_recog,"name":dir_img,"timestamp":timestamp}}
    dict_query={"session_id":dict_conf["session_id"],"string":json.dumps(dict_string)}
    return dict_query

def make_url_chiffon(filepath_img,result_recog,dict_conf):
    dict_query=make_dict_query_ch(filepath_img,result_recog,dict_conf)
    url_chiffon=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_receiver"]],dict_query)
    return url_chiffon

def sendToChiffon(filepath_img,dict_conf,result_recog):
    url_chiffon=make_url_chiffon(filepath_img,result_recog,dict_conf)
    print("URL(chiffon)..."+url_chiffon)

    if(dict_conf["product_env"]["is_product"]=="1"):
        get_http_result(url_chiffon)
    print("Result from server4recog has been successfully sent to CHIFFON server.")
