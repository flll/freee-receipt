import anthropic
import configparser
import sys

target_dir = "./batched"

config = configparser.ConfigParser()
config.read('config.ini')

client = anthropic.Anthropic(
    api_key=config['anthropic']['api_key'],
)

if len(sys.argv) < 2:
    print("使用方法: python view.py <バッチID>")
    sys.exit(1)
batch_id = sys.argv[1]

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
            #print(result)
        case "errored":
            if result.result.error.type == "invalid_request":
                print(f"バリデーションエラー {result.custom_id}")
            else:
                print(f"サーバーエラー {result.custom_id}")
        case "expired":
            print(f"リクエストの有効期限切れ {result.custom_id}")
