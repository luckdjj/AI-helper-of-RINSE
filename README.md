# AI Talking - RAG 知识库问答系统

基于 LangChain + Chroma 构建的 RAG (Retrieval Augmented Generation) 问答系统，支持知识库管理和智能对话。

## 项目结构

```
team/
├── app_aq.py                 # Streamlit 聊天界面
├── app_file_uploader.py       # Streamlit 知识库上传界面
├── config_data.py            # 配置文件
├── file_history_store.py      # 聊天历史记录存储
├── knowedge_base.py        # 知识库服务
├── rag.py                  # RAG 核心服务
├── Vector_stores.py         # 向量存储服务
├── data/                  # 知识库原始数据
│   ├── 尺码推荐.txt
│   ├── 洗涤养护.txt
│   └── 颜色选择.txt
└── __pycache__/            # Python 缓存目录
```

## 技术栈

| 类别       | 技术                                 |
| ---------- | ------------------------------------ |
| 向量数据库 | Chroma                               |
| Embedding  | 阿里云 DashScope (text-embedding-v4) |
| 大语言模型 | 阿里云 Qwen (qwen3-max)              |
| Web 框架   | Streamlit                            |
| 框架       | LangChain                            |

## 快速开始

### 1. 安装依赖

```bash
pip install langchain langchain-community langchain-chroma langchain-core
pip install streamlit
pip install dashscope
```

### 2. 配置 API Key

在环境变量中设置阿里云 DashScope API Key：

```bash
set DASHSCOPE_API_KEY=your_api_key
```

### 3. 启动应用

**聊天界面：**

```bash
streamlit run f:/AI_study/team/app_aq.py
```

**知识库上传界面：**

```bash
streamlit run f:/AI_study/team/app_file_uploader.py
```

## 功能说明

### 知识库管理 (`app_file_uploader.py`)

- 支持上传 txt、pdf、docx 文件
- 自动进行文本分块和向量化
- 基于 MD5 去重，避免重复上传
- 支持批量处理（单文件模式）

### 智能问答 (`app_aq.py`)

- 基于 RAG 从知识库检索相关上下文
- 结合历史对话记录进行上下文感知对话
- 流式输出交互体验
- 支持自定义会话 session

## 配置说明 (`config_data.py`)

| 参数                 | 说明             | 默认值            |
| -------------------- | ---------------- | ----------------- |
| collection_name      | Chroma 集合名称  | rag               |
| persist_directory    | 向量库持久化路径 | ./chroma_db       |
| chunk_size           | 文本分块大小     | 1000              |
| chunk_overlap        | 分块重叠字符数   | 100               |
| embedding_model_name | Embedding 模型   | text-embedding-v4 |
| chat_model_name      | 对话模型         | qwen3-max         |

## 核心模块

### RagService (`rag.py`)

- 初始化向量存储和 LLM
- 构建 RAG Chain：检索 → 格式化 → Prompt → LLM → 输出
- 支持会话历史管理

### knowledgeBaseService (`knowedge_base.py`)

- 文档上传和向量化
- MD5 去重机制
- 元数据管理（文件名、创建时间、操作者）

### VectorStoreService (`Vector_stores.py`)

- Chroma 向量库封装
- 相似度检索（返回 Top-K）

### FileChatMessageHistory (`file_history_store.py`)

- JSON 文件存储对话历史
- Session 隔离，安全验证
- 原子写入（先写临时文件再重命名）

## 数据流向

```
用户输入 → 检索器 → Chroma 向量库 (Top-K 相关文档)
                    ↓
格式化上下文 + 历史记录 + 用户问题
                    ↓
LLM (Qwen3-Max) → 流式输出
```

## 注意事项

1. **编码问题**: 上传文件需为 UTF-8 编码
2. **Session 隔离**: 每个 session_id 对应独立的历史记录文件
3. **去重机制**: 相同内容的文件会跳过重复上传
4. **Streamlit 重跑**: 页面交互会导致整个脚本重新执行，需用 session_state 保持服务对象
