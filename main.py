
import streamlit as st
import os
from openai import OpenAI
from save_manager import save_chat_history

def main():
    st.title("GPT-4.1-mini チャット")

    # APIキーの確認
    if "OPENAI_API_KEY" not in os.environ:
        st.error("環境変数 `OPENAI_API_KEY` が設定されていません。")
        return

    client = OpenAI()

    # 会話履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # サイドバー
    with st.sidebar:
        if st.button("会話をクリア"):
            st.session_state.messages = []
            st.rerun()

        if st.button("会話を保存"):
            if st.session_state.messages:
                result = save_chat_history(st.session_state.messages)
                st.success(result)
            else:
                st.warning("保存する会話がありません。")


    # 会話履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                stream = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                for chunk in stream:
                    full_response += (chunk.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"API呼び出し中にエラーが発生しました: {e}")
                full_response = f"エラー: {e}"

        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
