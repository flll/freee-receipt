import requests
import json

def load_tokens():
    with open('freee_tokens.json', 'r') as f:
        return json.load(f)

def get_companies():
    tokens = load_tokens()
    access_token = tokens['access_token']
    
    url = "https://api.freee.co.jp/api/1/companies"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Api-Version": "2020-06-15"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    companies = get_companies()
    if companies:
        print(json.dumps(companies, indent=2, ensure_ascii=False)) 