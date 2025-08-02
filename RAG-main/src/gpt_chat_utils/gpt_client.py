from openai import OpenAI
from typing import List, Dict, Iterator, Any, Optional

class GPTClient:
    """OpenAI APIと対話するためのクライアント。"""

    def __init__(self, model: str = "gpt-4.1-mini"):
        """クライアントを初期化します。

        Args:
            model: 使用するモデル名。
        """
        self.client = OpenAI()
        self.model = model

    def get_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Responses APIから応答を取得します。"""
        try:
            # instructions と input を分離
            instructions = ""
            input_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    instructions = msg["content"]
                else:
                    input_messages.append(msg)

            # input は最後のユーザーメッセージ、または全会話履歴を渡す
            # Responses APIのinputはstringまたはrole-contentオブジェクトの配列
            # ここでは、全会話履歴をinputとして渡す
            # ただし、最後のユーザーメッセージのみをinputとして渡す方がWeb検索ツールとの相性が良い場合もある
            # 今回は、messages_for_apiが既に整形されているため、それをinputとして渡す
            # もしinputがstringのみを期待する場合は、最後のユーザーメッセージを抽出する必要がある
            # GPTの回答例ではinputがrole-contentオブジェクトの配列なので、それに従う

            params = {
                "model": self.model,
                "input": input_messages, # messages ではなく input を使用
            }
            if instructions:
                params["instructions"] = instructions
            if temperature is not None:
                params["temperature"] = temperature
            if max_output_tokens is not None:
                params["max_output_tokens"] = max_output_tokens
            if tools is not None:
                params["tools"] = tools

            response = self.client.responses.create(**params)
            return response.output_text

        except Exception as e:
            print(f"API呼び出しエラー: {e}")
            raise