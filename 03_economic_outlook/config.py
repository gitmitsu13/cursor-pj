"""
フェーズ3: 経済指標見通し考察 - 設定管理モジュール
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
        'fred_api_key': os.environ.get('FRED_API_KEY'),
        
        # メール設定
        'gmail_username': os.environ.get('GMAIL_USERNAME'),
        'gmail_app_password': os.environ.get('GMAIL_APP_PASSWORD'),
        'recipient_email': os.environ.get('RECIPIENT_EMAIL'),
        'sender_email': os.environ.get('SENDER_EMAIL'),
        
        # システム設定
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'max_news_articles': int(os.environ.get('MAX_NEWS_ARTICLES', 10)),
        
        # グラフ設定
        'graph_output_dir': os.environ.get('GRAPH_OUTPUT_DIR', 'graphs'),
        'graph_dpi': int(os.environ.get('GRAPH_DPI', 300)),
        
        # 経済指標設定
        'default_indicators': os.environ.get('DEFAULT_INDICATORS', 
                                           'us_gdp,us_cpi,us_unemployment,us_interest_rate').split(','),
        'default_market_indices': os.environ.get('DEFAULT_MARKET_INDICES',
                                               '^DJI,^GSPC,^IXIC,^N225').split(','),
        
        # データ取得期間設定
        'economic_data_days': int(os.environ.get('ECONOMIC_DATA_DAYS', 365)),
        'market_data_days': int(os.environ.get('MARKET_DATA_DAYS', 30))
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
            logging.FileHandler('economic_outlook.log'),
            logging.StreamHandler()
        ]
    ) 