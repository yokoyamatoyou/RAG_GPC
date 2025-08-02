import streamlit as st
from typing import List, Dict, Any

class ChatManager:
    """Streamlitセッション状態を使用してチャット履歴を管理します。"""

    def __init__(self, session_state_key: str = "messages"):
        """マネージャーを初期化します。

        Args:
            session_state_key: 履歴を保存するためのセッション状態キー。
        """
        self.session_state_key = session_state_key
        if self.session_state_key not in st.session_state:
            st.session_state[self.session_state_key] = []

    @property
    def history(self) -> List[Dict[str, str]]:
        """現在のチャット履歴を取得します。"""
        return st.session_state[self.session_state_key]

    @history.setter
    def history(self, new_history: List[Dict[str, str]]) -> None:
        """チャット履歴を新しい内容で上書きします。"""
        st.session_state[self.session_state_key] = new_history

    def add_message(self, role: str, content: str) -> None:
        """チャット履歴にメッセージを追加します。

        Args:
            role: メッセージの役割（例: "user", "assistant"）。
            content: メッセージの内容。
        """
        # historyプロパティ経由で現在のリストを取得して追加
        current_history = self.history
        current_history.append({"role": role, "content": content})
        self.history = current_history # セッターを呼び出して更新

    def clear_history(self) -> None:
        """チャット履歴をクリアします。"""
        self.history = [] # セッター経由でクリア