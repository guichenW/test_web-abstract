import requests
from flask import Flask, render_template, request, jsonify
import re
import logging
from logging.handlers import RotatingFileHandler
import uuid
from db import init_db, get_chats, get_messages, create_chat, add_message, get_chat, update_chat_name, delete_chat

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

# 初始化数据库
init_db()

@app.route('/', methods=['GET'])
def index():
    logger.info("访问主页")
    return render_template('index.html')

@app.route('/chats', methods=['GET'])
def get_all_chats():
    """获取所有聊天"""
    try:
        chats_list = get_chats()
        return jsonify({"ok": True, "data": chats_list})
    except Exception as e:
        logger.error(f"获取聊天列表失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"获取聊天列表失败: {str(e)}"}), 500

@app.route('/chats/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    """获取指定聊天的所有消息"""
    try:
        messages_list = get_messages(chat_id)
        return jsonify({"ok": True, "data": messages_list})
    except Exception as e:
        logger.error(f"获取聊天消息失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"获取聊天消息失败: {str(e)}"}), 500

@app.route('/chats/<chat_id>/messages', methods=['POST'])
def add_chat_message(chat_id):
    """添加新消息到指定聊天"""
    try:
        body = request.json
        if not body or "role" not in body or "content" not in body:
            return jsonify({"ok": False, "errors": "缺少消息角色或内容"}), 400
        
        # 检查聊天是否存在
        chat = get_chat(chat_id)
        if not chat:
            return jsonify({"ok": False, "errors": "聊天不存在"}), 404
            
        # 添加消息
        message = add_message(chat_id, body["role"], body["content"])
        return jsonify({"ok": True, "data": message})
    except Exception as e:
        logger.error(f"添加聊天消息失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"添加聊天消息失败: {str(e)}"}), 500

@app.route('/chats', methods=['POST'])
def create_new_chat():
    """创建新聊天"""
    try:
        body = request.json
        if not body or "name" not in body:
            return jsonify({"ok": False, "errors": "缺少聊天名称"}), 400
        
        chat_id = f"chat-{uuid.uuid4().hex[:8]}"
        chat = create_chat(chat_id, body["name"])
        return jsonify({"ok": True, "data": chat})
    except Exception as e:
        logger.error(f"创建聊天失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"创建聊天失败: {str(e)}"}), 500

@app.route('/chats/<chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """更新聊天名称"""
    try:
        body = request.json
        if not body or "name" not in body:
            return jsonify({"ok": False, "errors": "缺少聊天名称"}), 400
        
        chat = update_chat_name(chat_id, body["name"])
        return jsonify({"ok": True, "data": chat})
    except Exception as e:
        logger.error(f"更新聊天名称失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"更新聊天名称失败: {str(e)}"}), 500

@app.route('/chats/<chat_id>', methods=['DELETE'])
def remove_chat(chat_id):
    """删除聊天"""
    try:
        result = delete_chat(chat_id)
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        logger.error(f"删除聊天失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"删除聊天失败: {str(e)}"}), 500

@app.route('/abstract', methods=['POST'])
def abstract_proxy():
    try:
        body = request.json
        logger.info(f"收到请求: {body}")
        if not body or "text" not in body:
            logger.warning("请求格式错误：缺少 text 字段")
            return jsonify({"ok": False, "errors": "请输入文本"}), 400
            
        # 获取聊天ID，如果没有则使用默认ID
        chat_id = body.get("chat_id", "default")
        
        # 检查聊天是否存在，如果不存在则创建
        chat = get_chat(chat_id)
        if not chat:
            chat = create_chat(chat_id, "默认任务")
            
        # 保存用户消息到数据库
        add_message(chat_id, "user", body["text"])
        
        processed_text, error = preprocess_text(body["text"])
        if error:
            logger.info(f"文本预处理失败: {error}")
            error_message = add_message(chat_id, "assistant", error)
            return jsonify({"ok": False, "errors": error, "message_id": error_message["id"]}), 400
            
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
            # 保存AI回复到数据库
            message = add_message(chat_id, "assistant", result["data"])
            result["message_id"] = message["id"]
        else:
            # 保存错误信息到数据库
            error_msg = result.get("errors", "未知错误")
            message = add_message(chat_id, "assistant", f"错误: {error_msg}")
            result["message_id"] = message["id"]
            
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        logger.error(f"Docker 请求失败: {str(e)}")
        return jsonify({"ok": False, "errors": f"Docker 服务错误: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}")
        return jsonify({"ok": False, "errors": f"服务器错误: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8058, debug=True)