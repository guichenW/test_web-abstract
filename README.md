# Abstract Web - 文本摘要系统

## 项目简介

Abstract Web是一个基于Flask的文本摘要Web应用，它使用了Text-Summarizer-Pytorch-Chinese模型提供中文文本摘要服务。该系统允许用户输入长文本，通过深度学习模型生成简洁的摘要，并支持多任务管理和历史记录查询。

## 运行方式

### 环境要求

- Python 3.x
- Flask
- SQLite3
- Docker (用于运行摘要模型服务)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

1. 首先启动Docker中的摘要模型服务：

```bash
# 在Text-Summarizer-Pytorch-Chinese目录下
docker-compose up -d
```

2. 启动Web应用：

```bash
python ts_main.py
```

应用将在 http://localhost:8058 上运行。

## 项目结构

```
abstract_web/
├── data/                  # 数据存储目录
│   ├── all_user_dict_v3.pkl  # 用户数据缓存文件
│   ├── config.yaml        # 配置文件
│   ├── running.log        # 运行日志
│   └── users.db           # SQLite数据库文件
├── static/                # 静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── ...                # 其他静态资源
├── templates/             # HTML模板
│   └── index.html         # 主页模板
├── db.py                  # 数据库操作模块
├── log.txt                # 应用日志
├── requirements.txt       # 项目依赖
└── ts_main.py            # 应用入口文件
```

## 数据存储方式

### 数据库结构

项目使用SQLite3作为数据库，存储在`data/users.db`文件中，包含以下表：

1. **users表** - 存储用户信息
   - id: 用户ID (主键)
   - username: 用户名 (唯一)
   - email: 邮箱
   - password: 密码

2. **chats表** - 存储摘要任务信息
   - chat_id: 任务ID (主键)
   - username: 用户名 (外键)
   - name: 任务名称
   - created_at: 创建时间

3. **messages表** - 存储消息记录
   - id: 消息ID (主键)
   - chat_id: 任务ID (外键)
   - role: 角色 (user/assistant)
   - content: 消息内容
   - timestamp: 时间戳

### 缓存机制

项目使用pickle文件(`all_user_dict_v3.pkl`)存储LRU缓存，用于提高频繁访问数据的响应速度。

## 技术原理

### 架构设计

系统采用前后端分离的架构：

1. **前端**：使用HTML、CSS和JavaScript构建用户界面，通过AJAX与后端通信。
2. **后端**：Flask框架提供Web服务，处理请求并与数据库交互。
3. **摘要服务**：使用Docker容器化的Text-Summarizer-Pytorch-Chinese模型提供摘要功能。

### 摘要模型

摘要功能基于Text-Summarizer-Pytorch-Chinese项目，该模型使用了：

- 基于LSTM的编码器-解码器架构
- 注意力机制 (Attention Mechanism)
- 指针生成网络 (Pointer-Generator Network)

模型通过Docker容器化部署，通过HTTP API提供服务。

### 数据流程

1. 用户在Web界面输入长文本
2. 前端通过AJAX发送请求到Flask后端
3. 后端对文本进行预处理（去除特殊标点、控制长度等）
4. 预处理后的文本发送到Docker中的摘要模型服务
5. 摘要模型生成摘要结果并返回
6. 后端将结果存储到数据库并返回给前端
7. 前端展示摘要结果

### 关键功能

1. **文本预处理**：去除特殊标点、控制文本长度
2. **任务管理**：创建、修改、删除摘要任务
3. **历史记录**：保存用户的所有摘要任务和结果
4. **数据持久化**：使用SQLite数据库存储用户数据和摘要记录

## API接口

### 主要接口

- `GET /` - 访问主页
- `GET /chats` - 获取所有任务列表
- `POST /chats` - 创建新任务
- `GET /chats/<chat_id>/messages` - 获取指定任务的所有消息
- `PUT /chats/<chat_id>` - 更新任务名称
- `DELETE /chats/<chat_id>` - 删除任务
- `POST /abstract` - 生成文本摘要

### 摘要模型API

- `POST http://172.17.0.16:5000/abstract` - Docker中的摘要服务接口