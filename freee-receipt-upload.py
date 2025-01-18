import anthropic
import os
import glob
import configparser
import json
from get_freee_token import get_current_token, refresh_token
import re
from pprint import pprint
import time
import concurrent.futures
from time import sleep
from datetime import datetime, timedelta
import argparse


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

RATE_LIMIT_PER_SECOND = 1
MAX_WORKERS = 4
REQUEST_TIMESTAMPS = []
MAX_RETRIES = 3
RATE_LIMIT_WINDOW = 60
DELAY_BETWEEN_REQUESTS = 1

parser = argparse.ArgumentParser(description='レシート処理プログラム')
parser.add_argument('--parallel', action='store_true',
                   help='並列処理モードで実行（デフォルトは直列処理）')
args = parser.parse_args()

def wait_for_rate_limit():
    """レート制限に従って待機する"""
    now = time.time()

    # 直近1秒間のリクエスト数を確認
    recent_requests = [ts for ts in REQUEST_TIMESTAMPS if now - ts < 1]

    if recent_requests:
        # 最も古いリクエストから1秒経過するまで待機
        sleep_time = 1 - (now - recent_requests[0])
        if sleep_time > 0:
            time.sleep(sleep_time)

    # 現在のタイムスタンプを記録
    REQUEST_TIMESTAMPS.append(time.time())
    # 古いタイムスタンプを削除
    while len(REQUEST_TIMESTAMPS) > 100:  # 直近100件のみ保持
        REQUEST_TIMESTAMPS.pop(0)

