"""
フェーズ2: 経済指標の実績グラフ化 - メインファイル
経済指標データの収集、グラフ生成、メール送信を行います
"""

import logging
import sys
import os
from datetime import datetime, timedelta

# 親ディレクトリをパスに追加（フェーズ1のモジュールを使用するため）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_config, setup_logging
from economic_data_collector import EconomicDataCollector
from graph_generator import GraphGenerator

# フェーズ1のモジュールをインポート
try:
    from news_collector import NewsCollector
    from news_summarizer import NewsSummarizer
    from email_sender import EmailSender
    PHASE1_AVAILABLE = True
except ImportError:
    PHASE1_AVAILABLE = False
    print("警告: フェーズ1のモジュールが見つかりません。ニュース機能は無効になります。")

def main():
    """メイン処理"""
    try:
        # 設定の読み込み
        config = load_config()
        
        # ログ設定
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)
        
        logger.info("フェーズ2: 経済指標の実績グラフ化を開始します")
        
        # データ収集期間の設定
        end_date = datetime.now()
        economic_start_date = (end_date - timedelta(days=config['economic_data_days'])).strftime('%Y-%m-%d')
        market_start_date = (end_date - timedelta(days=config['market_data_days'])).strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # ステップ1: 経済指標データの収集
        logger.info("ステップ1: 経済指標データの収集を開始")
        data_collector = EconomicDataCollector(config.get('fred_api_key'))
        
        # 経済指標データの取得
        economic_data = data_collector.get_economic_indicators(
            config['default_indicators'],
            start_date=economic_start_date,
            end_date=end_date_str
        )
        
        if not economic_data:
            logger.warning("経済指標データが取得できませんでした")
            return
        
        logger.info(f"{len(economic_data)} 件の経済指標データを収集しました")
        
        # ステップ2: 市場指数データの収集
        logger.info("ステップ2: 市場指数データの収集を開始")
        market_data = data_collector.get_market_indices(config['default_market_indices'])
        
        if not market_data:
            logger.warning("市場指数データが取得できませんでした")
        else:
            logger.info(f"{len(market_data)} 件の市場指数データを収集しました")
        
        # ステップ3: グラフの生成
        logger.info("ステップ3: グラフの生成を開始")
        graph_generator = GraphGenerator(config['graph_output_dir'])
        
        generated_graphs = []
        
        # 経済指標の個別グラフを生成
        for indicator_name, data in economic_data.items():
            try:
                graph_path = graph_generator.generate_indicator_graph(
                    data, indicator_name, 
                    title=f"{indicator_name} 推移"
                )
                if graph_path:
                    generated_graphs.append(graph_path)
            except Exception as e:
                logger.error(f"{indicator_name} グラフ生成でエラー: {e}")
        
        # 経済指標の比較グラフを生成
        if len(economic_data) > 1:
            try:
                comparison_graph = graph_generator.generate_comparison_graph(
                    economic_data, "経済指標比較"
                )
                if comparison_graph:
                    generated_graphs.append(comparison_graph)
            except Exception as e:
                logger.error(f"比較グラフ生成でエラー: {e}")
        
        # 市場指数のサマリーグラフを生成
        if market_data:
            try:
                market_summary_graph = graph_generator.generate_market_summary_graph(market_data)
                if market_summary_graph:
                    generated_graphs.append(market_summary_graph)
            except Exception as e:
                logger.error(f"市場サマリーグラフ生成でエラー: {e}")
        
        logger.info(f"{len(generated_graphs)} 件のグラフを生成しました")
        
        # ステップ4: フェーズ1の機能と統合（利用可能な場合）
        if PHASE1_AVAILABLE and config.get('news_api_key'):
            logger.info("ステップ4: フェーズ1の機能と統合")
            
            # ニュース収集と要約
            news_collector = NewsCollector(config['news_api_key'])
            articles = news_collector.get_market_news(max_articles=config['max_news_articles'])
            
            if articles:
                news_summarizer = NewsSummarizer(config['openai_api_key'])
                summarized_articles = news_summarizer.summarize_multiple_articles(articles)
                daily_summary = news_summarizer.generate_daily_summary(summarized_articles)
                
                # メール送信
                email_sender = EmailSender(config['gmail_username'], config['gmail_app_password'])
                
                # グラフ付きメール本文の作成
                email_body = create_graph_report_email(
                    daily_summary, summarized_articles, economic_data, market_data
                )
                
                # 件名の作成
                today = datetime.now().strftime('%Y年%m月%d日')
                subject = f"経済指標レポート - {today}"
                
                # メール送信（グラフを添付）
                success = email_sender.send_email(
                    subject=subject,
                    body=email_body,
                    to_address=config['recipient_email'],
                    attachments=generated_graphs
                )
                
                if success:
                    logger.info("グラフ付きメール送信が完了しました")
                else:
                    logger.error("メール送信に失敗しました")
            else:
                logger.warning("ニュース記事が取得できませんでした")
        else:
            logger.info("フェーズ1の機能は利用できません。グラフのみ生成しました。")
        
        logger.info("フェーズ2: 経済指標の実績グラフ化が正常に完了しました")
        
    except Exception as e:
        logger.error(f"システム実行中にエラーが発生しました: {e}")
        raise

def create_graph_report_email(daily_summary: str, summarized_articles: list, 
                             economic_data: dict, market_data: dict) -> str:
    """
    グラフ付きレポート用のメール本文を作成します
    
    Args:
        daily_summary (str): 日次サマリー
        summarized_articles (list): 要約済み記事のリスト
        economic_data (dict): 経済指標データ
        market_data (dict): 市場データ
        
    Returns:
        str: メール本文
    """
    today = datetime.now().strftime('%Y年%m月%d日')
    
    email_body = f"""
経済指標自動収集・分析システム - 日次レポート（グラフ付き）
{today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【本日の市場動向サマリー】
{daily_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【経済指標サマリー】

"""
    
    # 経済指標の最新値を追加
    for indicator_name, data in economic_data.items():
        if not data.empty:
            latest_value = data['value'].iloc[-1]
            latest_date = data.index[-1].strftime('%Y年%m月%d日')
            email_body += f"• {indicator_name}: {latest_value:.2f} ({latest_date})\n"
    
    email_body += "\n【主要ニュース詳細】\n"
    
    for i, article in enumerate(summarized_articles[:5], 1):
        email_body += f"""
{i}. {article.get('title', 'Unknown')}
    出典: {article.get('source', 'Unknown')}
    公開日: {article.get('published_at', 'Unknown')}
    
    要約:
    {article.get('summary', 'No summary')}
    
    詳細: {article.get('url', 'No URL')}
    
"""
    
    email_body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

※ このレポートは自動生成されています。
※ 添付グラフをご確認ください。
※ 投資判断は必ずご自身で行ってください。
※ 本システムは投資助言を行うものではありません。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return email_body

if __name__ == "__main__":
    main() 