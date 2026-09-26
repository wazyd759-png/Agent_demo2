# RAG 技术：检索增强生成

## 什么是 RAG

RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合检索和生成的技术：

1. 用户提问
2. 从知识库检索相关文档
3. 把文档作为上下文，让 LLM 生成答案

核心价值：让 LLM 回答训练数据之外的问题，减少幻觉。

## 为什么需要 RAG

### LLM 的局限

- 知识截止到训练时间
- 无法访问私有数据
- 容易产生幻觉
- 微调成本高

### RAG 的优势

- 知识实时更新
- 可接入私有数据
- 答案可溯源（返回来源）
- 成本低

## 基本流程

文档 → 切分 → Embedding → 向量库
用户问题 → Embedding → 向量检索 → 相关文档
上下文 + 问题 → LLM → 答案

### 关键步骤

- 加载：读取文档（PDF、Markdown、HTML）
- 切分：分成合适大小的块
- Embedding：转成向量
- 存储：存入向量库
- 检索：相似度搜索
- 重排：用 CrossEncoder 精排
- 生成：拼接上下文，LLM 生成

## 切分策略

### 固定长度切分

按字符数切，简单但可能切断语义。

### 递归切分

按分隔符递归切：`["\\n\\n", "。", "？", "！", "；", "，", "、", "\\n", " ", ""]`

LangChain 的 RecursiveCharacterTextSplitter 就是这种。

### 按标题切分

Markdown 用 MarkdownHeaderTextSplitter，按 `#` / `##` 切。

### 关键参数

- chunk_size：500-1000 字符
- chunk_overlap：50-200 字符，防止语义断裂

## Embedding 模型

### 常见选择

- text-embedding-v2：1536 维，DashScope，中文好
- text-embedding-3-small：1536 维，OpenAI
- bge-large-zh：1024 维，智源，中文
- m3e-base：768 维，中文

### 选型建议

- 中文场景：DashScope、bge
- 英文场景：OpenAI
- 本地部署：bge、m3e

## 向量库

### 常见选择

- Chroma：轻量，适合原型
- FAISS：Facebook，性能高
- Milvus：分布式，适合大规模
- Qdrant：Rust 编写，性能好
- Pinecone：云服务，托管

### 相似度度量

- 余弦相似度：最常用
- 欧氏距离：L2
- 内积：IP

## 重排（Rerank）

### 为什么需要

向量检索是粗排，可能召回不相关的内容。重排用更强的模型精排。

### CrossEncoder

把问题和文档一起输入模型，输出相关性分数。

优点：准确。
缺点：慢（每对都要算一次）。

### 常见模型

- BAAI/bge-reranker-base
- BAAI/bge-reranker-large
- Cohere Rerank

## 高级技巧

### 1. 混合检索

向量检索 + BM25 关键词检索，互补。

### 2. 查询改写

用 LLM 把用户问题改写成多个查询，提高召回。

### 3. HyDE

让 LLM 生成假设答案，用答案去检索。

### 4. 上下文压缩

用 LLM 压缩检索到的文档，减少 token。

### 5. 多路召回

从多个知识库或多种检索方式召回，合并去重。

## 评测指标

- 检索命中率：检索到的文档是否包含答案
- Faithfulness：答案是否基于上下文，没编造
- 答案相关性：答案是否回答了问题
- 上下文精度：检索到的文档有多少是相关的
- 响应时间：端到端延迟

## 常见问题

### 1. 检索不到相关内容

- 检查切分粒度
- 换更好的 Embedding
- 加混合检索
- 查询改写

### 2. 答案有幻觉

- 提示词强调“只根据上下文回答”
- 加相似度阈值过滤
- 用更强的 LLM

### 3. 响应慢

- 减少 top_k
- 用更小的重排模型
- 缓存常见问题

## 面试常问

1. RAG 和微调的区别？
2. 切分粒度怎么定？
3. 为什么需要重排？
4. 怎么评测 RAG 系统？
5. 如何减少幻觉？

## 延伸阅读

- LangChain 官方文档
- LlamaIndex 官方文档
- RAG 综述论文
