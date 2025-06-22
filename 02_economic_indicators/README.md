# フェーズ2: 経済指標の実績グラフ化

フェーズ1の機能に加えて、主要な経済指標の実績データを収集し、グラフとしてメール本文に添付または含める機能を追加します。

## 新機能

### 1. 経済指標データ収集
- **FRED API**: 米国の経済指標データ（GDP、CPI、失業率、政策金利など）
- **yfinance**: 株式市場データ（主要指数、個別銘柄）
- **手動データ**: 日本経済指標（サンプルデータ）

### 2. グラフ生成機能
- **個別指標グラフ**: 各経済指標の時系列推移
- **比較グラフ**: 複数指標の正規化比較
- **株価チャート**: 終値と出来高の表示
- **市場サマリー**: 主要指数の一覧表示

### 3. メール添付機能
- 生成されたグラフをメールに自動添付
- 経済指標の最新値をメール本文に含める

## セットアップ手順

### 1. 必要なライブラリのインストール

```bash
cd 02_economic_indicators
pip install -r requirements.txt
```

### 2. 追加APIキーの取得

#### FRED API（オプション）
1. [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html) でアカウントを作成
2. APIキーを取得
3. `.env`ファイルに設定

### 3. 環境変数の追加設定

`.env`ファイルに以下を追加：

```env
# フェーズ2の設定
FRED_API_KEY=your_fred_api_key_here

# グラフ設定
GRAPH_OUTPUT_DIR=graphs
GRAPH_DPI=300

# 経済指標設定
DEFAULT_INDICATORS=us_gdp,us_cpi,us_unemployment,us_interest_rate
DEFAULT_MARKET_INDICES=^DJI,^GSPC,^IXIC,^N225

# データ取得期間設定
ECONOMIC_DATA_DAYS=365
MARKET_DATA_DAYS=30
```

### 4. システムの実行

```bash
python main.py
```

## ファイル構成

```
02_economic_indicators/
├── main.py                    # メインファイル
├── config.py                  # 設定管理
├── economic_data_collector.py # 経済指標データ収集
├── graph_generator.py         # グラフ生成
├── requirements.txt           # 依存ライブラリ
└── README.md                 # このファイル
```

## 対応経済指標

### 米国指標（FRED API）
- **GDP**: 米国実質GDP（四半期）
- **CPI**: 米国消費者物価指数（月次）
- **失業率**: 米国失業率（月次）
- **政策金利**: 米国連邦基金金利（月次）

### 市場指数（yfinance）
- **^DJI**: ダウ・ジョーンズ工業平均
- **^GSPC**: S&P500
- **^IXIC**: ナスダック総合指数
- **^N225**: 日経平均株価

### 日本指標（サンプルデータ）
- **GDP**: 日本実質GDP（四半期）
- **CPI**: 日本消費者物価指数（月次）
- **失業率**: 日本失業率（月次）

## グラフの種類

### 1. 個別指標グラフ
- 時系列推移の表示
- マーカー付きの線グラフ
- グリッド表示

### 2. 比較グラフ
- 複数指標の正規化比較
- 相対的な動きの把握
- 凡例表示

### 3. 株価チャート
- 終値の推移
- 高安値幅の表示
- 出来高の棒グラフ

### 4. 市場サマリー
- 主要指数の一覧表示
- 複数のサブプロット
- 簡潔なレイアウト

## カスタマイズ

### 新しい経済指標の追加

`economic_data_collector.py`の`indicators`辞書に追加：

```python
'new_indicator': {
    'name': '新しい指標',
    'fred_id': 'FRED_ID',  # FRED APIの場合
    'source': 'manual',     # 手動データの場合
    'description': '説明'
}
```

### グラフスタイルの変更

`graph_generator.py`で以下の設定を変更：

```python
# グラフサイズ
fig, ax = plt.subplots(figsize=(12, 6))

# 色設定
sns.set_palette("husl")

# フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans']
```

## 注意事項

### API利用制限
- **FRED API**: 無料プランで1分120リクエスト
- **yfinance**: 利用制限なし（ただし過度な使用は避ける）

### データの信頼性
- 日本データは現在サンプルデータです
- 実際の使用では日本銀行や総務省統計局のAPIを使用してください

### グラフの品質
- 高解像度（300 DPI）で保存
- 日本語フォントの設定が必要
- 大量のグラフ生成時はメモリ使用量に注意

## トラブルシューティング

### よくあるエラー

1. **FRED APIエラー**
   - APIキーが正しく設定されているか確認
   - 利用制限に達していないか確認

2. **グラフ生成エラー**
   - matplotlibの日本語フォント設定を確認
   - 出力ディレクトリの権限を確認

3. **メール添付エラー**
   - ファイルサイズが大きすぎないか確認
   - ファイルパスが正しいか確認

## 次のステップ

フェーズ3では以下の機能を追加予定：
- 経済指標予想データの収集
- AIを活用した見通し分析
- より詳細な市場分析機能 