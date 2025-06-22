"""
経済指標データ収集モジュール
主要な経済指標の実績データを収集します
"""

import pandas as pd
import numpy as np
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from fredapi import Fred
import pandas_datareader.data as web

logger = logging.getLogger(__name__)

class EconomicDataCollector:
    """経済指標データ収集クラス"""
    
    def __init__(self, fred_api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            fred_api_key (str, optional): FRED APIキー
        """
        self.fred_api_key = fred_api_key
        if fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        
        # 主要経済指標の定義
        self.indicators = {
            'us_gdp': {
                'name': '米国GDP',
                'fred_id': 'GDP',
                'description': '米国実質GDP（四半期）'
            },
            'us_cpi': {
                'name': '米国消費者物価指数',
                'fred_id': 'CPIAUCSL',
                'description': '米国消費者物価指数（月次）'
            },
            'us_unemployment': {
                'name': '米国失業率',
                'fred_id': 'UNRATE',
                'description': '米国失業率（月次）'
            },
            'us_interest_rate': {
                'name': '米国政策金利',
                'fred_id': 'FEDFUNDS',
                'description': '米国連邦基金金利（月次）'
            },
            'japan_gdp': {
                'name': '日本GDP',
                'source': 'manual',
                'description': '日本実質GDP（四半期）'
            },
            'japan_cpi': {
                'name': '日本消費者物価指数',
                'source': 'manual',
                'description': '日本消費者物価指数（月次）'
            },
            'japan_unemployment': {
                'name': '日本失業率',
                'source': 'manual',
                'description': '日本失業率（月次）'
            }
        }
    
    def get_economic_indicators(self, indicator_names: List[str], 
                               start_date: str = None, 
                               end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        経済指標データを取得します
        
        Args:
            indicator_names (List[str]): 取得する指標名のリスト
            start_date (str): 開始日（YYYY-MM-DD形式）
            end_date (str): 終了日（YYYY-MM-DD形式）
            
        Returns:
            Dict[str, pd.DataFrame]: 指標名をキーとしたデータフレームの辞書
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        results = {}
        
        for indicator_name in indicator_names:
            if indicator_name not in self.indicators:
                logger.warning(f"未知の指標: {indicator_name}")
                continue
            
            try:
                indicator_info = self.indicators[indicator_name]
                
                if 'fred_id' in indicator_info:
                    # FREDからデータ取得
                    data = self._get_fred_data(indicator_info['fred_id'], start_date, end_date)
                elif indicator_info['source'] == 'manual':
                    # 手動データ取得（日本データなど）
                    data = self._get_manual_data(indicator_name, start_date, end_date)
                else:
                    logger.warning(f"データソースが不明: {indicator_name}")
                    continue
                
                if data is not None and not data.empty:
                    results[indicator_name] = data
                    logger.info(f"{indicator_info['name']} データ取得完了: {len(data)} 件")
                else:
                    logger.warning(f"{indicator_info['name']} データが取得できませんでした")
                    
            except Exception as e:
                logger.error(f"{indicator_name} データ取得でエラー: {e}")
        
        return results
    
    def _get_fred_data(self, fred_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        FREDからデータを取得します
        
        Args:
            fred_id (str): FREDの指標ID
            start_date (str): 開始日
            end_date (str): 終了日
            
        Returns:
            pd.DataFrame: 時系列データ
        """
        try:
            if not self.fred_api_key:
                logger.warning("FRED APIキーが設定されていません")
                return pd.DataFrame()
            
            data = self.fred.get_series(fred_id, start_date, end_date)
            df = pd.DataFrame(data)
            df.columns = ['value']
            df.index.name = 'date'
            return df
            
        except Exception as e:
            logger.error(f"FREDデータ取得でエラー: {e}")
            return pd.DataFrame()
    
    def _get_manual_data(self, indicator_name: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        手動でデータを取得します（日本データなど）
        
        Args:
            indicator_name (str): 指標名
            start_date (str): 開始日
            end_date (str): 終了日
            
        Returns:
            pd.DataFrame: 時系列データ
        """
        try:
            # ここでは簡易的な実装として、サンプルデータを生成
            # 実際の実装では、日本銀行や総務省統計局のAPIを使用
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 月次データを生成
            dates = pd.date_range(start=start_dt, end=end_dt, freq='M')
            
            if 'gdp' in indicator_name:
                # GDPデータ（四半期）
                dates = pd.date_range(start=start_dt, end=end_dt, freq='Q')
                values = np.random.normal(100, 2, len(dates))  # サンプルデータ
            elif 'cpi' in indicator_name:
                # CPIデータ（月次）
                values = np.random.normal(100, 1, len(dates))  # サンプルデータ
            elif 'unemployment' in indicator_name:
                # 失業率データ（月次）
                values = np.random.normal(3.0, 0.5, len(dates))  # サンプルデータ
            else:
                values = np.random.normal(0, 1, len(dates))
            
            df = pd.DataFrame({
                'date': dates,
                'value': values
            }).set_index('date')
            
            logger.info(f"サンプルデータを生成: {indicator_name}")
            return df
            
        except Exception as e:
            logger.error(f"手動データ取得でエラー: {e}")
            return pd.DataFrame()
    
    def get_stock_market_data(self, symbols: List[str], 
                             start_date: str = None, 
                             end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        株式市場データを取得します
        
        Args:
            symbols (List[str]): 銘柄シンボルのリスト
            start_date (str): 開始日
            end_date (str): 終了日
            
        Returns:
            Dict[str, pd.DataFrame]: 銘柄シンボルをキーとしたデータフレームの辞書
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        results = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)
                
                if not data.empty:
                    # 必要な列のみを選択
                    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
                    results[symbol] = data
                    logger.info(f"{symbol} データ取得完了: {len(data)} 件")
                else:
                    logger.warning(f"{symbol} データが取得できませんでした")
                    
            except Exception as e:
                logger.error(f"{symbol} データ取得でエラー: {e}")
        
        return results
    
    def get_market_indices(self, indices: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        主要市場指数を取得します
        
        Args:
            indices (List[str]): 指数のリスト
            
        Returns:
            Dict[str, pd.DataFrame]: 指数名をキーとしたデータフレームの辞書
        """
        if indices is None:
            indices = ['^DJI', '^GSPC', '^IXIC', '^N225']  # ダウ、S&P500、ナスダック、日経平均
        
        return self.get_stock_market_data(indices) 