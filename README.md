# GoogleスプレッドシートからWebフォームへ自動入力するツール

このツールは、Googleスプレッドシートの行データを読み取り、Seleniumで開いたWebフォームへ自動入力するPythonツールです。

## 必要なPythonバージョン

Python 3.10 以上を推奨します。

インストール済みのPythonバージョンは、PowerShellで次のコマンドを実行して確認できます。

```powershell
python --version
```

もしPythonが入っていない場合は、Python公式サイトからインストールしてください。

https://www.python.org/downloads/

インストール時は `Add python.exe to PATH` にチェックを入れると、PowerShellから `python` コマンドを使いやすくなります。

## フォルダ構成

```text
Googleフォーム/
├─ main.py
├─ config.py
├─ sheets.py
├─ form_filler.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

実行前に、次の2つのファイルを追加します。

```text
Googleフォーム/
├─ .env
└─ credentials.json
```

## 仮想環境の作成方法

まず、このプロジェクトのフォルダへ移動します。

```powershell
cd "C:\Users\User\Documents\Googleフォーム"
```

仮想環境を作成します。

```powershell
python -m venv .venv
```

仮想環境を有効化します。

```powershell
.\.venv\Scripts\Activate.ps1
```

成功すると、PowerShellの行頭に `(.venv)` のような表示が出ます。

もし実行ポリシーのエラーが出る場合は、次のコマンドを実行してから、もう一度有効化してください。

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## requirements.txt の作成

このプロジェクトには、すでに `requirements.txt` を用意しています。

内容は次の通りです。

```text
gspread
google-auth
python-dotenv
selenium
```

必要なライブラリをインストールします。

```powershell
pip install -r requirements.txt
```

## .env の書き方

`.env.example` をコピーして、`.env` という名前のファイルを作成してください。

PowerShellでは次のコマンドでコピーできます。

```powershell
copy .env.example .env
```

`.env` を開き、自分の環境に合わせて値を書き換えます。

```env
GOOGLE_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_spreadsheet_id
WORKSHEET_NAME=シート1
FORM_URL=https://example.com/form

FIRST_DATA_ROW=2
MAX_ROWS=600
DONE_STATUS=完了
WAIT_SECONDS=10

