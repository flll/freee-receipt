import anthropic
import configparser
import sys
import glob
import os

target_dir = "./batched"

config = configparser.ConfigParser()
config.read('config.ini')

client = anthropic.Anthropic(
    api_key=config['anthropic']['api_key'],
)

def process_batch(batch_id):
    message_batch = client.beta.messages.batches.retrieve(
        batch_id,
    )

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
                print(f"成功！ {result.custom_id}")
                print(result.result.message.content[0].text)
            case "errored":
                if result.result.error.type == "invalid_request":
                    print(f"バリデーションエラー {result.custom_id}")
                else:
                    print(f"サーバーエラー {result.custom_id}")
            case "expired":
                print(f"リクエストの有効期限切れ {result.custom_id}")

if len(sys.argv) < 2:
    # batchedフォルダからjpgファイルを取得
    jpg_files = glob.glob(os.path.join(target_dir, "*.jpg"))

    if not jpg_files:
        print("batchedフォルダにjpgファイルが見つかりません")
        sys.exit(1)

    for jpg_file in jpg_files:
        filename = os.path.basename(jpg_file)
        batch_id = os.path.splitext(filename)[0]

        print(f"\n処理中のファイル: {filename}")
        print(f"Batch ID: {batch_id}")
        process_batch(batch_id)
else:
    batch_id = sys.argv[1]
    process_batch(batch_id)
