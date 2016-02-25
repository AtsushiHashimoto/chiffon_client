# -*- coding:utf-8 -*-
import myutils

import os
import json
import re
import requests
import subprocess
import datetime
import locale

# 縮小済みの画像(256*256)を取得
# Put + 1 => bg の番号

# コマンドのヘルプ
# ExtractObjectBoxRegion.exe whole_input_image object_image output_image
# コマンド実行のサンプル
# ExtractObjectBoxRegion.exe ..\bg_0002837.png ..\putobject_0002836_027.png ..\output.png
def getUnMaskedImage(filepath_img_masked,dict_conf, mode):
    # %output_root%\%SESSION_ID%
    base_dir = os.path.join(dict_conf["chiffon_client"]["output_root"],dict_conf["session_id"])

    # マスク済みファイル名からフレーム数を抜き出し、背景差分の元情報となるファイル名を取得する。
    maskedimage_filename = os.path.basename(filepath_img_masked)
    pattern=re.compile("(_[0-9]+_)")
    frame_number_astext = pattern.search(maskedimage_filename).group(1)[1:-1]
    number_length = len(frame_number_astext)
    frame_number = str(int(frame_number_astext) + 1) # 背景画像は次の番号になる。

    bgimage_filename = "bg_" + frame_number.zfill(number_length) + myutils.get_ext(maskedimage_filename)
    bgimage_path=os.path.join(dict_conf["table_object_manager"]["output_rawimage"],bgimage_filename)

    # 縮小済み画像の出力先パス・ファイル名の作成
    # file_abspath_img = os.path.abspath(filepath_img_masked)
    # if(file_abspath_img.find(dict_conf["table_object_manager"]["output_touch"]) > -1):
    #    param = "output_touch"
    #elif(file_abspath_img.find(dict_conf["table_object_manager"]["output_release"]) > -1):
    #    param = "output_release"
    #else :
    #    raise OnError("Illegal Path:" + file_abspath_img)

    extractor_path=os.path.join(base_dir, dict_conf["object_region_box_extractor"][mode])
    imgpath_output=os.path.join(extractor_path, maskedimage_filename)

    # 実行
    list_imgpath=[bgimage_path, filepath_img_masked, imgpath_output]
    list_opt = list_imgpath + dict_conf["object_region_box_extractor"]["default_options"].split()
    retcode=myutils.callproc_cyg(dict_conf["object_region_box_extractor"]["path_exec"],list_opt)
    if(retcode == 0):
        return imgpath_output
    else :
        return ""

# 取得した画像を特徴抽出プログラムに渡して実行