NAME_SELECTOR=input[name="name"]
EMAIL_SELECTOR=input[name="email"]
PHONE_SELECTOR=input[name="phone"]
ADDRESS_SELECTOR=input[name="address"]
SUBMIT_SELECTOR=button[type="submit"]
```

各項目の意味は次の通りです。

- `GOOGLE_CREDENTIALS_FILE`: GoogleサービスアカウントJSONのファイル名です。
- `SPREADSHEET_ID`: GoogleスプレッドシートのIDです。
- `WORKSHEET_NAME`: 読み取るシート名です。
- `FORM_URL`: 自動入力したいWebフォームのURLです。
- `FIRST_DATA_ROW`: データを読み始める行番号です。1行目が見出しなら `2` にします。
- `MAX_ROWS`: 最大処理件数です。レベル1では `600` を想定しています。
- `DONE_STATUS`: 処理済みの行に書き込む文字です。
- `WAIT_SECONDS`: フォーム項目が表示されるまで待つ秒数です。
- `NAME_SELECTOR`: 名前欄のCSSセレクタです。
- `EMAIL_SELECTOR`: メールアドレス欄のCSSセレクタです。
- `PHONE_SELECTOR`: 電話番号欄のCSSセレクタです。
- `ADDRESS_SELECTOR`: 住所欄のCSSセレクタです。
- `SUBMIT_SELECTOR`: 登録ボタンのCSSセレクタです。

`SPREADSHEET_ID` は、スプレッドシートURLの次の部分です。

```text
https://docs.google.com/spreadsheets/d/【ここがSPREADSHEET_ID】/edit
```

CSSセレクタは、対象フォームのHTMLに合わせて変更してください。

## GoogleサービスアカウントJSONの置き方

Google Sheets APIを使うために、Google Cloudでサービスアカウントを作成し、JSONキーをダウンロードします。

大まかな流れは次の通りです。

1. Google Cloud Consoleを開きます。
2. プロジェクトを作成、または既存プロジェクトを選択します。
3. Google Sheets APIを有効化します。
4. サービスアカウントを作成します。
5. サービスアカウントのキーをJSON形式で作成し、ダウンロードします。
6. ダウンロードしたJSONファイルを、このプロジェクトフォルダに置きます。
7. ファイル名を `credentials.json` に変更します。

配置後は次のようになります。

```text
Googleフォーム/
├─ credentials.json
├─ main.py
├─ config.py
├─ sheets.py
└─ form_filler.py
```

`.env` の `GOOGLE_CREDENTIALS_FILE` も同じ名前にしてください。

```env
GOOGLE_CREDENTIALS_FILE=credentials.json
```

## スプレッドシート共有方法

サービスアカウントでスプレッドシートを読み書きできるように、スプレッドシートを共有します。

1. `credentials.json` を開きます。
2. `client_email` という項目を探します。
3. `xxxxx@xxxxx.iam.gserviceaccount.com` のようなメールアドレスをコピーします。
4. Googleスプレッドシートを開きます。
5. 右上の「共有」をクリックします。
6. コピーしたサービスアカウントのメールアドレスを追加します。
7. 権限を「編集者」にします。
8. 共有を完了します。

この共有を忘れると、Pythonからスプレッドシートを開けません。

## スプレッドシートの列

このツールでは、次の列を使います。

```text
A列: 名前
B列: メールアドレス
C列: 電話番号
D列: 住所
E列: ステータス
```

処理が成功した行には、E列に `完了` と書き込みます。

## 実行コマンド

仮想環境を有効化した状態で、次のコマンドを実行します。

```powershell
python main.py
```

実行するとChromeが起動します。

ログインが必要なフォームの場合は、Chrome上で手動ログインしてください。
準備ができたら、PowerShellに戻ってEnterキーを押すと自動入力が始まります。

## よくあるエラーと対処法

### `python` が認識されない

Pythonがインストールされていないか、PATHが通っていない可能性があります。

対処法:

- Pythonをインストールします。
- インストール時に `Add python.exe to PATH` にチェックを入れます。
- PowerShellを開き直してから再実行します。

### `.\.venv\Scripts\Activate.ps1 cannot be loaded`

PowerShellの実行ポリシーで、仮想環境の有効化が止められています。

対処法:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### `ModuleNotFoundError: No module named 'gspread'`

必要なライブラリがインストールされていません。

対処法:

```powershell
pip install -r requirements.txt
```

仮想環境を使っている場合は、先に有効化してください。

```powershell
.\.venv\Scripts\Activate.ps1
```

### `.env に XXX を設定してください。`

`.env` に必要な設定がありません。

対処法:

- `.env.example` をコピーして `.env` を作成します。
- エラーに表示された項目を `.env` に追加します。
- 値が空になっていないか確認します。

### `FileNotFoundError` や `No such file or directory: credentials.json`

GoogleサービスアカウントJSONが見つかっていません。

対処法:

- `credentials.json` をプロジェクトフォルダに置きます。
- `.env` の `GOOGLE_CREDENTIALS_FILE` とファイル名が一致しているか確認します。

### `SpreadsheetNotFound`

スプレッドシートIDが間違っているか、サービスアカウントに共有されていません。

対処法:

- `.env` の `SPREADSHEET_ID` が正しいか確認します。
- `credentials.json` の `client_email` をスプレッドシートに「編集者」として共有します。

### `WorksheetNotFound`

`.env` の `WORKSHEET_NAME` と、実際のシート名が一致していません。

対処法:

- スプレッドシート下部のタブ名を確認します。
- `.env` の `WORKSHEET_NAME` を同じ名前にします。

### Chromeが起動しない

Chromeがインストールされていない、またはSeleniumがChromeDriverを取得できない可能性があります。

対処法:

- Google Chromeをインストールします。
- Chromeを最新版に更新します。
- `selenium` を最新版に更新します。

```powershell
pip install -U selenium
```

### `TimeoutException`

指定したCSSセレクタのフォーム項目が見つからない、または表示されていません。

対処法:

- `.env` のCSSセレクタが正しいか確認します。
- 手動ログイン後、フォーム画面まで移動してからEnterを押します。
- 表示に時間がかかるフォームなら、`.env` の `WAIT_SECONDS` を大きくします。

例:

```env
WAIT_SECONDS=20
```

### 入力はできるが送信できない

登録ボタンのCSSセレクタが違っている可能性があります。

対処法:

- `.env` の `SUBMIT_SELECTOR` を確認します。
- ボタンが `button[type="submit"]` ではないフォームもあります。
- 開発者ツールで実際のボタン要素を確認してください。

## 注意点

このツールはレベル1の実装です。

- エラーが出た行では処理を止め、エラー内容を表示します。
- 完了済みの行は二重登録を避けるためスキップします。
- フォームの確認画面や複数ページ構成には、追加対応が必要になる場合があります。
- 実運用前に、必ず少ない件数でテストしてください。
