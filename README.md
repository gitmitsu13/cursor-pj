# 市場情報自動収集・分析システム

マーケットニュース、経済指標、企業IR情報を自動収集・分析し、日次で要約レポートをGmailで指定の宛先に送信するシステムです。

## 機能概要

### フェーズ1: マーケットニュースの自動要約とGmail送信システム ✅
- NewsAPIを使用したマーケットニュースの自動収集
- OpenAI APIを使用したニュース記事の自動要約
- Gmailでの日次レポート自動送信

### フェーズ2: 経済指標の実績グラフ化 (予定)
- 主要経済指標データの収集
- グラフ生成とメール添付機能

### フェーズ3: ニュース内容を踏まえた経済指標見通しの考察 (予定)
- 経済指標予想データの収集
- AIを活用した見通し分析

### フェーズ4: 動きのあった会社のIR・動きと注目銘柄の抽出 (予定)
- 株価データの収集と分析
- 注目銘柄の自動抽出

## セットアップ手順

### 1. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. APIキーの取得と設定

#### NewsAPI
1. [NewsAPI](https://newsapi.org/) でアカウントを作成
2. APIキーを取得
3. `.env`ファイルに設定

#### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/) でアカウントを作成
2. APIキーを取得
3. `.env`ファイルに設定

### 3. Gmail設定

#### 方法1: アプリパスワードを使用（推奨）
1. Googleアカウントで2段階認証を有効化
2. アプリパスワードを生成
3. `.env`ファイルに設定

#### 方法2: Gmail APIを使用
1. Google Cloud ConsoleでGmail APIを有効化
2. OAuth2.0認証情報を作成
3. `credentials.json`ファイルをダウンロード
4. `python setup_gmail.py`を実行

### 4. 環境変数の設定

`env_example.txt`を参考に`.env`ファイルを作成：

```bash
cp env_example.txt .env
```

`.env`ファイルを編集して実際の値を設定：

```env
NEWS_API_KEY=your_news_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GMAIL_USERNAME=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient@example.com
```

### 5. システムの実行

```bash
python main.py
```

## ファイル構成

```
MyProject/
├── main.py                 # メインファイル
├── config.py              # 設定管理
├── news_collector.py      # ニュース収集
├── news_summarizer.py     # ニュース要約
├── email_sender.py        # メール送信
├── setup_gmail.py         # Gmail API設定
├── requirements.txt       # 依存ライブラリ
├── env_example.txt        # 環境変数設定例
└── README.md             # このファイル
```

## 注意事項

### API利用制限
- NewsAPI: 無料プランで1日1,000リクエスト
- OpenAI API: 使用量に応じて課金
- Gmail API: 1日1,000,000,000クォータ

### セキュリティ
- APIキーは絶対にGitにコミットしないでください
- `.env`ファイルは`.gitignore`に追加してください
- 本番環境では適切なセキュリティ対策を実施してください

### 法的注意
- Webスクレイピングを行う場合は、対象サイトの利用規約を確認してください
- 投資助言を行うものではありません
- 生成された内容は必ず人間の目で確認してください

## トラブルシューティング

### よくあるエラー

1. **APIキーエラー**
   - 環境変数が正しく設定されているか確認
   - APIキーが有効か確認

2. **Gmail認証エラー**
   - アプリパスワードが正しく設定されているか確認
   - 2段階認証が有効になっているか確認

3. **ニュース取得エラー**
   - NewsAPIの利用制限に達していないか確認
   - インターネット接続を確認

## 今後の開発予定

- [ ] フェーズ2: 経済指標グラフ化機能
- [ ] フェーズ3: 経済指標見通し分析
- [ ] フェーズ4: 注目銘柄抽出機能
- [ ] Web UIの追加
- [ ] データベース連携
- [ ] バックテスト機能

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 