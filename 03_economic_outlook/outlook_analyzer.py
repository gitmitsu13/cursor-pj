"""
経済指標見通し考察モジュール
AI（OpenAI API等）を活用して今後の見通しを自動生成します
※ 生成された考察は必ず人間が最終確認・修正してください
"""

import openai
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class OutlookAnalyzer:
    """経済指標見通し考察クラス"""
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name
        openai.api_key = api_key

    def analyze_outlook(self, news_summary: str, actual_indicators: Dict[str, Any], forecast_indicators: Dict[str, Any], model_name: Optional[str] = None) -> str:
        """
        ニュースサマリ・実績・予想データをもとにAIで今後の見通しを考察します
        ※ 生成された内容は必ず人間が最終確認し、必要に応じて修正してください
        Args:
            news_summary (str): ニュース要約
            actual_indicators (dict): 実績データ
            forecast_indicators (dict): 予想データ
            model_name (str, optional): 使用するAIモデル名
        Returns:
            str: AIによる見通し考察
        """
        try:
            prompt = f"""
以下の情報をもとに、今後の経済指標の見通しと市場への影響を考察してください。

【ニュース要約】
{news_summary}

【経済指標の実績データ】
{actual_indicators}

【経済指標の予想データ】
{forecast_indicators}

要件：
- 重要な要素を簡潔にまとめる
- 市場へのインパクトを明確に述べる
- 投資家が参考にできる示唆を含める
- 3-5段落程度、日本語で
- ※このAIによる考察は必ず人間が最終確認し、必要に応じて修正してください

考察：
"""
            response = openai.ChatCompletion.create(
                model=model_name or self.model_name,
                messages=[
                    {"role": "system", "content": "あなたは金融・経済の専門アナリストです。経済指標とニュースをもとに今後の見通しを考察してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.4
            )
            outlook = response.choices[0].message.content.strip()
            logger.info("AIによる見通し考察生成完了")
            return outlook
        except Exception as e:
            logger.error(f"見通し考察生成でエラー: {e}")
            return "AIによる見通し考察生成中にエラーが発生しました。" 