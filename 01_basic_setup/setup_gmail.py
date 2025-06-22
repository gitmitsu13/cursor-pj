"""
Gmail API OAuth2.0認証設定スクリプト
初回セットアップ時に実行してください
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail_oauth():
    """
    Gmail APIのOAuth2.0認証を設定します
    """
    creds = None
    
    # 既存のトークンファイルがある場合は読み込み
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 有効な認証情報がない場合、または期限切れの場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.jsonファイルが必要です
            # Google Cloud ConsoleでGmail APIを有効にし、OAuth2.0認証情報を作成してください
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証情報を保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def test_gmail_api():
    """
    Gmail APIの接続をテストします
    """
    try:
        creds = setup_gmail_oauth()
        service = build('gmail', 'v1', credentials=creds)
        
        # プロフィール情報を取得してテスト
        profile = service.users().getProfile(userId='me').execute()
        print(f"Gmail API接続成功: {profile['emailAddress']}")
        
        return True
    except Exception as e:
        print(f"Gmail API接続エラー: {e}")
        return False

if __name__ == "__main__":
    print("Gmail API OAuth2.0認証設定を開始します...")
    print("注意: credentials.jsonファイルが必要です")
    print("Google Cloud ConsoleでGmail APIを有効にし、OAuth2.0認証情報を作成してください")
    
    success = test_gmail_api()
    if success:
        print("設定が完了しました。token.pickleファイルが作成されました。")
    else:
        print("設定に失敗しました。credentials.jsonファイルを確認してください。") 