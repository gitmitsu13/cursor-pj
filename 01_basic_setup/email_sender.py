"""
Gmail送信モジュール
要約されたニュースをGmailで送信します
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailSender:
    """Gmail送信クラス"""
    
    def __init__(self, username: str, app_password: str):
        """
        初期化
        
        Args:
            username (str): Gmailユーザー名
            app_password (str): Googleアカウントのアプリパスワード
        """
        self.username = username
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_email(self, subject: str, body: str, to_address: str, 
                   attachments: Optional[List[str]] = None) -> bool:
        """
        メールを送信します
        
        Args:
            subject (str): 件名
            body (str): 本文
            to_address (str): 送信先アドレス
            attachments (List[str], optional): 添付ファイルのパスリスト
            
        Returns:
            bool: 送信成功時True
        """
        try:
            # メールメッセージの作成
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_address
            msg['Subject'] = subject
            
            # 本文を追加
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添付ファイルを追加
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                        logger.info(f"添付ファイルを追加: {file_path}")
                    except Exception as e:
                        logger.error(f"添付ファイルの追加でエラー: {e}")
            
            # SMTPサーバーに接続して送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.app_password)
                server.send_message(msg)
            
            logger.info(f"メール送信完了: {to_address}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Gmail認証エラー。アプリパスワードを確認してください。")
            return False
        except Exception as e:
            logger.error(f"メール送信でエラー: {e}")
            return False
    
    def create_market_report_email(self, daily_summary: str, 
                                  summarized_articles: List[dict]) -> str:
        """
        市場レポート用のメール本文を作成します
        
        Args:
            daily_summary (str): 日次サマリー
            summarized_articles (List[dict]): 要約済み記事のリスト
            
        Returns:
            str: メール本文
        """
        today = datetime.now().strftime('%Y年%m月%d日')
        
        email_body = f"""
市場情報自動収集・分析システム - 日次レポート
{today}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【本日の市場動向サマリー】
{daily_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【主要ニュース詳細】

"""
        
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
※ 投資判断は必ずご自身で行ってください。
※ 本システムは投資助言を行うものではありません。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return email_body 