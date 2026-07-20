# SummarizeCharacterSheets

SW2.5 のキャラクターシートをスプレッドシートに集計する

## 初期設定

AWS SAM がセットアップ済みであること  
参考

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/install-sam-cli.html)

```bash
# コミットメッセージのテンプレート設定
git config --local commit.template .gitmessage.txt
# SSO設定
# CLI profile nameを"default"にするとデフォルト設定になる
aws configure sso
```

## AWS SSO

デプロイやローカルデバッグには SSO 認証が必要になる

```bash
aws sso login
```

## キャラクターシート集計システム

source/README.md 参照

## ネットワーク設定

network/README.md 参照
