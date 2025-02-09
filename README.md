# SummarizeCharacterSheets

SW2.5 のキャラクターシートをスプレッドシートに集計する StepFunctions

## デプロイ

初回のみ認証情報を設定する

```bash
aws configure
vi ~/.aws/credentials # aws_session_tokenを追記
```

デプロイする

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

requirements.in に必要なパッケージ名を追記する。開発時のみ必要なものは requirements-dev.in に追記。

その後、requirements.txt を生成する

```bash
pip-compile
pip-compile requirements_dev.in
pip-sync requirements_dev.txt # バージョンが更新されることがあるので適応
```
