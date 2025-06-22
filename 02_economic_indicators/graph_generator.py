"""
グラフ生成モジュール
経済指標データをグラフ化します
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

logger = logging.getLogger(__name__)

class GraphGenerator:
    """グラフ生成クラス"""
    
    def __init__(self, output_dir: str = "graphs"):
        """
        初期化
        
        Args:
            output_dir (str): グラフ保存ディレクトリ
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        
        # グラフのスタイル設定
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def _ensure_output_dir(self):
        """出力ディレクトリを作成"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"出力ディレクトリを作成: {self.output_dir}")
    
    def generate_indicator_graph(self, data_frame: pd.DataFrame, 
                                indicator_name: str, 
                                title: str = None,
                                filename: str = None) -> str:
        """
        経済指標のグラフを生成します
        
        Args:
            data_frame (pd.DataFrame): 時系列データ
            indicator_name (str): 指標名
            title (str): グラフタイトル
            filename (str): 保存ファイル名
            
        Returns:
            str: 保存されたファイルのパス
        """
        try:
            if data_frame.empty:
                logger.warning(f"{indicator_name} データが空です")
                return ""
            
            # グラフの作成
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # データのプロット
            ax.plot(data_frame.index, data_frame['value'], linewidth=2, marker='o', markersize=4)
            
            # タイトルの設定
            if title is None:
                title = f"{indicator_name} 推移"
            ax.set_title(title, fontsize=16, fontweight='bold')
            
            # 軸ラベルの設定
            ax.set_xlabel('日付', fontsize=12)
            ax.set_ylabel('値', fontsize=12)
            
            # グリッドの設定
            ax.grid(True, alpha=0.3)
            
            # x軸の日付フォーマット
            ax.tick_params(axis='x', rotation=45)
            
            # レイアウトの調整
            plt.tight_layout()
            
            # ファイル名の生成
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{indicator_name}_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # グラフの保存
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"グラフを保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"グラフ生成でエラー: {e}")
            return ""
    
    def generate_stock_price_graph(self, data_frame: pd.DataFrame, 
                                  symbol: str,
                                  filename: str = None) -> str:
        """
        株価チャートを生成します
        
        Args:
            data_frame (pd.DataFrame): 株価データ
            symbol (str): 銘柄シンボル
            filename (str): 保存ファイル名
            
        Returns:
            str: 保存されたファイルのパス
        """
        try:
            if data_frame.empty:
                logger.warning(f"{symbol} データが空です")
                return ""
            
            # グラフの作成
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # 株価チャート
            ax1.plot(data_frame.index, data_frame['Close'], linewidth=2, label='終値')
            ax1.fill_between(data_frame.index, data_frame['Low'], data_frame['High'], 
                           alpha=0.3, label='高安値幅')
            
            ax1.set_title(f'{symbol} 株価チャート', fontsize=16, fontweight='bold')
            ax1.set_ylabel('株価', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 出来高チャート
            ax2.bar(data_frame.index, data_frame['Volume'], alpha=0.7, color='orange')
            ax2.set_title('出来高', fontsize=12)
            ax2.set_xlabel('日付', fontsize=12)
            ax2.set_ylabel('出来高', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            # x軸の日付フォーマット
            ax2.tick_params(axis='x', rotation=45)
            
            # レイアウトの調整
            plt.tight_layout()
            
            # ファイル名の生成
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{symbol}_stock_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # グラフの保存
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"株価チャートを保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"株価チャート生成でエラー: {e}")
            return ""
    
    def generate_comparison_graph(self, data_dict: Dict[str, pd.DataFrame], 
                                 title: str = "経済指標比較",
                                 filename: str = None) -> str:
        """
        複数の指標を比較するグラフを生成します
        
        Args:
            data_dict (Dict[str, pd.DataFrame]): 指標名をキーとしたデータの辞書
            title (str): グラフタイトル
            filename (str): 保存ファイル名
            
        Returns:
            str: 保存されたファイルのパス
        """
        try:
            if not data_dict:
                logger.warning("比較データがありません")
                return ""
            
            # グラフの作成
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # 各指標をプロット
            for indicator_name, data in data_dict.items():
                if not data.empty:
                    # データを正規化（比較しやすくするため）
                    normalized_data = (data['value'] - data['value'].mean()) / data['value'].std()
                    ax.plot(data.index, normalized_data, linewidth=2, label=indicator_name, marker='o', markersize=3)
            
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('日付', fontsize=12)
            ax.set_ylabel('正規化された値', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # x軸の日付フォーマット
            ax.tick_params(axis='x', rotation=45)
            
            # レイアウトの調整
            plt.tight_layout()
            
            # ファイル名の生成
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"comparison_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # グラフの保存
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"比較グラフを保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"比較グラフ生成でエラー: {e}")
            return ""
    
    def generate_market_summary_graph(self, market_data: Dict[str, pd.DataFrame],
                                     filename: str = None) -> str:
        """
        市場サマリーグラフを生成します
        
        Args:
            market_data (Dict[str, pd.DataFrame]): 市場データ
            filename (str): 保存ファイル名
            
        Returns:
            str: 保存されたファイルのパス
        """
        try:
            if not market_data:
                logger.warning("市場データがありません")
                return ""
            
            # サブプロットの数を決定
            n_plots = len(market_data)
            cols = min(2, n_plots)
            rows = (n_plots + cols - 1) // cols
            
            fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
            if n_plots == 1:
                axes = [axes]
            elif rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            # 各市場指数をプロット
            for i, (symbol, data) in enumerate(market_data.items()):
                if i < len(axes):
                    ax = axes[i]
                    
                    # 終値の推移
                    ax.plot(data.index, data['Close'], linewidth=2)
                    ax.set_title(f'{symbol} 終値推移', fontsize=12, fontweight='bold')
                    ax.set_ylabel('価格', fontsize=10)
                    ax.grid(True, alpha=0.3)
                    ax.tick_params(axis='x', rotation=45)
            
            # 未使用のサブプロットを非表示
            for i in range(n_plots, len(axes)):
                axes[i].set_visible(False)
            
            # レイアウトの調整
            plt.tight_layout()
            
            # ファイル名の生成
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"market_summary_{timestamp}.png"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # グラフの保存
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"市場サマリーグラフを保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"市場サマリーグラフ生成でエラー: {e}")
            return "" 