"""
マーケットニュース収集モジュール
NewsAPIを使用してマーケット関連のニュースを収集します
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NewsCollector:
    """マーケットニュース収集クラス"""
    
    def __init__(self, api_key: str):
        """
        初期化
        
        Args:
            api_key (str): NewsAPIのAPIキー
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        
    def get_market_news(self, keywords: Optional[List[str]] = None, 
                       max_articles: int = 10) -> List[Dict]:
        """
        マーケットニュースを取得します
        
        Args:
            keywords (List[str], optional): 検索キーワードのリスト
            max_articles (int): 取得する記事の最大数
            
        Returns:
            List[Dict]: ニュース記事のリスト
        """
        try:
            # デフォルトのキーワード（マーケット関連）
            if keywords is None:
                keywords = [
                    "market", "economy", "finance", "stocks", "trading",
                    "investment", "economic", "financial", "business"
                ]
            
            # 昨日の日付を取得
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 複数のキーワードで検索
            all_articles = []
            
            for keyword in keywords[:3]:  # APIコール数を制限
                try:
                    url = f"{self.base_url}/everything"
                    params = {
                        'q': keyword,
                        'from': yesterday,
                        'sortBy': 'relevancy',
                        'language': 'en',
                        'apiKey': self.api_key,
                        'pageSize': min(max_articles, 20)  # API制限
                    }
                    
                    logger.info(f"キーワード '{keyword}' でニュースを検索中...")
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get('status') == 'ok':
                        articles = data.get('articles', [])
                        # 重複を除去
                        for article in articles:
                            if not any(a.get('url') == article.get('url') for a in all_articles):
                                all_articles.append(article)
                        
                        logger.info(f"キーワード '{keyword}' で {len(articles)} 件の記事を取得")
                    else:
                        logger.warning(f"キーワード '{keyword}' の検索でエラー: {data.get('message', 'Unknown error')}")
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"キーワード '{keyword}' の検索でリクエストエラー: {e}")
                except Exception as e:
                    logger.error(f"キーワード '{keyword}' の検索で予期しないエラー: {e}")
            
            # 記事数を制限
            all_articles = all_articles[:max_articles]
            
            # 記事データを整形
            formatted_articles = []
            for article in all_articles:
                formatted_article = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'author': article.get('author', '')
                }
                formatted_articles.append(formatted_article)
            
            logger.info(f"合計 {len(formatted_articles)} 件の記事を収集完了")
            return formatted_articles
            
        except Exception as e:
            logger.error(f"ニュース収集で予期しないエラー: {e}")
            return []
    
    def get_article_content(self, url: str) -> str:
        """
        記事の本文を取得します（Webスクレイピング）
        
        Args:
            url (str): 記事のURL
            
        Returns:
            str: 記事の本文
        """
        try:
            # 注意: Webスクレイピングを行う場合は、対象サイトのrobots.txtと利用規約を確認してください
            # 可能な限り公式APIを優先することを推奨します
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 簡易的な本文抽出（実際の実装ではより高度な解析が必要）
            content = response.text
            # ここでは簡易的な実装とし、実際の使用では適切なHTMLパーサーを使用してください
            
            return content[:2000]  # 長すぎる場合は切り詰め
            
        except Exception as e:
            logger.error(f"記事本文の取得でエラー: {e}")
            return "" 