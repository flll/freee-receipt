# レシート管理システム

## 概要
freeeとClaudeを使用してレシートを自動で処理・アップロードするシステムです。

## セットアップ手順

### 1. 初期設定
1. `images`フォルダにレシートを配置
2. `config.ini`の設定
   - freeeのアクセストークン設定（90日毎に再発行が必要）
   - アプリケーション設定例:
     - アプリURL: https://app.secure.freee.co.jp/developers/applications/37072
     - 認証URL: `https://accounts.secure.freee.co.jp/public_api/authorize?client_id=586969164444930&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code`
     - 注意: `&prompt=select_company`は削除してください
     - 認証コードの有効期限は10分です
     - リフレッシュトークンは90日で失効するので、90日ごとに再発行すること

### 2. レシート処理
1. `python main.py`を実行してレシートをClaudeに送信
2. [batches進捗確認](https://console.anthropic.com/settings/workspaces/default/batches)（処理に24時間程度必要）

### 3. freeeアップロード
1. `python get_freee_token.py`を実行（トークン発行）
2. `python freee-receipt-upload.py`を実行（レシートアップロード）

## 注意事項
- 久しぶりに使用する場合は`freee_tokens.json`を削除し、アプリ認証コードを再発行
- JPG形式のみ対応
- Anthropic Batchesおよびキャッシュ機能はベータ版のため、仕様変更の可能性あり
- `view.py`でバッチ処理結果の確認が可能

[![](https://mermaid.ink/img/pako:eNpVks9u00AQxl_F2nNLJcQpB6S0TlIHIVWCE3YPi72JjWI7MrYQSiJ1dwVNqFoi_rQqHKAhAtJSOLQIEaA8zGCXvAXr9TaiPqw8s79vdubTdJAdOgSVUKMVPrBdHMXabd0KNPGVTc_HTbIE_CWwCfAj4BtAP9fXajJzAGwskunT3fRsb11bXLyuLXeAvwD2BdiPHGdfc4RNz0fTv4fbvaLqck520_EHoNtA94HuANtK356mw35XWzGBH8516eb78-Hj9f91MzrJjt_Nia6mC8UQOAdODR3Ys0utDcULR-l4kL0-VVVWZJ9qQF0GFfMujm2XOJfnFO2f5NPwn0pakXTVLAexG4Vtz9bKa4bgZhv0z-8DBVUlVDOvXsv22Wz3eXr2KJu8UZfFWZPIqlmNCCHARsov9h14X7yWh_xEuVooVqXCuOhzCegWsIGhX7nXbmZPfqWbUwUaEqyr0vkII2nNHvDjvDQfKLAuwRvCu0_AvsmrPtCPwF9J5xQs7FTDoQXkk8jHniM2pZPXsFDsEp9YqCR-HdLASSu2kBX0BIqTOLz1MLBRKY4SsoCiMGm6qNTArfsiStoOjonu4WaE_Xm2jYM7YehfSAqo4nhxGM0ZIsObxb7Kte39A4WIRDU?type=png)](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNpVks9u00AQxl_F2nNLJcQpB6S0TlIHIVWCE3YPi72JjWI7MrYQSiJ1dwVNqFoi_rQqHKAhAtJSOLQIEaA8zGCXvAXr9TaiPqw8s79vdubTdJAdOgSVUKMVPrBdHMXabd0KNPGVTc_HTbIE_CWwCfAj4BtAP9fXajJzAGwskunT3fRsb11bXLyuLXeAvwD2BdiPHGdfc4RNz0fTv4fbvaLqck520_EHoNtA94HuANtK356mw35XWzGBH8516eb78-Hj9f91MzrJjt_Nia6mC8UQOAdODR3Ys0utDcULR-l4kL0-VVVWZJ9qQF0GFfMujm2XOJfnFO2f5NPwn0pakXTVLAexG4Vtz9bKa4bgZhv0z-8DBVUlVDOvXsv22Wz3eXr2KJu8UZfFWZPIqlmNCCHARsov9h14X7yWh_xEuVooVqXCuOhzCegWsIGhX7nXbmZPfqWbUwUaEqyr0vkII2nNHvDjvDQfKLAuwRvCu0_AvsmrPtCPwF9J5xQs7FTDoQXkk8jHniM2pZPXsFDsEp9YqCR-HdLASSu2kBX0BIqTOLz1MLBRKY4SsoCiMGm6qNTArfsiStoOjonu4WaE_Xm2jYM7YehfSAqo4nhxGM0ZIsObxb7Kte39A4WIRDU)