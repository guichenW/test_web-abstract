# Abstract Web - 文本摘要系统

## 项目简介

Abstract Web是一个基于Flask的文本摘要Web应用，它使用了Text-Summarizer-Pytorch-Chinese模型提供中文文本摘要服务。该系统允许用户输入长文本，通过深度学习模型生成简洁的摘要，并支持多任务管理和历史记录查询。

## 项目结构

```
abstract_web/
├── data/                  # 数据存储目录
│   ├── all_user_dict_v3.pkl  # 用户数据缓存文件
│   ├── config.yaml        # 配置文件
│   ├── chats.db           # SQLite数据库文件
├── static/                # 静态资源
│   ├── css/               # 样式文件
│   │   ├── common.css     # 通用样式
│   │   └── modern.css     # 现代化UI样式
│   ├── js/                # JavaScript文件
│   │   ├── chatFunctions.js  # 聊天功能实现
│   │   ├── clickEventHandler.js # 点击事件处理
│   │   ├── modernUI.js    # UI交互增强
│   │   └── utils.js       # 工具函数
│   └── ...                # 其他静态资源
├── templates/             # HTML模板
│   └── index.html         # 主页模板
├── db.py                  # 数据库操作模块
├── log.txt                # 应用日志
├── requirements.txt       # 项目依赖
└── ts_main.py            # 应用入口文件
```

## 数据库结构与存储

### 表结构

项目使用SQLite3作为数据库，存储在`data/chats.db`文件中，包含以下表：

1. **chats表** - 存储摘要任务信息
   - chat_id: 任务ID (TEXT类型，主键)
   - name: 任务名称 (TEXT类型)
   - created_at: 创建时间 (TEXT类型，格式为YYYY-MM-DD HH:MM:SS)

2. **messages表** - 存储消息记录
   - id: 消息ID (INTEGER类型，主键，自增)
   - chat_id: 任务ID (TEXT类型，外键，关联chats表的chat_id)
   - role: 角色 (TEXT类型，user/assistant)
   - content: 消息内容 (TEXT类型)
   - timestamp: 时间戳 (TEXT类型，格式为YYYY-MM-DD HH:MM:SS)

### 数据交互与存储

数据库操作通过`db.py`模块实现，主要包括以下功能：

1. **连接管理**：
   - `get_db_connection()`: 获取数据库连接，设置行工厂为sqlite3.Row，使结果可以通过列名访问
   - `init_db()`: 初始化数据库，创建必要的表结构

2. **聊天管理**：
   - `get_chats()`: 获取所有聊天记录，按创建时间降序排列
   - `get_chat(chat_id)`: 获取指定ID的聊天信息
   - `create_chat(chat_id, name)`: 创建新聊天，生成创建时间
   - `update_chat_name(chat_id, new_name)`: 更新聊天名称
   - `delete_chat(chat_id)`: 删除聊天及其所有消息

3. **消息管理**：
   - `get_messages(chat_id)`: 获取指定聊天的所有消息，按时间戳排序
   - `add_message(chat_id, role, content)`: 添加新消息，生成时间戳

数据交互流程：
1. 前端通过AJAX请求与后端API交互
2. 后端API调用数据库操作函数处理数据
3. 数据库操作函数执行SQL语句并返回结果
4. 后端API将结果转换为JSON格式返回给前端
5. 前端解析JSON数据并更新UI

## 样式设计思路

项目采用现代化UI设计，主要通过`modern.css`实现，设计思路包括：

1. **CSS变量系统**：
   - 使用CSS变量定义颜色、边距、过渡时间等，便于统一管理和主题切换
   - 主色调采用蓝色系（--primary-color: #4a6fa5），辅助色采用绿色系（--secondary-color: #5cb85c）

2. **响应式布局**：
   - 使用Flexbox布局实现界面结构
   - 通过媒体查询适配不同屏幕尺寸（手机、平板、桌面）
   - 在小屏设备上自动调整布局，优化触摸区域大小

3. **交互动效**：
   - 使用CSS过渡效果增强用户体验
   - 为按钮、列表项等添加悬停和点击效果
   - 新消息添加淡入和滑动动画