def process_receipt(jpg_file):
    # レート制限の適用
    wait_for_rate_limit()

    # ファイル名からbatch_idを抽出
    filename = os.path.basename(jpg_file)
    batch_id = os.path.splitext(filename)[0]

    print(f"処理中のファイル: {filename}")
    print(f"Batch ID: {batch_id}")

    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            message_batch = client.beta.messages.batches.retrieve(
                batch_id,
            )
            break  # 成功したらループを抜ける
        except anthropic.RateLimitError as e:
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                print(f"レート制限エラーが{MAX_RETRIES}回発生しました。処理を中断します。")
                print("エラー詳細:", str(e))
                raise

            # 待機時間を動的に調整
            wait_time = min(RATE_LIMIT_WINDOW * (2 ** (retry_count - 1)), 300)  # 最大5分
            next_try = datetime.now() + timedelta(seconds=wait_time)
            print(f"レート制限エラーが発生しました。{wait_time}秒待機します...")
            print(f"次回試行時刻: {next_try.strftime('%H:%M:%S')}")
            sleep(wait_time)
        except anthropic.AuthenticationError as e:
            print(f"認証エラーが発生しました: {e}")
            print(f"使用中のAPIキー: {ANTHROPIC_API_KEY}...")
            raise

    while message_batch.processing_status == "in_progress":
        print("in_progress... 30秒後に再確認します")
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
            case "errored":
                if result.result.error.type == "invalid_request":
                    print(f"バリデーションエラー {result.custom_id} {batch_id}")
                    raise Exception("バリデーションエラーが発生しました")
                else:
                    print(f"サーバーエラー {result.custom_id} {batch_id}")
                    raise Exception("サーバーエラーが発生しました")
            case "expired":
                print(f"リクエストの有効期限切れ {result.custom_id} {batch_id}")
                raise Exception("リクエストの有効期限切れ")


    import requests

    freee_api_url = "https://api.freee.co.jp/api/1/receipts"  # freee APIのURLを別の変数に

    payload = {
        "company_id": config['freee']['company_id'],
        "document_type": "receipt",
    }

    for result in client.beta.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            message_text = result.result.message.content[0].text

            match = re.search(r'<output>(.*?)</output>', message_text, re.DOTALL)
            if match:
                message_text = match.group(1).strip()

            message_content = json.loads(message_text)
            message_content['description'] = message_content['description'][:255]

            if ('invoice_registration_number' in message_content):
                message_content['invoice_registration_number'] = message_content['invoice_registration_number'].replace('-', '')
                invoice_num = message_content['invoice_registration_number']
                if invoice_num.startswith('T') and len(invoice_num) == 14:
                    try:
                        sel_reg_no = invoice_num[1:]
                        invoice_url = f"https://www.invoice-kohyo.nta.go.jp/regno-search/detail?selRegNo={sel_reg_no}"
                        response = requests.get(invoice_url)
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        real_partner_name = soup.select_one('p.itemdata.sp_nmTsuushou_data')
                        if real_partner_name:
                            message_content['receipt_metadatum_partner_name'] = real_partner_name.text.strip()
                    except Exception as e:
                        print(f"Error fetching partner_name: {e}")
            pprint(message_content, indent=2, width=80)

            new_content = {k: v for k, v in message_content.items() if k not in payload}
            payload.update(new_content)
            break

    if not os.path.exists(jpg_file) or os.path.getsize(jpg_file) == 0:
        print(f"エラー: ファイル {jpg_file} が存在しないか空です")
        return False

    with open(jpg_file, 'rb') as file:
        files = {
            'receipt': ('receipt.jpg', file, 'image/jpeg')
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {get_current_token()}",
            'X-Api-Version': '2020-06-15'
        }

        encoded_payload = {
            key: value.encode('utf-8').decode('utf-8') if isinstance(value, str) else value
            for key, value in payload.items()
        }

        encoded_payload = {
            key: value for key, value in encoded_payload.items()
            if value != "unknown"
        }

        response = requests.post(
            freee_api_url,
            headers=headers,
            data=encoded_payload,
            files=files
        )

        print("ステータスコード:", response.status_code)

        # post.logにログを記録
        with open('./post.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {filename}\n")
            log_file.write(f"ステータスコード: {response.status_code}\n")
            log_file.write(f"リクエストURL: {freee_api_url}\n")
            log_file.write(f"ペイロード: {json.dumps(encoded_payload, ensure_ascii=False, indent=2)}\n")
            log_file.write(f"レスポンス時間: {response.elapsed.total_seconds()}秒\n")
            try:
                log_file.write(f"レスポンス: {json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")
            except ValueError:
                log_file.write(f"レスポンス: {response.text}\n")
            log_file.write("-" * 80 + "\n")

        if response.status_code == 401:
            print("トークンを更新します...")
            new_tokens = refresh_token()
            headers['Authorization'] = f"Bearer {new_tokens['access_token']}"

            file.seek(0)
            response = requests.post(
                freee_api_url,
                headers=headers,
                data=encoded_payload,
                files=files
            )
        elif response.status_code == 403:
            print("freee APIからのForbiddenエラー")
            try:
                error_json = response.json()
                print("エラー詳細:", json.dumps(error_json, indent=2, ensure_ascii=False))
            except ValueError:
                print("レスポンスボディ:", response.text)

        if not 200 <= response.status_code < 300:
            print("エラーが発生しました")
            print("ステータスコード:", response.status_code)
            print("レスポンスヘッダー:", response.headers)
            print("レスポンスボディ:", response.text)

            # スキップログを記録
            try:
                error_json = response.json()
                with open('./skip.log', 'a', encoding='utf-8') as f:
                    f.write(f"{filename}\t{response.status_code}\t{json.dumps(error_json, ensure_ascii=False)}\n")
            except ValueError:
                with open('./skip.log', 'a', encoding='utf-8') as f:
                    f.write(f"{filename}\t{response.status_code}\t{response.text}\n")

            raise Exception(f"APIエラー: {response.status_code}")

        print("ステータスコード:", response.status_code)
        try:
            json_response = response.json()
            print("JSONレスポンス:")
            print(json.dumps(json_response, indent=2, ensure_ascii=False))
        except ValueError:
            print("JSONではないレスポンスが返されました")
        print("レスポンス時間:", response.elapsed.total_seconds(), "秒")

        if 200 <= response.status_code < 300:
            print(f"成功: {filename}")
            return True
        else:
            print(f"失敗: {filename}")
            return False

def process_files_sequential(jpg_files):
    """直列処理でファイルを処理"""
    success_count = 0
    failure_count = 0

    for jpg_file in jpg_files:
        try:
            result = process_receipt(jpg_file)
            if result:
                success_count += 1
            else:
                failure_count += 1
                raise Exception("処理が失敗しました")
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
            raise

    return success_count, failure_count

def process_files_parallel(jpg_files):
    """並列処理でファイルを処理"""
    success_count = 0
    failure_count = 0
    active_futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for jpg_file in jpg_files:
            # 1秒間隔でリクエストを送信
            time.sleep(1.5)

            future = executor.submit(process_receipt, jpg_file)
            active_futures.append(future)

            done_futures = []
            for future in active_futures:
                if future.done():
                    try:
                        result = future.result()
                        if result:
                            success_count += 1
                        else:
                            failure_count += 1
                            raise Exception("処理が失敗しました")
                    except Exception as e:
                        print(f"エラーが発生しました: {str(e)}")
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise
                    done_futures.append(future)

            for done_future in done_futures:
                active_futures.remove(done_future)

        for future in active_futures:
            try:
                result = future.result()
                if result:
                    success_count += 1
                else:
                    failure_count += 1
                    raise Exception("処理が失敗しました")
            except Exception as e:
                print(f"エラーが発生しました: {str(e)}")
                executor.shutdown(wait=False, cancel_futures=True)
                raise

    return success_count, failure_count

# メイン処理の実行
print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"処理モード: {'並列処理' if args.parallel else '直列処理'}")
print(f"予想所要時間: 約{len(jpg_files) * DELAY_BETWEEN_REQUESTS / 60:.1f}分")

success_count = 0
failure_count = 0

try:
    if args.parallel:
        success_count, failure_count = process_files_parallel(jpg_files)
    else:
        success_count, failure_count = process_files_sequential(jpg_files)

except Exception as e:
    print(f"\n処理が中断されました: {str(e)}")
    print(f"成功: {success_count}件")
    print(f"失敗: {failure_count}件")
    exit(1)

print(f"\n処理完了！")
print(f"成功: {success_count}件")
print(f"失敗: {failure_count}件")
