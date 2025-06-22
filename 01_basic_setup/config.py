"""
設定管理モジュール
環境変数から設定を安全に読み込みます
"""

import os
import logging
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def load_config():
    """
    環境変数から設定を読み込み、辞書形式で返します
    
    Returns:
        dict: 設定値の辞書
    """
    config = {
        # NewsAPI設定
        'news_api_key': os.environ.get('NEWS_API_KEY'),
        
        # OpenAI API設定
        'openai_api_key': os.environ.get('OPENAI_API_KEY'),
        
        # Gmail設定
        'gmail_client_id': os.environ.get('GMAIL_CLIENT_ID'),
        'gmail_client_secret': os.environ.get('GMAIL_CLIENT_SECRET'),
        'gmail_refresh_token': os.environ.get('GMAIL_REFRESH_TOKEN'),
        'gmail_username': os.environ.get('GMAIL_USERNAME'),
        'gmail_app_password': os.environ.get('GMAIL_APP_PASSWORD'),
        
        # メール送信設定
        'recipient_email': os.environ.get('RECIPIENT_EMAIL'),
        'sender_email': os.environ.get('SENDER_EMAIL'),
        
        # システム設定
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'max_news_articles': int(os.environ.get('MAX_NEWS_ARTICLES', 10))
    }
    
    # 必須設定の確認
    required_keys = ['news_api_key', 'openai_api_key', 'recipient_email']
    missing_keys = [key for key in required_keys if not config[key]]
    
    if missing_keys:
        raise ValueError(f"必須の環境変数が設定されていません: {missing_keys}")
    
    return config

def setup_logging(log_level='INFO'):
    """
    ログ設定を初期化します
    
    Args:
        log_level (str): ログレベル
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('market_analysis.log'),
            logging.StreamHandler()
        ]
    ) 