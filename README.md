# 順序
## はじめに
1. imageフォルダにレシートを入れる
1. config.iniを設定
    - 90日ぶりに起動する場合、freeeのアクセストークンを再発行する
    - アプリ例: https://app.secure.freee.co.jp/developers/applications/37072
    - 認証コード例: `https://accounts.secure.freee.co.jp/public_api/authorize?client_id=586969164444930&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code`
    - `&prompt=select_company`は消すこと
    - 認証コードは10分で失効する。
1. `python main.py`を実行し、レシートをclaudeに送信
1. 24時間待つ[batches進捗詳細](https://console.anthropic.com/settings/workspaces/default/batches)

## 24時間たったら...
1. `python get_freee_token.py`を実行し、Freeeリフレッシュトークンとアクセストークンを発行
1. `python freee-receipt-upload.py`を実行し、claudeからのレスポンスを元に、freeeにレシートをアップロード


# メモ
- 久しぶりに使うときは`freee_tokens.json`を削除して、アプリの認証コードを再発行すること
- jpgのみ対応
- batcheの機能はbetaなので仕様が変わる可能性がある
- 同じくcacheの機能もbetaなので、仕様が変わる可能性がある
- view.pyは、batchの結果を表示します

## pipコマンド
```sh
pip install anthropic requests
```

[![](https://mermaid.ink/img/pako:eNpVks9u00AQxl_F2nNLJcQpB6S0TlIHIVWCE3YPi72JjWI7MrYQSiJ1dwVNqFoi_rQqHKAhAtJSOLQIEaA8zGCXvAXr9TaiPqw8s79vdubTdJAdOgSVUKMVPrBdHMXabd0KNPGVTc_HTbIE_CWwCfAj4BtAP9fXajJzAGwskunT3fRsb11bXLyuLXeAvwD2BdiPHGdfc4RNz0fTv4fbvaLqck520_EHoNtA94HuANtK356mw35XWzGBH8516eb78-Hj9f91MzrJjt_Nia6mC8UQOAdODR3Ys0utDcULR-l4kL0-VVVWZJ9qQF0GFfMujm2XOJfnFO2f5NPwn0pakXTVLAexG4Vtz9bKa4bgZhv0z-8DBVUlVDOvXsv22Wz3eXr2KJu8UZfFWZPIqlmNCCHARsov9h14X7yWh_xEuVooVqXCuOhzCegWsIGhX7nXbmZPfqWbUwUaEqyr0vkII2nNHvDjvDQfKLAuwRvCu0_AvsmrPtCPwF9J5xQs7FTDoQXkk8jHniM2pZPXsFDsEp9YqCR-HdLASSu2kBX0BIqTOLz1MLBRKY4SsoCiMGm6qNTArfsiStoOjonu4WaE_Xm2jYM7YehfSAqo4nhxGM0ZIsObxb7Kte39A4WIRDU?type=png)](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNpVks9u00AQxl_F2nNLJcQpB6S0TlIHIVWCE3YPi72JjWI7MrYQSiJ1dwVNqFoi_rQqHKAhAtJSOLQIEaA8zGCXvAXr9TaiPqw8s79vdubTdJAdOgSVUKMVPrBdHMXabd0KNPGVTc_HTbIE_CWwCfAj4BtAP9fXajJzAGwskunT3fRsb11bXLyuLXeAvwD2BdiPHGdfc4RNz0fTv4fbvaLqck520_EHoNtA94HuANtK356mw35XWzGBH8516eb78-Hj9f91MzrJjt_Nia6mC8UQOAdODR3Ys0utDcULR-l4kL0-VVVWZJ9qQF0GFfMujm2XOJfnFO2f5NPwn0pakXTVLAexG4Vtz9bKa4bgZhv0z-8DBVUlVDOvXsv22Wz3eXr2KJu8UZfFWZPIqlmNCCHARsov9h14X7yWh_xEuVooVqXCuOhzCegWsIGhX7nXbmZPfqWbUwUaEqyr0vkII2nNHvDjvDQfKLAuwRvCu0_AvsmrPtCPwF9J5xQs7FTDoQXkk8jHniM2pZPXsFDsEp9YqCR-HdLASSu2kBX0BIqTOLz1MLBRKY4SsoCiMGm6qNTArfsiStoOjonu4WaE_Xm2jYM7YehfSAqo4nhxGM0ZIsObxb7Kte39A4WIRDU)