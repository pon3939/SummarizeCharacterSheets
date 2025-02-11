# SummarizeCharacterSheets

SW2.5 のキャラクターシートをスプレッドシートに集計する StepFunctions

## AWS SSO

デプロイやローカルデバッグには SSO 認証が必要になる

初回のみ設定が必要

```bash
aws configure sso  # CLI profile nameを"default"にするとデフォルト設定になる
```

ログイン

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

初回のみ環境を初期化する

```bash
python -m venv .venv
```

仮想環境に入る(Visual Studio Code は自動で入ってくれたりする)

```bash
source venv/bin/activate
```

仮想環境終了

```bash
deactivate
```

## パッケージ管理

初回のみ pip-tools をインストールする

```bash
pip install pip-tools
```

パッケージインストール

```bash
pip-sync requirements_dev.txt
```

layers/requirements.in に必要なパッケージ名を追記する。開発時のみ必要なものは requirements-dev.in に追記。

その後、requirements.txt を生成する

```bash
pip-compile layers/requirements.in
pip-compile requirements_dev.in
pip-sync requirements_dev.txt # エディターの補完等のためにインストール
```
