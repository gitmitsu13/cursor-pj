"""
フェーズ3: ニュース内容を踏まえた経済指標見通しの考察 - メインファイル
"""

import logging
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_config, setup_logging
from forecast_collector import get_economic_forecasts
from outlook_analyzer import OutlookAnalyzer

# フェーズ1・2のモジュールをインポート（存在すれば）
try:
    from news_collector import NewsCollector
    from news_summarizer import NewsSummarizer
    from economic_data_collector import EconomicDataCollector
    from graph_generator import GraphGenerator
    from email_sender import EmailSender
    PHASE1_2_AVAILABLE = True
except ImportError:
    PHASE1_2_AVAILABLE = False
    print("警告: フェーズ1・2のモジュールが見つかりません。基本機能のみ動作します。")

def main():
    try:
        config = load_config()
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)
        logger.info("フェーズ3: 経済指標見通し考察を開始します")

        # データ収集期間の設定
        end_date = datetime.now()
        start_date = (end_date - timedelta(days=config['economic_data_days'])).strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # ステップ1: 実績データ収集
        if PHASE1_2_AVAILABLE:
            data_collector = EconomicDataCollector(config.get('fred_api_key'))
            actual_data = data_collector.get_economic_indicators(
                config['default_indicators'],
                start_date=start_date,
                end_date=end_date_str
            )
        else:
            actual_data = {}

        # ステップ2: 予想データ収集
        forecast_data = {}
        for indicator in config['default_indicators']:
            forecast = get_economic_forecasts(indicator)
            if forecast is not None:
                forecast_data[indicator] = forecast

        # ステップ3: ニュース要約取得
        if PHASE1_2_AVAILABLE and config.get('news_api_key'):
            news_collector = NewsCollector(config['news_api_key'])
            articles = news_collector.get_market_news(max_articles=config['max_news_articles'])
            if articles:
                news_summarizer = NewsSummarizer(config['openai_api_key'])
                summarized_articles = news_summarizer.summarize_multiple_articles(articles)
                news_summary = news_summarizer.generate_daily_summary(summarized_articles)
            else:
                news_summary = "本日は重要なマーケットニュースはありませんでした。"
        else:
            news_summary = "（ニュース要約機能は無効です）"

        # ステップ4: AIによる見通し考察
        outlook_analyzer = OutlookAnalyzer(config['openai_api_key'])
        # 実績・予想データは直近値のみを要約して渡す
        actual_summary = {k: v['value'].iloc[-1] if not v.empty else None for k, v in actual_data.items()}
        forecast_summary = {k: v['forecast'].iloc[-1] if not v.empty else None for k, v in forecast_data.items()}
        outlook_text = outlook_analyzer.analyze_outlook(news_summary, actual_summary, forecast_summary)

        # ステップ5: レポートメール送信（フェーズ2の機能があればグラフも添付）
        if PHASE1_2_AVAILABLE:
            email_sender = EmailSender(config['gmail_username'], config['gmail_app_password'])
            body = create_outlook_report_email(news_summary, actual_summary, forecast_summary, outlook_text)
            subject = f"経済指標見通しレポート - {datetime.now().strftime('%Y年%m月%d日')}"
            # グラフ生成（省略可）
            attachments = []
            if 'graph_output_dir' in config:
                graph_generator = GraphGenerator(config['graph_output_dir'])
                for k, v in actual_data.items():
                    if not v.empty:
                        path = graph_generator.generate_indicator_graph(v, k)
                        if path:
                            attachments.append(path)
            success = email_sender.send_email(subject, body, config['recipient_email'], attachments=attachments)
            if success:
                logger.info("メール送信が完了しました")
            else:
                logger.error("メール送信に失敗しました")
        else:
            print("--- AIによる経済指標見通し考察 ---")
            print(outlook_text)
        logger.info("フェーズ3: 経済指標見通し考察が正常に完了しました")
    except Exception as e:
        logger.error(f"システム実行中にエラーが発生しました: {e}")
        raise

def create_outlook_report_email(news_summary, actual_summary, forecast_summary, outlook_text):
    today = datetime.now().strftime('%Y年%m月%d日')
    body = f"""
経済指標見通し自動分析レポート
{today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【本日のニュース要約】
{news_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【経済指標 実績サマリー】
"""
    for k, v in actual_summary.items():
        body += f"・{k}: {v}\n"
    body += "\n【経済指標 予想サマリー】\n"
    for k, v in forecast_summary.items():
        body += f"・{k}: {v}\n"
    body += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【AIによる見通し考察】
{outlook_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

※ このAIによる考察は必ず人間が最終確認し、必要に応じて修正してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return body

if __name__ == "__main__":
    main() 