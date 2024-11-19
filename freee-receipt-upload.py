import anthropic
import os
import glob
import configparser
from get_freee_token import get_current_token, refresh_token


# 処理対象のディレクトリを指定
source_dir = "./batched"

config = configparser.ConfigParser()
config.read('config.ini')
ANTHROPIC_API_KEY = config['anthropic']['api_key']

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)

# source_dirからjpgファイルを取得
jpg_files = glob.glob(os.path.join(source_dir, "*.jpg"))

for jpg_file in jpg_files:
    # ファイル名からbatch_idを抽出
    filename = os.path.basename(jpg_file)
    batch_id = os.path.splitext(filename)[0]  # 拡張子を除去

    print(f"処理中のファイル: {filename}")
    print(f"Batch ID: {batch_id}")

    # 認証確認のためのデバッグ出力を追加
    try:
        message_batch = client.beta.messages.batches.retrieve(
            batch_id,
        )
    except anthropic.AuthenticationError as e:
        print(f"認証エラーが発生しました: {e}")
        print(f"使用中のAPIキー: {ANTHROPIC_API_KEY}...") # セキュリティのため最初の5文字のみ表示
        exit(1)

    while message_batch.processing_status == "in_progress":
        print("in_progress... 30秒後に再確認します")
        import time
        time.sleep(30)

        message_batch = client.beta.messages.batches.retrieve(
            batch_id,
        )

    for result in client.beta.messages.batches.results(
        batch_id,
    ):
        match result.result.type:
            case "succeeded":
                print(f"成功！ {result.custom_id} {batch_id}")
                print(result.result.message.content[0].text)
            case "errored":
                if result.result.error.type == "invalid_request":
                    # リクエスト本文を修正してから再送信する必要があります
                    print(f"バリデーションエラー {result.custom_id} {batch_id}")
                    print("リクエスト本文を修正してから再送信する必要があります")
                    exit(1)
                else:
                    print(f"サーバーエラー {result.custom_id} {batch_id}")
                    exit(1)
            case "expired":
                print(f"リクエストの有効期限切れ {result.custom_id} {batch_id}")
                exit(1)


    import requests

    url = "https://api.freee.co.jp/api/1/receipts"

    payload = {
        "company_id": config['freee']['company_id'],
        "document_type": "receipt",
    }

    # message_batchからの内容更新は維持
    for result in client.beta.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            import json
            message_text = result.result.message.content[0].text
            message_content = json.loads(message_text)
            new_content = {k: v for k, v in message_content.items() if k not in payload}
            payload.update(new_content)
            break

    files = {
        'receipt': ('file', open(jpg_file, 'rb'), 'application/octet-stream')
    }

    headers = {
        'Accept': 'application/json',
        'Authorization': f"Bearer {get_current_token()}",
        'X-Api-Version': '2020-06-15'
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        files=files
    )

    print(response.status_code)
    if response.status_code == 401:
        print("トークンを更新します...")
        new_tokens = refresh_token()
        headers['Authorization'] = f"Bearer {new_tokens['access_token']}"
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            files=files
        )


    print("ステータスコード:", response.status_code)
    print("レスポンスヘッダー:", response.headers)
    print("レスポンスボディ:", response.text)
    try:
        json_response = response.json()
        print("JSONレスポンス:")
        for key, value in json_response.items():
            print(f"  {key}: {value}")
    except ValueError:
        print("JSONではないレスポンスが返されました")
    print("レスポンス時間:", response.elapsed.total_seconds(), "秒")
