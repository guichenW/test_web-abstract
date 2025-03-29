import sqlite3
import os
import time
import logging

# 获取logger
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/chats.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 设置行工厂，使结果可以通过列名访问
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建聊天表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            name TEXT,
            created_at TEXT
        );
    ''')
    
    # 创建消息表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
        );
    ''')
    
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

# 聊天相关操作
def get_chats():
    """获取所有聊天"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats ORDER BY created_at DESC')
    chats = cursor.fetchall()
    conn.close()
    return [dict(chat) for chat in chats]

def get_chat(chat_id):
    """获取单个聊天信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
    chat = cursor.fetchone()
    conn.close()
    return dict(chat) if chat else None

def create_chat(chat_id, name):
    """创建新聊天"""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        'INSERT INTO chats (chat_id, name, created_at) VALUES (?, ?, ?)',
        (chat_id, name, created_at)
    )
    
    conn.commit()
    conn.close()
    logger.info(f"创建新聊天: {chat_id}, 名称: {name}")
    return {'chat_id': chat_id, 'name': name, 'created_at': created_at}

def update_chat_name(chat_id, new_name):
    """更新聊天名称"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE chats SET name = ? WHERE chat_id = ?',
        (new_name, chat_id)
    )
    
    conn.commit()
    conn.close()
    logger.info(f"更新聊天名称: {chat_id}, 新名称: {new_name}")
    return {'chat_id': chat_id, 'name': new_name}

def delete_chat(chat_id):
    """删除聊天及其所有消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先删除聊天的所有消息
    cursor.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    
    # 再删除聊天本身
    cursor.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
    
    conn.commit()
    conn.close()
    logger.info(f"删除聊天: {chat_id}")
    return {'chat_id': chat_id, 'deleted': True}

# 消息相关操作
def get_messages(chat_id):
    """获取聊天的所有消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp', (chat_id,))
    messages = cursor.fetchall()
    conn.close()
    return [dict(msg) for msg in messages]

def add_message(chat_id, role, content):
    """添加新消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        'INSERT INTO messages (chat_id, role, content, timestamp) VALUES (?, ?, ?, ?)',
        (chat_id, role, content, timestamp)
    )
    
    # 获取插入的消息ID
    message_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    logger.info(f"添加新消息到聊天: {chat_id}, 角色: {role}, ID: {message_id}")
    return {
        'id': message_id,
        'chat_id': chat_id,
        'role': role,
        'content': content,
        'timestamp': timestamp
    }

# 初始化数据库
if __name__ == "__main__":
    init_db()