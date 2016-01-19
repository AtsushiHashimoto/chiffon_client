# 仕様(仮)


## 概要

### 処理の流れ

1. 設定ファイル(`chiffon\_client.yaml`)の読み込み
2. `user\_id`を基にCHIFFONサーバから`session\_id`,`recipe\_id`を取得
3. 画像保存用ディレクトリを作成
4. TableObjectManagerを起動
5. 特定の画像保存用ディレクトリに保存された画像を随時チェック
6. 特徴抽出用プログラムに保存された画像を渡し、特徴量を保存する。
7. 6.で保存されたデータから特徴量をserver4recog(認識用プログラム)にHTTPで送信し、認識結果を得る。
8. 7.で得た認識結果をHTTPでCHIFFONに送信する。

### 関連ファイル

* chiffon\_client.py
* 一連の処理を行うPythonスクリプトファイル
* chiffon\_client.conf
* 各種設定を記述したconfファイル
* lib/
* chiffon_client.pyで用いるライブラリを置くディレクトリ

### 引数

スクリプトは以下の様に引数を指定して起動する。

```
python chiffon\_cient.py user\_id grouptag \[grouptag ...\]
```

指定する引数は以下の通り。

* user\_id
* ユーザー名
* grouptag
* server4recogへ渡すサンプルに付加するグループタグ
* 複数指定可能
* 但し最低1つは必要


### 設定ファイルの記述

```
[chiffon\_client]
\# chiffon\_clientが利用する全保存先ディレクトリのroot
output\_root=/Users/kitchen/pytest/src/data
[table\_object\_manager]
\# TableObjectManagerの絶対パス
path\_exec=/Users/kitchen/pytest/src/TableObjectManager.exe
default\_options=-d 0 --gpu_device 0 -v false
\# TableObjectManagerによる出力のディレクトリ
output\_touch=table\_object\_manager/PUT
output\_release=table\_object\_manager/TAKEN
[image\_feature\_extractor]
\# TableObjectManagerの絶対パス
path\_exec=/Users/kitchen/pytest/src/ImageFeatureExtractor.exe
\# 特徴抽出プログラムによる出力ディレクトリ
output\_touch=image\_feature\_extractor/touch
output\_release=image\_feature\_extractor/release
\# 抽出する特徴量の種類の名前
feature\_name=ilsvrc13
default\_group=image\_feature\_extractor\_v1
[serv4recog]
host=10.236.170.190
port=8080
[chiffon\_server]
domain=chiffon.mm.media.kyoto-u.ac.jp
path\_sessionid=/woz/session\_id/
path\_recipe=/woz/recipe/
port=80
path=/release
navigator=object\_access
```


## CHIFFONからの情報の取得

スクリプト起動時にCHIFFONから引数で指定した`user\_id`を基に`session\_id`,`recipe\_id`を取得する。

* `session\_id`
* 書式:`{user\_id}-{datetime}`
* `user\_id`:ユーザー名
* 引数で指定する
* `datetime`:ログイン日時
* 書式:`yyyy.MM.dd_HH.MM.ss.ffffff`
* 例:`guest-2015.12.08_14.33.56.381162`
* `http://{chiffon\_server["host"]}:{chiffon\_server["port"]}/woz/session_id/{user\_id}`から取得可能
* 上の方ほど日付が新しい
* 一番上に書かれているものを`session\_id`として用いる
* `recipe\_id`
* 各レシピに割り当てられるID
* 例:`FriedRice\_with\_StarchySauce`
* `http://{chiffon\_server["host"]}:{chiffon\_server["port"]}/woz/recipe/{session\_id}`から取得可能
* HTTP GETにより取得されるレシピはXMLで記述されている
* `recipe\_id`はrecipe要素のidとして指定されている



## TableObjectManager起動

TableObjectManagerは外部のプログラムをスクリプト内部で呼び出すことで実行する。実行ファイルのパスの指定場所は設定ファイルで指定する。後述の特徴量抽出プログラムも同様。

引数として画像を保存するディレクトリを指定する必要があるが、これはスクリプト内で設定ファイル内のディレクトリ名を絶対パスに変換して指定する。その他の引数は設定ファイルで指定する。


## 特徴量抽出

プログラムの引数として`{input\_file}`,`{output\_file}`を渡す必要がある。`{input\_file}`には保存された画像のパス、`{output\_file}`には特徴量を保存するファイルのパスを指定する。`input\_file`には追加された画像ファイルのパス,`output\_file`は設定ファイルで指定されたディレクトリのパスをそれぞれ用いる。



## server4recog

### 送信するURLおよびクエリ

```
http://localhost:8080/ml/my_db/my_feature/svc/predict?json_data={${SAMPLE}, ${CLASSIFIER-PARAMS}}
```

`{SAMPLE}`は以下のパラメータを持つ。

* feature
* サンプルの特徴量。
* 前の特徴量抽出プログラムにより出力されたファイルの中身が入る。
* id
* 入力するサンプルのID。
* 画像ファイルのbasenameを使う。
* group
* グループタグの名前
* 起動時の引数で指定した`group\_id`を配列の形で代入する。

`{CLASSIFIER-PARAMS}`は以下のパラメータを持つ。

* name
* 分類器の名前
* `recipe\_id`(レシピ名)を入れる。



## CHIFFON

### 送信するURLおよびクエリ

```
http://chiffon.mm.media.kyoto-u.ac.jp/receiver?sessionid={sessionid}&string={string}
```

* sessionid
* 起動時引数で指定した`session\_id`と同一。
* string
* 書式:`{"navigator":"object_acceess","action":{"target":{target},"name":{name},"timestamp":{timestamp}}}`
* `target`:操作対象
* server4recogから返ってきたjsonのハッシュから決まる
* `name`:操作の内容
* `touch`(物を掴む動作)あるいは`release`(物を手放す動作)
* 画像の保存されるディレクトリ名から決まる
* `timestamp`:クエリ送信日時
* 書式:`yyyy.MM.dd_HH.MM.ss.ffffff`
* 例:`{"navigator":"object_access","action":{"target":"knife_utensil","name":"release","timestamp":"2015.12.08_15.06.27.710000"}}`
