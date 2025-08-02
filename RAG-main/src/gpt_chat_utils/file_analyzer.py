import fitz  # PyMuPDF
import docx
from typing import IO

def extract_text_from_file(file: IO, file_extension: str) -> str:
    """アップロードされたファイルからテキストを抽出します。"""
    text = ""
    try:
        if file_extension == "txt":
            text = file.getvalue().decode("utf-8")
        elif file_extension == "pdf":
            with fitz.open(stream=file.read(), filetype="pdf") as doc:
                text = "".join(page.get_text() for page in doc)
        elif file_extension == "docx":
            doc = docx.Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"ファイルからのテキスト抽出中にエラーが発生しました: {e}"
    return text