def make_results_FE(filepath_img,dict_conf, mode):
    path_exec = dict_conf["image_feature_extractor"]["path_exec"]

    if(dict_conf["product_env"]["use_cygpath"]=="1"):
        filepath_img = myutils.convert_to_cygpath(filepath_img)
        path_exec = myutils.convert_to_cygpath(path_exec)

    if(dict_conf["product_env"]["enable_image_feature_extractor"]=="1"):
        # 特徴量抽出プログラムの実行
        list_cmds = [path_exec, filepath_img] + dict_conf["image_feature_extractor"]["default_options"].split()

        p = subprocess.Popen(
            list_cmds,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        (stdoutdata, stderrdata) = p.communicate()

        # stdoutdata = subprocess.check_output(list_cmds)

        if(int(p.returncode) == 0):
            # 標準出力に出る特徴量
            result_feature = stdoutdata

            # 特徴量のフォルダに置換
            file_abspath_img = os.path.abspath(filepath_img)
            image_feature_extractor_path = file_abspath_img.replace(dict_conf["object_region_box_extractor"][mode], dict_conf["image_feature_extractor"][mode])

            # ファイルの拡張子を特徴量用のものに変換
            for ext in dict_conf["table_object_manager"]["fileexts"]:
                if(image_feature_extractor_path.rfind(ext) > -1):
                    image_feature_extractor_path = image_feature_extractor_path.replace(ext, dict_conf["image_feature_extractor"]["fileext"])
                    break

            # ファイルへ書き出し。
            myutils.output_to_file(image_feature_extractor_path, result_feature)

            return result_feature
    else:
        list_opt=[filepath_img]+dict_conf["image_feature_extractor"]["default_options"].split()
        result_feature = " ".join([dict_conf["image_feature_extractor"]["path_exec"]]+list_opt)
        return result_feature


# 特徴量の抽出
# 特徴量を抽出する別実行ファイルの制約で、一時的にカレントディレクトリを移動する処理がある。
def featureExtraction(filepath_img,dict_conf, mode):
    cwd = os.getcwd()

    path_exec = dict_conf["image_feature_extractor"]["path_exec"]
    os.chdir(os.path.dirname(path_exec))

    result_feature=make_results_FE(filepath_img,dict_conf, mode)

    os.chdir(cwd)
    print("Feature extraction has been completed.")
    return result_feature



# 得た特徴をserver4recogにHTTPで渡す
def make_dict_query_s4r(filepath_img,feature_extracted,dict_conf):
    dir_img=os.path.basename(filepath_img)
    list_group=[dict_conf["user_id"],dict_conf["recipe_id"],dict_conf["session_id"],dict_conf["image_feature_extractor"]["default_group"]]+dict_conf["grouptag"]

    feature_list_as_string = feature_extracted.strip().rstrip(",").replace(" ", "").split(",") # リスト形式
    formatted_feature_extracted = [float(x) for x in feature_list_as_string] # 各値を float に変換

    dict_json_data={"feature":formatted_feature_extracted,"id:":dir_img,"group":list_group,"name":dict_conf["recipe_id"]}
    dict_query={"json_data":json.dumps(dict_json_data)}
    return dict_query


def make_url_server4recog(filepath_img,feature_extracted,dict_conf):
    dict_query=make_dict_query_s4r(filepath_img,feature_extracted,dict_conf)
    url_recog=myutils.get_url_request(dict_conf["serv4recog"]["host"],dict_conf["serv4recog"]["port"],[dict_conf["serv4recog"]["path"]],dict_query)
    return url_recog


def sendToServer4recog(filepath_img,dict_conf,result_feature, mode):
    #if(dict_conf["product_env"]["is_product"]=="1"):
    #    with open(filepath_output) as f:
    #        feature_extracted=f.open()
    #else:
    #    feature_extracted="".join(result_feature)

    # ディレクトリパスを置換
    file_abspath_img = os.path.abspath(filepath_img)
    output_path = file_abspath_img.replace(dict_conf["object_region_box_extractor"][mode], dict_conf["serv4recog"][mode])

    # ファイルの拡張子を特徴量用のものに変換
    for ext in dict_conf["table_object_manager"]["fileexts"]:
        if(output_path.rfind(ext) > -1):
            log_output_path = output_path.replace(ext, dict_conf["serv4recog"]["logfileext"])
            output_path = output_path.replace(ext, dict_conf["serv4recog"]["fileext"])
            break


    url_recog="http://{domain}:{port}{path}".format(domain=dict_conf["serv4recog"]["host"],port=dict_conf["serv4recog"]["port"],path=dict_conf["serv4recog"]["path"])
    dict_query=make_dict_query_s4r(filepath_img,result_feature,dict_conf)

    logtime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    print("URL(server4recog)..."+url_recog)
    # print(dict_query)
    myutils.output_to_file(log_output_path, "[%s] %s %s" % (logtime, url_recog, dict_query))

    if(dict_conf["product_env"]["enable_server4recog"]=="1"):
        response = requests.get(url_recog,params=dict_query)

        print(response.text)
        # ファイルへ書き出し。
        myutils.output_to_file(output_path, response.text)

        result_recog=json.loads(response.text)
        # result_recog=myutils.get_http_result(url_recog)
    else:
        result_recog={"tomato":"1"}
    print("Recognition by server4recog has been completed.")

    return result_recog



# 認識結果をCHIFFONにHTTPで渡す
def convert_recjson_to_idjson(recog_name,dict_conf):
    if recog_name in dict_conf["serv4recog"]["convtable"]:
        return dict_conf["serv4recog"]["convtable"][recog_name]
    else :
        return recog_name

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

def sendToChiffon(filepath_img,dict_conf,result_recog, mode):
    # dict_recog=convert_recjson_to_idjson(result_recog,dict_conf)
    # url_chiffon=make_url_chiffon(filepath_img,dict_recog,dict_conf)

    recog = result_recog["result"]["likelihood"]
    target = max(recog.items(), key=lambda x:x[1])[0]
    target = convert_recjson_to_idjson(target,dict_conf)

    dir_img=mode.replace("output_", "")
    timestamp=myutils.get_time_stamp(dict_conf["chiffon_server"]["timestamp"])
    dict_string={"navigator":dict_conf["chiffon_server"]["navigator"],"action":{"target":target,"name":dir_img,"timestamp":timestamp}}
    dict_query={"sessionid":dict_conf["session_id"],"string":json.dumps(dict_string)}

    url_chiffon=myutils.get_url_request(dict_conf["chiffon_server"]["host"],dict_conf["chiffon_server"]["port"],[dict_conf["chiffon_server"]["path_receiver"]],dict_query)
    print("URL(chiffon)..."+url_chiffon)

    # if(dict_conf["product_env"]["is_product"]=="1"):
    # myutils.get_http_result(url_chiffon)

    url = "http://{domain}:{port}{path}".format(domain=dict_conf["chiffon_server"]["host"],port=dict_conf["chiffon_server"]["port"],path=dict_conf["chiffon_server"]["path_receiver"])
    print("URL(chiffon)..."+url)
    response = requests.get(url,params=dict_query)

    print(response.text)

    print("Result from server4recog has been successfully sent to CHIFFON server.")
