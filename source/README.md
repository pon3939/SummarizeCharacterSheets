# source

## 初期設定

### 本番環境

下記を作成

- s3 バケット
  - summarize-character-sheets-bucket
- AWS Backup ボールト
  - summarize_character_sheets_vault

下記を編集

- functions
  - initial_data/insert_dynamo_db.json : google_service_accounts
  - local_inputs/insert_dynamo_db.json : google_service_accounts
- local_env.json
  - GetYtsheetDataFunction.MY_SNS_TOPIC_ARN : SNS トピックの ARN、sam deploy 時に表示される
- template.yaml : MyEmailAddress

### ローカル環境

```bash
# Python仮想環境
python3 -m venv .venv
source .venv/bin/activate
# パッケージ管理ツールインストール
pip install pip-tools
# エディターの補完等のためにライブラリインストール
pip-sync requirements_dev.txt
```

## デプロイ

```bash
sam build
sam deploy
```

不要になったら削除する

```bash
sam delete
```

## 開発環境構築

仮想環境に入る(Visual Studio Code は自動で入ってくれたりする)

```bash
source .venv/bin/activate
```

仮想環境終了

```bash
deactivate
```

## パッケージ管理

パッケージインストール

```bash
pip-sync requirements_dev.txt
```

layers/requirements.in に必要なパッケージ名を追記する。
開発時のみ必要なものは requirements_dev.in に追記。
その後、requirements.txt を生成する。

```bash
pip-compile layers/requirements.in
pip-compile requirements_dev.in
pip-sync requirements_dev.txt
```

## その他

- SNSはメールから確認すると自動解除されることがある(原因不明)。管理画面から確認すること。
