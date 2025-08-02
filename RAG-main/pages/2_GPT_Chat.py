
import streamlit as st
import os
import sys

# `src` ディレクトリへのパスを追加
# このファイルの場所（pages）から一つ上の階層（プロジェクトルート）に移動し、そこから `src` を指定
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, 'src'))

from gpt_chat_utils.gpt_client import GPTClient
from gpt_chat_utils.chat_manager import ChatManager
from gpt_chat_utils.save_manager import (
    save_chat_history, 
    convert_history_to_markdown,
    list_saved_chats,
    load_chat_history
)
from gpt_chat_utils.file_analyzer import extract_text_from_file
from datetime import datetime

st.set_page_config(page_title="GPTチャット", layout="wide")

def main():
    """チャットアプリケーションのメイン関数。"""
    st.title("GPT-4.1-mini チャット")

    # APIキーの確認
    if "OPENAI_API_KEY" not in os.environ:
        st.error("環境変数 `OPENAI_API_KEY` が設定されていません。")
        return

    try:
        gpt_client = GPTClient()
        chat_manager = ChatManager(session_state_key="gpt_chat_messages")
    except Exception as e:
        st.error(f"初期化中にエラーが発生しました: {e}")
        return

    # サイドバー
    with st.sidebar:
        st.header("ファイルアップロード")
        uploaded_file = st.file_uploader(
            "ファイルで知識を補強 (TXT, PDF, DOCX)", 
            type=['txt', 'pdf', 'docx']
        )
        if uploaded_file is not None:
            # 拡張子を取得
            file_extension = uploaded_file.name.split('.')[-1].lower()
            # テキストを抽出
            file_content = extract_text_from_file(uploaded_file, file_extension)
            
            if "エラーが発生しました" in file_content:
                st.error(file_content)
            else:
                # ファイル内容をセッション状態に保存
                st.session_state.uploaded_file_content = file_content
                st.success(f"「{uploaded_file.name}」を読み込みました。内容について質問できます。")

        st.header("モード設定")
        is_deep_think_mode = st.toggle("じっくり考えるモード", value=False)
        use_web_search = st.toggle("Web検索を有効にする", value=False)
        st.info("「じっくり考える」: より慎重で網羅的な回答を生成します。\n「Web検索」: 最新情報に関する質問に、AIが自律的にWebを参照して回答します。")

        st.header("会話の管理")

        # 保存ディレクトリ
        save_dir = os.path.join(project_root, 'saved_chats')

        # 会話の読み込み
        saved_chats = list_saved_chats(save_dir)
        if saved_chats:
            selected_chat = st.selectbox("保存した会話を選択", saved_chats)
            if st.button("この会話を読み込む"):
                filepath = os.path.join(save_dir, selected_chat)
                loaded_history = load_chat_history(filepath)
                chat_manager.history = loaded_history # ChatManagerのhistoryを直接更新
                st.rerun()
        else:
            st.info("保存された会話はありません。")


        # 会話の保存とダウンロード
        if st.button("現在の会話を保存 (JSON)"):
            if chat_manager.history:
                result = save_chat_history(chat_manager.history, save_dir=save_dir)
                st.success(result)
            else:
                st.warning("保存する会話がありません。")

        if chat_manager.history:
            markdown_data = convert_history_to_markdown(chat_manager.history)
            file_name = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            st.download_button(
                label="会話をダウンロード (MD)",
                data=markdown_data,
                file_name=file_name,
                mime="text/markdown",
            )

        st.header("操作")
        if st.button("現在の会話をクリア"):
            chat_manager.clear_history()
            # アップロードされたファイル情報もクリア
            if "uploaded_file_content" in st.session_state:
                del st.session_state.uploaded_file_content
            st.rerun()

    # 会話履歴の表示
    for message in chat_manager.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        chat_manager.add_message("user", prompt) # ユーザーメッセージをまず履歴に追加
        with st.chat_message("user"):
            st.markdown(prompt)

        # ファイルがアップロードされていれば、その内容をシステムメッセージとして追加
        messages_for_api = chat_manager.history.copy() # 更新された履歴をコピーして使用
        if st.session_state.get("uploaded_file_content"):
            file_content = st.session_state.get("uploaded_file_content")
            system_message = f"あなたはデータ分析アシスタントです。以下のファイル内容を元に、ユーザーの質問に答えてください。\n\n---\n{file_content}\n---"
            # 常に最新のファイル内容をシステムメッセージとして先頭に追加
            # （既存のシステムメッセージがあれば置き換える）
            if messages_for_api and messages_for_api[0]["role"] == "system":
                messages_for_api[0]["content"] = system_message
            else:
                messages_for_api.insert(0, {"role": "system", "content": system_message})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # モードに応じたパラメータを設定
                if is_deep_think_mode:
                    temperature = 0.1
                    max_output_tokens = 2048
                else:
                    temperature = 0.7
                    max_output_tokens = 512

                # Web検索ツールを有効にするか
                tools = [{"type": "web_search", "search_context_size": "medium"}] if use_web_search else None

                full_response = gpt_client.get_response(
                    messages_for_api, 
                    temperature=temperature,
                    max_output_tokens=max_output_tokens, # max_tokens を max_output_tokens に変更
                    tools=tools # ツール設定を渡す
                )
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"API呼び出し中にエラーが発生しました: {e}")
                full_response = f"エラー: {e}"

        chat_manager.add_message("assistant", full_response)
        # アシスタントの応答後に再実行して表示を更新
        st.rerun()

if __name__ == "__main__":
    main()

