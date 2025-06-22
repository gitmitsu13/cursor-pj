"""
フェーズ4: 動きのあった会社のIR・動きと注目銘柄の抽出 - メインファイル
"""

import logging
from datetime import datetime
from config import load_config, setup_logging
from hot_stock_collector import get_active_companies, identify_hot_stocks, link_news_to_stock

# フェーズ1のニュース要約・メール送信モジュールがあれば利用
try:
    from news_collector import NewsCollector
    from news_summarizer import NewsSummarizer
    from email_sender import EmailSender
    PHASE1_AVAILABLE = True
except ImportError:
    PHASE1_AVAILABLE = False
    print("警告: フェーズ1のモジュールが見つかりません。ニュース連携・メール送信は無効です。")

def main():
    config = load_config()
    setup_logging(config['log_level'])
    logger = logging.getLogger(__name__)
    logger.info("フェーズ4: 動きのあった会社・注目銘柄抽出を開始します")

    # ステップ1: 株価データ取得
    stock_data = get_active_companies(config['target_symbols'], days=config['hot_stock_days'])
    if not stock_data:
        logger.warning("株価データが取得できませんでした")
        return

    # ステップ2: 注目銘柄抽出
    hot_stocks = identify_hot_stocks(
        stock_data,
        volume_threshold=config['volume_threshold'],
        price_change_threshold=config['price_change_threshold']
    )
    if not hot_stocks:
        logger.info("注目銘柄はありませんでした")
        return
    logger.info(f"{len(hot_stocks)}件の注目銘柄を抽出")

    # ステップ3: ニュース連携（フェーズ1があれば）
    news_articles = []
    if PHASE1_AVAILABLE and config.get('openai_api_key'):
        news_collector = NewsCollector(config['openai_api_key'])
        news_articles = news_collector.get_market_news(max_articles=30)
        if news_articles:
            news_summarizer = NewsSummarizer(config['openai_api_key'])
            news_articles = news_summarizer.summarize_multiple_articles(news_articles)

    # ステップ4: 注目銘柄ごとに関連ニュースを抽出
    for stock in hot_stocks:
        symbol = stock['symbol']
        stock['related_news'] = link_news_to_stock(symbol, news_articles)

    # ステップ5: レポートメール送信（フェーズ1があれば）
    if PHASE1_AVAILABLE:
        email_sender = EmailSender(config['gmail_username'], config['gmail_app_password'])
        body = create_hot_stock_report_email(hot_stocks)
        subject = f"注目銘柄レポート - {datetime.now().strftime('%Y年%m月%d日')}"
        success = email_sender.send_email(subject, body, config['recipient_email'])
        if success:
            logger.info("メール送信が完了しました")
        else:
            logger.error("メール送信に失敗しました")
    else:
        print("--- 注目銘柄レポート ---")
        print(create_hot_stock_report_email(hot_stocks))
    logger.info("フェーズ4: 動きのあった会社・注目銘柄抽出が正常に完了しました")

def create_hot_stock_report_email(hot_stocks):
    today = datetime.now().strftime('%Y年%m月%d日')
    body = f"""
動きのあった会社・注目銘柄自動抽出レポート
{today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    for stock in hot_stocks:
        body += f"■ {stock['symbol']}\n"
        for reason in stock['reasons']:
            body += f"  - {reason}\n"
        if stock.get('related_news'):
            body += "  関連ニュース:\n"
            for news in stock['related_news']:
                body += f"    ・{news['title']}\n      {news['summary']}\n      {news['url']}\n"
        body += "\n"
    body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

※ 本レポートは自動生成です。投資判断は必ずご自身で行ってください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return body

if __name__ == "__main__":
    main() 