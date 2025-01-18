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

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'cache-control': 'no-cache'
}

def save_tokens(access_token, refresh_token):
    """トークンをJSONファイルに保存"""
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=4)

def load_tokens():
    """保存されたトークンを読み込み"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return {"access_token": None, "refresh_token": None}

def get_access_token():
    """初期認可コードを使用してアクセストークンを取得"""
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': CODE
    }

    response = requests.post(TOKEN_URL, headers=HEADERS, data=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens
    raise Exception(f"APIエラー: {response.text}")

def refresh_access_token(refresh_token):
    """リフレッシュトークンを使用して新しいアクセストークンを取得"""
    data = {
        'grant_type': 'refresh_token',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    response = requests.post(TOKEN_URL, headers=HEADERS, data=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens['access_token'], tokens['refresh_token'])
        return tokens
    raise Exception(f"APIエラー: {response.text}")

def get_current_token():
    """現在の有効なトークンを取得する関数"""
    try:
        saved_tokens = load_tokens()
        if not saved_tokens['refresh_token']:
            print("トークンが存在しません")
            return None

        return saved_tokens['access_token']
        
    except Exception as e:
        print(f"トークン取得エラー: {e}")
        return None

def refresh_token():
    """外部から呼び出し可能なリフレッシュ関数"""
    saved_tokens = load_tokens()
    if not saved_tokens['refresh_token']:
        print("リフレッシュトークンが存在しません")
        return None
    
    url = TOKEN_URL
    data = {
        "grant_type": "refresh_token",
        "refresh_token": saved_tokens['refresh_token'],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(url, headers=HEADERS, data=data)
        if response.status_code == 200:
            tokens = response.json()
            save_tokens(tokens['access_token'], tokens['refresh_token'])
            return tokens
        else:
            print(f"トークン更新エラー: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"トークン更新中の例外: {e}")
        return None

def main():
    saved_tokens = load_tokens()
    try:
        if saved_tokens['refresh_token']:
            refresh_access_token(saved_tokens['refresh_token'])
            print("トークン更新成功")
        else:
            get_access_token()
            print("初回トークン取得成功")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()
