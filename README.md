# SummarizeCharacterSheets

SW2.5 のキャラクターシートをスプレッドシートに集計する StepFunctions

## 初期設定

### 本番環境

s3 に`summarize-character-sheets-bucket`バケットを作成する。

### ローカル環境

AWS SAM がセットアップ済みであること

```bash
# Python仮想環境
python -m venv .venv
source venv/bin/activate
# パッケージ管理ツールインストール
pip install pip-tools
# エディターの補完等のためにライブラリインストール
pip-sync requirements_dev.txt
# SSO設定
# CLI profile nameを"default"にするとデフォルト設定になる
aws configure sso
```

## AWS SSO

デプロイやローカルデバッグには SSO 認証が必要になる

```bash
aws sso login
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
source venv/bin/activate
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
開発時のみ必要なものは requirements-dev.in に追記。
その後、requirements.txt を生成する。

```bash
pip-compile layers/requirements.in
pip-compile requirements_dev.in
pip-sync requirements_dev.txt
```
