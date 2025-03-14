import requests
from flask import Flask, render_template, request, jsonify
import re
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)



# 设置日志格式
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 设置文件日志
file_handler = RotatingFileHandler("log.txt", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# 设置控制台日志
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# 获取 logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Docker 接口地址
ABSTRACT_API_URL = "http://172.17.0.16:5000/abstract"

# 特殊标点，包括中文标点和全角空格
SPECIAL_PUNCTUATION = r'[~`@#$^*]'
PUNCTUATION_FOR_TRUNCATION = r'[。！？.,!?]'

def preprocess_text(text):
    """预处理文本：去除特殊标点、全角空格、换行并处理长度"""
    # 先去除全角空格和换行（扩展可能的空格字符）
    text_no_fullwidth = re.sub(r'[\u3000\s\n]', '', text)  # 包括 \u3000 和其他空白字符
    # 再去除特殊标点
    cleaned_text = re.sub(SPECIAL_PUNCTUATION, '', text_no_fullwidth)
    logger.info(f"原始文本: {text}")
    logger.info(f"去除全角空格和换行后: {text_no_fullwidth}")
    logger.info(f"去除特殊标点后: {cleaned_text}")
    if len(cleaned_text) < 15:
        return None, "文本过短，请输入至少15字的内容"
    if len(cleaned_text) > 80:
        truncated = cleaned_text[:80]
        remaining = cleaned_text[80:]
        match = re.search(PUNCTUATION_FOR_TRUNCATION, remaining)
        if match:
            truncated += remaining[:match.end()]
        else:
            truncated = cleaned_text[:80]
        logger.info(f"截断后文本: {truncated}")
        return truncated, None
    return cleaned_text, None

@app.route('/', methods=['GET'])
def index():
    logger.info("访问主页")
    return render_template('index.html')

@app.route('/abstract', methods=['POST'])
def abstract_proxy():
    try:
        body = request.json
        logger.info(f"收到请求: {body}")
        if not body or "text" not in body:
            logger.warning("请求格式错误：缺少 text 字段")
            return jsonify({"ok": False, "errors": "请输入文本"}), 400
        processed_text, error = preprocess_text(body["text"])
        if error:
            logger.info(f"文本预处理失败: {error}")
            return jsonify({"ok": False, "errors": error}), 400
        payload = {"text": processed_text}
        logger.info(f"发送到 Docker 的 payload: {payload}")
        response = requests.post(
            ABSTRACT_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Docker 返回结果: {result}")
        if result.get("ok", False) and "data" in result:
            result["data"] = re.sub(r'\s*\[UNK\]\s*', ' ', result["data"]).strip()
            logger.info(f"清理 [UNK] 后结果: {result['data']}")
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Docker 请求失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"Docker 服务错误: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}")
        return jsonify({"ok": False, "errors": f"服务器错误: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8058, debug=True)