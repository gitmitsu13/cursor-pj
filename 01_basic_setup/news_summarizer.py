"""
ニュース要約モジュール
OpenAI APIを使用してニュース記事を要約します
"""

import openai
import logging
from typing import List, Dict
import time

logger = logging.getLogger(__name__)

class NewsSummarizer:
    """ニュース要約クラス"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        """
        初期化
        
        Args:
            api_key (str): OpenAI APIキー
            model_name (str): 使用するモデル名
        """
        self.api_key = api_key
        self.model_name = model_name
        openai.api_key = api_key
        
    def summarize_news(self, article_text: str, title: str = "") -> str:
        """
        ニュース記事を要約します
        
        Args:
            article_text (str): 記事の本文
            title (str): 記事のタイトル
            
        Returns:
            str: 要約されたテキスト
        """
        try:
            # プロンプトの作成
            prompt = f"""
以下のマーケットニュース記事を、マーケットに与える影響に焦点を当てて要約してください。

タイトル: {title}

記事内容:
{article_text[:3000]}  # 長すぎる場合は切り詰め

要約の要件:
1. マーケットへの影響を明確に示す
2. 重要な数値や指標があれば含める
3. 簡潔で分かりやすい日本語で
4. 3-5文程度の長さ

要約:
"""
            
            logger.info(f"記事の要約を開始: {title[:50]}...")
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "あなたは金融・経済の専門家です。マーケットニュースを簡潔に要約し、市場への影響を明確に示してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"記事の要約完了: {len(summary)} 文字")
            
            return summary
            
        except openai.error.RateLimitError:
            logger.warning("APIレート制限に達しました。少し待機します...")
            time.sleep(60)  # 1分待機
            return self.summarize_news(article_text, title)  # 再試行
            
        except openai.error.APIError as e:
            logger.error(f"OpenAI APIエラー: {e}")
            return f"要約エラー: {title}"
            
        except Exception as e:
            logger.error(f"要約処理で予期しないエラー: {e}")
            return f"要約エラー: {title}"
    
    def summarize_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        複数の記事を要約します
        
        Args:
            articles (List[Dict]): 記事のリスト
            
        Returns:
            List[Dict]: 要約を含む記事のリスト
        """
        summarized_articles = []
        
        for i, article in enumerate(articles):
            try:
                # 記事の内容を準備
                content = article.get('content', '')
                if not content:
                    content = article.get('description', '')
                
                if not content:
                    logger.warning(f"記事 {i+1} に内容がありません: {article.get('title', 'Unknown')}")
                    continue
                
                # 要約を生成
                summary = self.summarize_news(content, article.get('title', ''))
                
                # 要約を追加
                article_with_summary = article.copy()
                article_with_summary['summary'] = summary
                summarized_articles.append(article_with_summary)
                
                # APIコール間隔を調整（レート制限対策）
                if i < len(articles) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"記事 {i+1} の要約でエラー: {e}")
                # エラーが発生しても他の記事は処理を続行
                article_with_summary = article.copy()
                article_with_summary['summary'] = f"要約エラー: {article.get('title', 'Unknown')}"
                summarized_articles.append(article_with_summary)
        
        logger.info(f"{len(summarized_articles)} 件の記事を要約完了")
        return summarized_articles
    
    def generate_daily_summary(self, summarized_articles: List[Dict]) -> str:
        """
        日次サマリーを生成します
        
        Args:
            summarized_articles (List[Dict]): 要約済み記事のリスト
            
        Returns:
            str: 日次サマリー
        """
        try:
            if not summarized_articles:
                return "本日は重要なマーケットニュースはありませんでした。"
            
            # サマリー用のプロンプトを作成
            articles_text = ""
            for i, article in enumerate(summarized_articles[:5], 1):  # 上位5件のみ
                articles_text += f"{i}. {article.get('title', 'Unknown')}\n"
                articles_text += f"   要約: {article.get('summary', 'No summary')}\n\n"
            
            prompt = f"""
以下のマーケットニュースの要約を基に、本日の市場動向を簡潔にまとめてください。

本日の主要ニュース:
{articles_text}

要件:
1. 市場全体の動向を把握
2. 最も重要な影響要因を特定
3. 投資家への示唆を含める
4. 3-4段落程度の長さ
5. 分かりやすい日本語で

本日の市場動向サマリー:
"""
            
            logger.info("日次サマリーの生成を開始...")
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "あなたは金融・経済の専門アナリストです。市場動向を簡潔にまとめ、投資家に有用な洞察を提供してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            daily_summary = response.choices[0].message.content.strip()
            logger.info("日次サマリーの生成完了")
            
            return daily_summary
            
        except Exception as e:
            logger.error(f"日次サマリー生成でエラー: {e}")
            return "日次サマリーの生成中にエラーが発生しました。" 