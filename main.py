import anthropic
from anthropic.types.beta.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.beta.messages.batch_create_params import Request
import os
import base64
import glob
import time
import shutil
from PIL import Image
from io import BytesIO
from resize import resize_image
import configparser

# 処理対象のディレクトリを指定
source_dir = "./images"
target_dir = "./batched"
batches_enabled = True


config = configparser.ConfigParser()
config.read('config.ini')
ANTHROPIC_API_KEY = config['anthropic']['api_key']


client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)

with open('./prompt.txt', 'r') as f:
    system_prompt = f.read()

def create_message_params(system_prompt, base64_image):
    """メッセージパラメータを作成する共通関数"""
    return {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "temperature": 0,
        "system": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    }

def process_image(image_path, is_first=False):
    if is_first:
        time.sleep(5)
    custom_id = os.path.basename(image_path).replace('.', '_').replace('/', '_')

    with Image.open(image_path) as img:
        resized_img = resize_image(img)
        img_byte_arr = BytesIO()
        resized_img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

    message_params = create_message_params(system_prompt, base64_image)

    if batches_enabled:
        message = client.beta.messages.batches.create(
            betas=["prompt-caching-2024-07-31"],
            requests=[
                Request(
                    custom_id=custom_id,
                    params=MessageCreateParamsNonStreaming(**message_params)
                )
            ]
        )
        print(message.id)
        # 画像をtarget_dirにコピー
        target_path = os.path.join(target_dir, f"{message.id}.jpg")
        shutil.copy2(image_path, target_path)
    else:
        message = client.beta.prompt_caching.messages.create(**message_params)
        print(message.content)

jpg_files = glob.glob(os.path.join(source_dir, "*.jpg"))
for i, jpg_file in enumerate(jpg_files):
    print(f"Processing {jpg_file}...")
    process_image(jpg_file, is_first=(i==1))
    print("-" * 80)
