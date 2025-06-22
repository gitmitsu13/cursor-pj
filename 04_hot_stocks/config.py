"""
フェーズ4: 動きのあった会社・注目銘柄抽出 - 設定管理モジュール
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
        # APIキー
        'openai_api_key': os.environ.get('OPENAI_API_KEY'),
        
        # メール設定
        'gmail_username': os.environ.get('GMAIL_USERNAME'),
        'gmail_app_password': os.environ.get('GMAIL_APP_PASSWORD'),
        'recipient_email': os.environ.get('RECIPIENT_EMAIL'),
        'sender_email': os.environ.get('SENDER_EMAIL'),
        
        # システム設定
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'hot_stock_days': int(os.environ.get('HOT_STOCK_DAYS', 5)),
        'volume_threshold': float(os.environ.get('VOLUME_THRESHOLD', 2.0)),
        'price_change_threshold': float(os.environ.get('PRICE_CHANGE_THRESHOLD', 0.05)),
        'target_symbols': os.environ.get('TARGET_SYMBOLS', '7203.T,6758.T,AAPL,MSFT').split(','),
    }
    
    # 必須設定の確認
    required_keys = ['openai_api_key', 'recipient_email']
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
            logging.FileHandler('hot_stocks.log'),
            logging.StreamHandler()
        ]
    ) 