4. **视觉层次**：
   - 使用阴影和边框区分不同区域
   - 通过颜色对比突出重要元素
   - 圆角设计（--border-radius: 8px）增加现代感

5. **移动优先**：
   - 针对触摸设备优化交互区域
   - 在小屏设备上使用抽屉式导航
   - 自适应输入区域和内容显示

## JavaScript功能实现

项目前端功能通过多个JavaScript模块实现：

### 1. chatFunctions.js - 核心聊天功能

- **任务管理**：
  - `loadChats()`: 加载任务列表，从服务器获取聊天数据
  - `selectChat(chatId)`: 切换当前任务，加载对应消息
  - `newChat(name)`: 创建新任务
  - `updateChatName(chatId, newName)`: 更新任务名称
  - `deleteChat(chatId)`: 删除任务及其消息

- **消息处理**：
  - `sendMessage()`: 发送用户输入的文本，调用摘要API
  - `appendMessage(message)`: 将消息添加到聊天界面，支持Markdown渲染
  - `saveWelcomeMessage()`: 保存欢迎消息到数据库

- **智能问候**：
  - 根据当前时间段（上午、下午、晚上）自动生成不同的问候语
  - 在新建聊天时显示时间相关的欢迎消息
  - 欢迎消息会持久化保存到消息历史中

### 2. clickEventHandler.js - 事件处理

- 绑定各种UI元素的点击事件
- 实现按钮交互、任务切换、消息发送等功能
- 处理移动端特有的交互（如侧边栏显示/隐藏）

### 3. modernUI.js - UI交互增强

- `enhanceUIWithAnimations()`: 为新消息添加动画效果
- `enhanceChatListInteraction()`: 改进任务列表项的交互体验
- `enhanceInputAreaInteraction()`: 优化输入区域的交互
- `enhanceResponsiveLayout()`: 实现响应式布局调整

### 4. utils.js - 工具函数

- `generateUUID()`: 生成唯一标识符
- `get_time_str(time)`: 格式化时间显示

## Flask后端实现

后端使用Flask框架实现，主要功能包括：

1. **路由设计**：
   - `/`: 主页路由，返回index.html模板
   - `/chats`: 任务管理API，支持GET（获取列表）和POST（创建新任务）
   - `/chats/<chat_id>`: 单个任务管理，支持PUT（更新）和DELETE（删除）
   - `/chats/<chat_id>/messages`: 获取指定任务的消息
   - `/abstract`: 文本摘要API，处理摘要请求并转发到Docker服务

2. **文本预处理**：
   - `preprocess_text(text)`: 处理用户输入文本
     - 去除特殊标点、全角空格和换行
     - 检查文本长度（至少15字）
     - 对过长文本进行智能截断（在标点处截断）

3. **API代理**：
   - 将处理后的文本发送到Docker中运行的摘要模型服务
   - 处理模型返回的结果，清理[UNK]标记
   - 将结果保存到数据库并返回给前端

4. **错误处理**：
   - 捕获并记录各种异常
   - 返回友好的错误信息给前端

5. **日志系统**：
   - 使用RotatingFileHandler实现日志轮转
   - 同时输出到控制台和文件
   - 记录请求、处理过程和错误信息

## 缓存机制实现

项目使用多层缓存机制提高性能：

1. **数据库缓存**：
   - SQLite数据库本身提供了基本的缓存功能
   - 通过索引优化查询性能

2. **前端缓存**：
   - 在JavaScript中使用chats对象缓存任务和消息数据
   - 切换任务时优先使用本地缓存数据，减少服务器请求
   - 仅在必要时（如初始加载、创建新任务）从服务器刷新数据

3. **会话状态管理**：
   - 使用currentChatId变量跟踪当前选中的任务
   - 在页面刷新后通过API重新加载最近的会话状态

4. **静态资源缓存**：
   - 使用外部CDN加载第三方库（如highlight.js）
   - 静态文件（CSS、JavaScript）由浏览器缓存

5. **数据持久化**：
   - 所有任务和消息数据持久化存储在SQLite数据库中
   - 通过pickle文件（all_user_dict_v3.pkl）实现用户数据的LRU缓存，提高频繁访问数据的响应速度

缓存机制的实现使系统在保持数据一致性的同时，显著提高了响应速度和用户体验。