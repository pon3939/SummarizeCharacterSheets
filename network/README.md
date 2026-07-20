# network

IPアドレスを固定するための設定

## デプロイ

削除するとIPアドレスが変わるため、削除しないこと

```bash
sam build
sam deploy
aws cloudformation update-termination-protection --stack-name summarize-character-sheets-network --enable-termination-protection # 誤削除防止
```
