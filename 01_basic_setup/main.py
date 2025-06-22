"""
市場情報自動収集・分析システム - メインファイル
フェーズ1: マーケットニュースの自動要約とGmail送信システム
"""

import logging
from datetime import datetime
from config import load_config, setup_logging
from news_collector import NewsCollector
from news_summarizer import NewsSummarizer
from email_sender import EmailSender

def main():
    """メイン処理"""
    try:
        # 設定の読み込み
        config = load_config()
        
        # ログ設定
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)
        
        logger.info("市場情報自動収集・分析システムを開始します")
        
        # ニュース収集
        logger.info("ステップ1: マーケットニュースの収集を開始")
        news_collector = NewsCollector(config['news_api_key'])
        articles = news_collector.get_market_news(max_articles=config['max_news_articles'])
        
        if not articles:
            logger.warning("ニュース記事が取得できませんでした")
            return
        
        logger.info(f"{len(articles)} 件の記事を収集しました")
        
        # ニュース要約
        logger.info("ステップ2: ニュース記事の要約を開始")
        news_summarizer = NewsSummarizer(config['openai_api_key'])
        summarized_articles = news_summarizer.summarize_multiple_articles(articles)
        
        if not summarized_articles:
            logger.warning("要約された記事がありません")
            return
        
        # 日次サマリー生成
        logger.info("ステップ3: 日次サマリーの生成を開始")
        daily_summary = news_summarizer.generate_daily_summary(summarized_articles)
        
        # メール送信
        logger.info("ステップ4: メール送信を開始")
        email_sender = EmailSender(config['gmail_username'], config['gmail_app_password'])
        
        # メール本文の作成
        email_body = email_sender.create_market_report_email(daily_summary, summarized_articles)
        
        # 件名の作成
        today = datetime.now().strftime('%Y年%m月%d日')
        subject = f"市場情報レポート - {today}"
        
        # メール送信
        success = email_sender.send_email(
            subject=subject,
            body=email_body,
            to_address=config['recipient_email']
        )
        
        if success:
            logger.info("メール送信が完了しました")
        else:
            logger.error("メール送信に失敗しました")
        
        logger.info("市場情報自動収集・分析システムが正常に完了しました")
        
    except Exception as e:
        logger.error(f"システム実行中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    main() 