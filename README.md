Demo0220
====

とある企業でのインターンシップ報告会にて使用したデモンストレーションのプログラムです。  
プログラムでなんかやってと言われたときにパッと出せるといいんじゃないでしょうか。  


<div align="center">
<img src=https://github.com/zashio/Demo0220/blob/master/multi-media.png "Google-Natural-Language=API">
</div>

## Description
[Cloud Speech-to-Text ドキュメント](https://cloud.google.com/speech-to-text/docs/?hl=ja)  
[Cloud Natural Language API ドキュメント](https://cloud.google.com/natural-language/docs/)

## Demo
よく見ると上部に実行したコマンドが映っています。  
![result](https://github.com/zashio/Demo0220/blob/master/streaming_recognize_demo.gif)


## Requirement
- Python3.6.6  
- Jupyterで実行する場合、Anaconda3

## Usage

### Google Cloud Platformを利用するために
[Google Cloud Platformの簡単スタートアップガイド](http://goo.gl/ua5fQw)の、サービス共通編(P9-P20)を終え、プロジェクトを作成してください。

### ソースコードのコピー
- コンソールを開き、任意の場所で以下を実行し、全てのファイルをダウンロードしてください。  
`git clone https://github.com/zacceydesuyo/Demo0220.git`  
- Demo0220フォルダ内に移動し、コンソール上で以下を実行し、必要なライブラリをインストールしてください。  
`pip install -r requirements.txt`   

### 認証について  
ソースコード中の、
`os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:***/***/***.json"`  
を、訂正する必要があります。  
[認証の概要](https://cloud.google.com/docs/authentication/getting-started)中の、「サービスアカウントを作成する」を実行し、認証用jsonファイルを入手してください。  
<div align="center">
<img src=https://github.com/zashio/Demo0220/blob/master/CreateServiceAccountKey.png "GetJson">
</div>
  
「作成」を押してダウンロードされたjsonファイルを、任意の場所に保存して  
`os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:***/***/***.json"`  
中の`***/***/***`にその場所へのパスを記載してください。  
これは、環境変数に書き込んでおくのがスマートではありますが、このようにソースコード中で指定することもできます。  
  
### .ipynbを使う場合
- 任意の環境(デモGifではJupyterLab)で"mic_recog.ipynb"を開き、  
`os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:***/***/***.json"`  
を訂正したのち、上から実行してください。  
  
### .pyを使う場合
- 任意のエディタで"mic_recog.py"を開き、以下を訂正してください。  
`os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "C:***/***/***.json"`  
- コマンドライン上で、以下を実行してください。
`python mic_recog.py`
- 言語コード（[詳細](https://cloud.google.com/speech-to-text/docs/languages)）を英語に変更したい場合  
`python mic_recog.py -lang=en-US`  
- 感情推定をONにしたい場合  
`python mic_recog.py -sentiment=True`

## Install
必要なライブラリは、'requirements.txt'に記述してあります。  
そのため、以下のコマンドをDemo0220フォルダ内で実行していただくことにより、必要なライブラリがすべてインストールされます。  
`pip install -r requirements.txt`  
Anaconda環境にてPythonのインストールを行った場合は、pipコマンドとcondaコマンドを併用してのインストールはおやめください。  

## Contribution  
お待ちしております。  
フォークして、新しいブランチを作ってそこに変更点をプッシュしておいてください。  
プルリクエストもお願いします。  

## Licence  
This source is licensed under the Apache License, Version2.0

## Author
zashio
