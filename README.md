# 仕様(仮)

## 概要

### 処理の流れ

1. 設定ファイル(`chiffon_client.conf`)の読み込み
2. `user_id`を基にCHIFFONサーバから`session_id`,`recipe_id`を取得
3. 画像保存用ディレクトリを作成
4. TableObjectManagerを起動
5. 特定の画像保存用ディレクトリに保存された画像を随時チェック
6. 特徴抽出用プログラムに保存された画像を渡し、特徴量を保存
7. 6.で得た特徴量をserver4recog(認識用プログラム)にHTTPで送信し認識結果を取得
8. 7.で得た認識結果をHTTPでCHIFFONに送信する


### 関連ファイル

* chiffon_client.py
   * 一連の処理を行うPythonスクリプトファイル
* chiffon_client.conf
   * 各種設定を記述したconfファイル
* lib/
   * chiffon_client.pyで用いるライブラリを置くディレクトリ


### 引数

スクリプトは以下の様に引数を指定して起動する。

```
python chiffon_cient.py user_id grouptag [grouptag ...]
```

指定する引数は以下の通り。

* user_id
   * ユーザー名
* grouptag
   * server4recogへ渡すサンプルに付加するグループタグ
   * 複数指定可能
     * 但し最低1つは必要


### 設定ファイルの記述

```
[chiffon_client]
# chiffon_clientが利用する全保存先ディレクトリのroot
output_root=/Users/kitchen/pytest/src/data

[table_object_manager]
# TableObjectManagerの絶対パス
path_exec=/Users/kitchen/pytest/src/TableObjectManager.exe
# TableObjectManager実行時に渡すオプション引数
default_options=-d 0 --gpu_device 0 -v false
# TableObjectManagerによる出力のディレクトリ
output_touch=table_object_manager/PUT
output_release=table_object_manager/TAKEN
# 画像拡張子一覧
fileexts=.jpg,.png,.gif,.bmp,.tif

[image_feature_extractor]
# TableObjectManagerの絶対パス
path_exec=/Users/kitchen/pytest/src/ImageFeatureExtractor.exe
default_options=-s 256:256 -p /Users/kitchen/sample_data/imagenet_val.prototxt -m /Users/kitchen/sample_data/bvlc_reference_rcnn_ilsvrc13.caffemodel
# 特徴抽出プログラムによる出力ディレクトリ
output_touch=image_feature_extractor/touch
output_release=image_feature_extractor/release
# 抽出する特徴量の種類の名前
feature_name=ilsvrc13
default_group=image_feature_extractor_v1

[serv4recog]
host=10.236.170.190
port=8080
path=/ml/my_db/my_feature/svc/predict

[chiffon_server]
host=chiffon.mm.media.kyoto-u.ac.jp
path_sessionid=/woz/session_id/
path_recipe=/woz/recipe/
path_receiver=/receiver
port=80
navigator=object_access
# TimeStampの書式
timestamp=yyyy.MM.dd_HH.MM.ss.ffffff

[product_env]
# 本番環境なら1を指定
is_product=0
```



## CHIFFONからの情報の取得

スクリプト起動時にCHIFFONから引数で指定した`user_id`を基に`session_id`,`recipe_id`を取得する。

* `session_id`
   * 書式:`{user_id}-{datetime}`
     * `user_id`:ユーザー名
        * 引数で指定する
     * `datetime`:ログイン日時
        * 書式:`yyyy.MM.dd_HH.MM.ss.ffffff`
           * 例:`guest-2015.12.08_14.33.56.381162`
   * `http://{chiffon_server["host"]}:{chiffon_server["port"]}/woz/session_id/{user_id}`から取得可能
     * 上の方ほど日付が新しい
     * 一番上に書かれているものを`session_id`として用いる
* `recipe_id`
   * 各レシピに割り当てられるID
     * 例:`FriedRice_with_StarchySauce`
   * `http://{chiffon_server["host"]}:{chiffon_server["port"]}/woz/recipe/{session_id}`から取得可能
     * HTTP GETにより取得されるレシピはXMLで記述されている
     * `recipe_id`はrecipe要素のidとして指定されている



## TableObjectManager起動

TableObjectManagerはスクリプト内部で呼び出して実行する。実行ファイルのパスの指定場所は設定ファイルで指定する。後述の特徴量抽出プログラムも同様。

引数として画像を保存するディレクトリを指定する必要があるが、これはスクリプト内で設定ファイル内のディレクトリ名を絶対パスに変換して指定する。その他の引数は設定ファイルで指定する。



## 特徴量抽出

プログラムの引数として`{input_file}`,`{output_file}`を渡す必要がある。`{input_file}`には新しく保存された画像のパス、`{output_file}`には特徴量を保存するファイルのパス(設定ファイルに記述)を指定する。



## server4recog

### 送信するURLおよびクエリ

```
http://localhost:8080/ml/my_db/my_feature/svc/predict?json_data={${SAMPLE}, ${CLASSIFIER-PARAMS}}
```

`{SAMPLE}`は以下のパラメータを持つ。

* feature
   * サンプルの特徴量
   * 前の特徴量抽出プログラムにより出力されたファイルの中身が入る
* id
   * 入力するサンプルのID
   * 画像ファイルのbasenameを使う
* group
   * グループタグの名前
   * 起動時の引数で指定した`group_id`の他に`user_id`,`recipe_id`,`session_id`および設定ファイルで指定した`default_group`を配列の形で代入する

`{CLASSIFIER-PARAMS}`は以下のパラメータを持つ。

* name
   * 分類器の名前
   * `recipe_id`(レシピ名)を入れる



## CHIFFON

### 送信するURLおよびクエリ

```
http://chiffon.mm.media.kyoto-u.ac.jp/receiver?sessionid={sessionid}&string={string}
```

* sessionid
   * 起動時引数で指定した`session_id`と同一。
* string
   * 書式:`{"navigator":{navigator},"action":{"target":{target},"name":{name},"timestamp":{timestamp}}}`
   * `navigator`:
     * 設定ファイルで指定したものを用いる
   * `target`:操作対象
     * server4recogから返ってきたjsonのハッシュを代入する
   * `name`:操作の内容
     * `touch`(物を掴む動作)あるいは`release`(物を手放す動作)
     * 画像が保存されたディレクトリの名前が入る
   * `timestamp`:クエリ送信日時
     * 設定ファイルで指定したものを用いる
       * 例:`{"navigator":"object_access","action":{"target":"knife_utensil","name":"release","timestamp":"2015.12.08_15.06.27.710000"}}`
