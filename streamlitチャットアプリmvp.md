# Streamlit×GPT-4.1mini チャットアプリ MVP & 拡張 開発指示書（完全版）

## ■ 共通開発ルール・要件
- Python 3.11
- Streamlitで実装
- 外部ライブラリは自由に使用可能（openai, streamlit, pandas, PyPDF2, requests, beautifulsoup4, matplotlib等）
- モデルは常に "gpt-4.1-mini" 固定
- OpenAI APIキーは環境変数（例: "OPENAI_API_KEY"）からのみ取得。明示的なUI入力・コード埋め込み不可
- すべてOpenAI APIドキュメント規約（レートリミット・stream引数・ファイルアップロードの扱い等）を順守
- モジュール分割、型ヒント・docstring・例外処理必須
- 各機能単体ごとにテスト用関数またはダミーデータで動作確認
- エラーやAPI異常・未設定時はUIでユーザーにわかりやすくメッセージ
- requirements.txt必須

---

## ■ フェーズ1：チャットUI・API連携
### [機能・要件]
- Streamlit UI：入力欄、送信ボタン、会話表示欄のみ
- エンターキー or 送信ボタンで送信可能
- GPT-4.1-mini（model="gpt-4.1-mini"）を `stream=True` で呼び出し、ストリーミングレスポンスを1文字ずつ描画
- APIキーは常に環境変数から自動取得。未設定ならエラー表示
- 通信エラー、レートリミット等もすべてUIで通知
- main.pyのみ、後のモジュール化を考慮した関数設計
- [テスト] APIレスポンスのストリーミング性・UI反映・エラー発生時の動作

---

## ■ フェーズ2：会話履歴・記憶管理
### [機能・要件]
- 会話履歴はstreamlit.session_state["chat_history"]で管理し、毎回初期化しないこと
- ユーザー/AI区別（role="user" or "assistant"）で表示（吹き出し/色分け推奨）
- 履歴は時系列で上→下へ描画
- 会話履歴クリアボタン、クリア時も状態/表示一貫
- [テスト] セッション中の履歴保存・再描画時消失しないか

---

## ■ フェーズ3：ローカル保存・自動タイトル
### [機能・要件]
- 「会話保存」ボタン設置。履歴をjsonでローカル保存
- ファイル名："日付_自動タイトル.json" 形式（例: 20250802_製品QAチャット.json）
- タイトル自動生成：履歴冒頭数文をopenai.ChatCompletionで"タイトルを20文字以内で要約"指示を与えて取得
- 保存成功/失敗は明示表示。失敗時はエラー理由も表示
- save_manager.pyに保存・タイトル生成を関数化。main.pyから呼び出す
- [テスト] 保存ファイル内容・タイトル生成の妥当性

---

## ■ フェーズ4：モジュール分割・型ヒント・例外
### [機能・要件]
- gpt_client.py：GPT-4.1-mini用APIラッパー（stream=True必須）
- chat_manager.py：履歴・状態管理
- save_manager.py：保存・タイトル生成・エラー処理
- main.py：UI本体
- 各関数には型ヒント、docstring、try/except例外処理。異常時はmain.py UIに詳細を伝播
- importの形でmain.py→各モジュール呼び出し
- モジュール単体でのテスト・サンプル関数も設置

---

## ■ フェーズ5：拡張機能（必須要件レベルで詳細に設計）

### 5-1. 「じっくり考える」モード
- ユーザーが「じっくり考える」ON/OFF切替可
- ON時はAPI呼び出し時にtemperature=0.1, max_tokens=2048などを指定（通常: temperature=0.7, max_tokens=512等）
- 切替UI、現在のモードを明示。履歴・保存にもモード情報を記録
- [テスト] レスポンス生成の違い・モード切替UI

### 5-2. ファイルアップロード&分析
- ユーザーがtxt/csv/pdf等アップロード可
- 内容はopenai.ChatCompletion("あなたはデータ分析アシスタント...ファイル内容を要約しQA可能に...")で渡す
- テキスト以外は必要に応じてPyPDF2やpandas等で解析→要約・QAプロンプトへ変換
- 複数ファイル対応、履歴/保存にもアップロード記録
- [テスト] 各ファイル形式・大容量時の挙動

### 5-3. URL参照・Web検索（OpenAI規約順守）
- ユーザーがURL/クエリ入力→"ネット参照"ボタンで外部情報取得
- requests/beautifulsoup4等で取得（robots.txt順守・タイムアウト設定）
- 得られたテキストをopenai.ChatCompletionでQA/要約可能に
- OpenAI APIのfunction callingまたはtools(web-search)機能活用（もし利用可能な場合はOpenAI公式Web-Search tool/ Retrieval toolも積極利用）
- レート制限・不正URL・失敗時も明示
- [テスト] 検索精度・応答速度

### 5-4. HTMLインフォグラフィック生成
- ユーザーが「グラフ/図作成指示」を入力→AIにHTML/CSS/JS形式で生成させ、UIでsandbox表示
- コードインジェクション防止のため、iframeやst.components.v1.htmlでサンドボックス必須
- matplotlib等で画像グラフ生成も選択可
- 出力例は保存履歴に付記
- [テスト] 表示崩れ・セキュリティ

### 5-5. その他OpenAI API規則順守（全体に適用）
- レートリミット、API呼び出し頻度調整、function calling, tools, assistant等の新機能は随時追従
- 長文分割・多ファイル/大規模履歴時は自動で複数APIコール・要約等で効率化
- アップロードファイルやWEB取得データは一時保存し、個人情報等はセッション終了時削除（規約順守）
- ログやエラーはdebug.log等に出力（ユーザー個人データ保護にも配慮）

---

## ■ 最終ファイル構成（例）
```
/project-root
  /src
    gpt_client.py         # OpenAI API専用ラッパー
    chat_manager.py       # 履歴管理
    save_manager.py       # 保存/タイトル生成/エラー処理
    file_analyzer.py      # ファイルアップロード解析
    web_tools.py          # URL取得・Web検索
    infograph.py          # HTML/グラフ生成
    main.py               # Streamlit UI本体
  /static
    /saved_chats          # 履歴保存
    /uploaded_files       # 一時保存
  requirements.txt
  README.md
  .env（OPENAI_API_KEY管理用、gitignore推奨）
```

---

## ■ 開発進行
- 各フェーズごとに、最低限のUI・機能が完成したら必ず動作テスト→エラー時はその内容を出力・修正し再テスト
- コード内コメント・ドキュメント多めに
- 途中でOpenAI API仕様変更やエラー時は速やかに規則再確認
- main.pyは全機能UIを統合・各機能import形式

---

### （各モジュールAPI設計やプロンプト例、コード雛形も必要に応じて随時追加できます）

