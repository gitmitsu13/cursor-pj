"""
動きのあった会社・注目銘柄抽出モジュール
yfinanceで株価・出来高・企業情報を取得し、注目銘柄を抽出します
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def get_active_companies(symbols: List[str], days: int = 5) -> Dict[str, pd.DataFrame]:
    """
    指定した銘柄リストから株価・出来高等のデータを取得
    ※ WebスクレイピングでTDnet/EDINETを利用する場合はrobots.txt・利用規約を必ず確認
    Args:
        symbols (List[str]): 銘柄シンボルリスト（例: ['7203.T', '6758.T', 'AAPL', 'MSFT']）
        days (int): 取得日数
    Returns:
        Dict[str, pd.DataFrame]: シンボルごとの株価データ
    """
    results = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{days}d")
            if not df.empty:
                results[symbol] = df
                logger.info(f"{symbol} データ取得: {len(df)}件")
            else:
                logger.warning(f"{symbol} データが取得できませんでした")
        except Exception as e:
            logger.error(f"{symbol} データ取得でエラー: {e}")
    return results

def identify_hot_stocks(stock_data: Dict[str, pd.DataFrame], volume_threshold: float = 2.0, price_change_threshold: float = 0.05) -> List[Dict]:
    """
    出来高急増・株価変動率が大きい銘柄を抽出
    Args:
        stock_data (Dict[str, pd.DataFrame]): シンボルごとの株価データ
        volume_threshold (float): 出来高急増の判定基準（平均の何倍か）
        price_change_threshold (float): 株価変動率の判定基準（例: 0.05=5%）
    Returns:
        List[Dict]: 注目銘柄リスト（シンボル・理由等）
    """
    hot_stocks = []
    for symbol, df in stock_data.items():
        try:
            if len(df) < 2:
                continue
            # 出来高急増判定
            avg_volume = df['Volume'][:-1].mean()
            last_volume = df['Volume'].iloc[-1]
            volume_ratio = last_volume / avg_volume if avg_volume > 0 else 0
            # 株価変動率判定
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
            reasons = []
            if volume_ratio >= volume_threshold:
                reasons.append(f"出来高が過去平均の{volume_ratio:.1f}倍")
            if abs(price_change) >= price_change_threshold:
                reasons.append(f"株価が前日比{price_change*100:.1f}%変動")
            if reasons:
                hot_stocks.append({
                    'symbol': symbol,
                    'volume_ratio': volume_ratio,
                    'price_change': price_change,
                    'reasons': reasons
                })
        except Exception as e:
            logger.error(f"{symbol} 注目銘柄判定でエラー: {e}")
    return hot_stocks

def link_news_to_stock(stock_symbol: str, news_articles: List[Dict]) -> List[Dict]:
    """
    銘柄に関連するニュースを抽出し、要約を付与
    Args:
        stock_symbol (str): 銘柄シンボル
        news_articles (List[Dict]): ニュース記事リスト
    Returns:
        List[Dict]: 関連ニュース（タイトル・要約・URL等）
    """
    related = []
    for article in news_articles:
        title = article.get('title', '')
        if stock_symbol.split('.')[0] in title or stock_symbol in title:
            related.append({
                'title': title,
                'summary': article.get('summary', ''),
                'url': article.get('url', '')
            })
    return related

# TDnet/EDINETのWebスクレイピング注意
# ※ 公式APIやRSSがない場合、robots.txt・利用規約を必ず確認し、許可された範囲でのみ取得してください
# ※ 企業名・銘柄コードによるフィルタリングも推奨 