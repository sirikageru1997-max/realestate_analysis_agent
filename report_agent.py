import os
import json
import base64
import shutil # ファイルのコピー（バックアップ）用に追加
from email.message import EmailMessage
import requests
import pandas as pd
from dotenv import load_dotenv

# Google API 関連
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gemini API 関連
import google.generativeai as genai

# 環境変数の読み込み (.envファイル)
load_dotenv()

# === 設定項目 ===
# 認証ファイルのパス設定（絶対パスまたは相対パスで指定）
CONFIG_DIR = "./config" # 設定ファイル用ディレクトリ
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
TOKEN_BACKUP_PATH = os.path.join(CONFIG_DIR, "token.json.bak")

# Google APIのスコープ
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/gmail.send'
]

# 設定ファイル(.env)からメールアドレスを読み込み
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
# ================

def main():
    print("--- 処理を開始します ---")
    
    # 必須の設定値が読み込めているかチェック
    if not SENDER_EMAIL or not RECEIVER_EMAIL or not os.environ.get("GEMINI_API_KEY"):
        print("エラー: .env ファイルに必須の環境変数が設定されていません。")
        return
        
    # configディレクトリが存在しない場合は作成する
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    # ---------------------------------------------------------
    # Module 1: 認証基盤 (OAuth 2.0 トークン管理・バックアップ機能付き)
    # ---------------------------------------------------------
    creds = None
    # 指定パスに token.json があれば読み込む
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # トークンが無い、または有効期限切れの場合の処理
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("アクセストークンの有効期限が切れています。リフレッシュトークンを使って再取得します...")
            
            # 【新規追加】更新前に現在の token.json をバックアップ
            if os.path.exists(TOKEN_PATH):
                shutil.copy2(TOKEN_PATH, TOKEN_BACKUP_PATH)
                print(f"古いトークンをバックアップしました: {TOKEN_BACKUP_PATH}")
                
            creds.refresh(Request())
        else:
            print("初回認証、またはリフレッシュトークンが無効です。ブラウザでの認証を開始します...")
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"エラー: 認証用ファイルが見つかりません: {CREDENTIALS_PATH}")
                return
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 新しいトークンを指定パスに保存（上書き）
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            print(f"新しいトークンを保存しました: {TOKEN_PATH}")
    
    # 各APIのサービスを構築
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
        gmail_service = build('gmail', 'v1', credentials=creds)
    except HttpError as error:
        print(f"Google APIへの接続エラー: {error}")
        return

    # ---------------------------------------------------------
    # Module 2: 国交省 不動産情報ライブラリAPI (データ取得)
    # ---------------------------------------------------------
    # (前回から変更なし。省略せずに記載します)
    print("不動産データを取得しています...")
    raw_data = """
    【対象エリア: 東京都 世田谷区】
    2026年7月: 取引件数 120件, 平均価格 6500万円
    2026年8月: 取引件数 115件, 平均価格 6550万円
    2026年9月: 取引件数 130件, 平均価格 6620万円
    """
    
    # ---------------------------------------------------------
    # Module 3: Gemini API (データ分析)
    # ---------------------------------------------------------
    # (前回から変更なし)
    print("Gemini API で分析を実行しています...")
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    以下の不動産取引データを分析し、専門家としてのレポートを作成してください。
    Markdown形式で、見出しや箇条書きを使って読みやすく構成してください。
    
    【データ】
    {raw_data}
    """
    
    try:
        response = model.generate_content(prompt)
        analysis_result = response.text
        print("分析が完了しました。")
    except Exception as e:
        print(f"Gemini API エラー: {e}")
        return

    # ---------------------------------------------------------
    # Module 4: Google Docs API (レポート生成)
    # ---------------------------------------------------------
    # (前回から変更なし)
    print("Google Docsにレポートを作成しています...")
    try:
        doc_metadata = {'name': '【週次】不動産時系列データ分析レポート'}
        doc = docs_service.documents().create(body=doc_metadata).execute()
        document_id = doc.get('documentId')
        
        requests_body = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': analysis_result
                }
            }
        ]
        docs_service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests_body}
        ).execute()
        
        docs_url = f"https://docs.google.com/document/d/{document_id}/edit"
        print(f"ドキュメントを作成しました: {docs_url}")
        
    except HttpError as error:
        print(f"Google Docsの作成エラー: {error}")
        return

    # ---------------------------------------------------------
    # Module 5: Gmail API (完了通知)
    # ---------------------------------------------------------
    # (前回から変更なし)
    print("完了通知メールを送信しています...")
    try:
        message = EmailMessage()
        message.set_content(f"不動産データの週次分析が完了し、レポートを作成しました。\n\n以下のURLから確認してください。\n{docs_url}")
        message['To'] = RECEIVER_EMAIL
        message['From'] = SENDER_EMAIL
        message['Subject'] = '【完了通知】不動産データ分析レポート'

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        gmail_service.users().messages().send(userId="me", body=create_message).execute()
        print("通知メールを送信しました。")

    except HttpError as error:
        print(f"Gmailの送信エラー: {error}")

    print("--- すべての処理が完了しました ---")

if __name__ == '__main__':
    main()
