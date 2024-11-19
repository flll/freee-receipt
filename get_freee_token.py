import requests
import json
import os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN_URL = config['freee']['token_url']
REDIRECT_URI = config['freee']['redirect_uri']
CLIENT_ID = config['freee']['client_id']
CLIENT_SECRET = config['freee']['client_secret']
CODE = config['freee']['code']
TOKEN_FILE = "freee_tokens.json"

def save_tokens(access_token, refresh_token):
    """トークンをJSONファイルに保存"""
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)

def load_tokens():
    """保存されたトークンを読み込み"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return {"access_token": None, "refresh_token": None}

def get_access_token():
    """初期認可コードを使用してアクセストークンを取得"""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cache-control': 'no-cache'
    }

    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': CODE
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens
    else:
        raise Exception(f"トークン取得エラー: {response.text}")

def refresh_access_token(refresh_token):
    """リフレッシュトークンを使用して新しいアクセストークンを取得"""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'cache-control': 'no-cache'
    }

    data = {
        'grant_type': 'refresh_token',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens
    else:
        raise Exception(f"トークン更新エラー: {response.text}")

def get_current_token():
    """現在の有効なトークンを取得する関数"""
    saved_tokens = load_tokens()

    if not saved_tokens['refresh_token']:
        raise Exception("トークンが存在しません。初回認証を行ってください。")

    try:
        # 一度リフレッシュを試みる
        new_tokens = refresh_access_token(saved_tokens['refresh_token'])
        return new_tokens['access_token']
    except Exception as e:
        raise Exception(f"トークン更新に失敗しました: {e}")

def refresh_token():
    """外部から呼び出し可能なリフレッシュ関数"""
    saved_tokens = load_tokens()
    if not saved_tokens['refresh_token']:
        raise Exception("リフレッシュトークンが存在しません")

    return refresh_access_token(saved_tokens['refresh_token'])

def main():
    # 保存されたトークンを読み込む
    saved_tokens = load_tokens()

    if saved_tokens['refresh_token']:
        # リフレッシュトークンが存在する場合は、それを使用してトークンを更新
        try:
            new_tokens = refresh_access_token(saved_tokens['refresh_token'])
            print("トークン更新成功")
        except Exception as e:
            print(f"トークン更新エラー: {e}")
    else:
        # リフレッシュトークンが存在しない場合は、新規にアクセストークンを取得
        try:
            tokens = get_access_token()
            print("初回トークン取得成功")
        except Exception as e:
            print(f"トークン取得エラー: {e}")

if __name__ == "__main__":
    main()