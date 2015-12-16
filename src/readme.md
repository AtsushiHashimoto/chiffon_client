# 仕様(仮)


## 概要

### 処理の流れ

1. 特定の画像保存用ディレクトリに保存された画像を随時チェックし、もしファイルが追加されていれば特徴量抽出プログラムにそのファイルを引数の1つとして渡して実行し、特徴量のデータを保存する。
2. 1.で保存されたデータから特徴量をserver4recog(認識用プログラム)にHTTPで送信し、認識結果を得る。
3. 2.で得た認識結果をHTTPでCHIFFONに送信する。

### 関連ファイル

* batch\_navi\_client.py
    * 一連の処理を行うスクリプト(python)
* config.yaml
    * 各種設定を記述したyamlファイル

### 引数

スクリプトは以下の様に引数を指定して起動する。

```
python batch\_navi\_client.py \[usrername\] \[grouptag ...\]
```

指定する引数は以下の通り。

* username
    * ユーザー名
* groupname
    * server4recogへ渡すサンプルに付加するグループタグ
    * 複数指定可能
	    * 但し最低1つは必要


### 設定ファイルの記述

```
\# 抽出した特徴量の保存先
filepath\_ext: /path/to/feature
\# 画像の保存ディレクトリ
dir\_check: /path/to/TOUCH
\# 特徴量抽出プログラムのパス
exe\_featurek: /path/to/exe
\# 各接続先(server4recog,CHIFFON)のIPアドレス,ポート番号
ip\_recog: 10.236.170.190
port\_recog: 8080
ip\_chiffon: 133.3.251.221
port\_chiffon: 8080
```



## CHIFFONからの情報の取得

###取得する情報

スクリプト起動時にCHIFFONから引数で指定した`username`を基に`session\_id`,`recipe\_id`を取得する。

* `session\_id`
    * 書式:`{username}-{datetime}`
    * `username`:ユーザー名
    	* 設定ファイルで指定する
	* `datetime`:ログイン日時
		* 書式:`yyyy.MM.dd_HH.MM.ss.ffffff`
	* 例:`guest-2015.12.08_14.33.56.381162`
	* `http://chiffon.mm.media.kyoto-u.ac.jp/woz/session_id/{username}`から取得可能(後述)
* `recipe\_id`
    * 例:`FriedRice\_with\_StarchySauce`

### sessionidの取得

```
http://chiffon.mm.media.kyoto-u.ac.jp/woz/session_id/{username}
```

`username`には引数で指定したものを用いる。上の方ほど日付が新しく、一番上に書かれているものを`session\_id`として用いる。


### レシピ取得

```
http://chiffon.mm.media.kyoto-u.ac.jp/woz/recipe/{session_id}
```

上のURLによって取得出来るレシピはXMLで記述されている。`recipe\_id`はrecipe要素のidによって指定されているものを用いる。


## 特徴量抽出

特徴量抽出用プログラムは外部のプログラムをスクリプト内部で呼び出すことで実行する。

プログラムの引数として`{input_file}`,`{output_file}`を渡す必要がある。`{input_file}`には保存された画像のパス、`{output_file}`には特徴量を保存するファイルのパスを指定する。`input\_file`には追加された画像ファイルのパス,`output_file`は設定ファイルで指定されたディレクトリのパスをそれぞれ用いる。


## server4recog


### 送信するURLおよびクエリ

```
http://localhost:8080/ml/my_db/my_feature/svc/predict?json_data={${SAMPLE}, ${CLASSIFIER-PARAMS}}
```

`{SAMPLE}`は以下のパラメータを持つ。

* feature
    * サンプルの特徴量。
    * 前の特徴量抽出プログラムの出力を成形したものが入る。
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


