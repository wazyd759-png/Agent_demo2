# 产品知识库 RAG 问答服务

基于 DashScope（通义千问）+ Chroma + CrossEncoder 重排的 RAG 问答系统，支持向量召回、语义重排、来源引用，提供 FastAPI 接口与前端问答页面。

## 线上地址

http://121.40.172.119/

## 技术栈

| 层 | 技术 |
|---|---|
| LLM | qwen-turbo（DashScope） |
| Embedding | text-embedding-v2（DashScope） |
| 向量库 | Chroma（cosine 空间） |
| 重排 | BAAI/bge-reranker-base |
| 服务 | FastAPI + Uvicorn |
| 部署 | Docker + Nginx 反向代理（阿里云 ECS） |

## 架构
浏览器 → Nginx :80 → 127.0.0.1:8000 → FastAPI /ask
→ RAGEngine
├─ 向量召回 top-7
├─ CrossEncoder 重排 top-3
└─ qwen-turbo 生成
→ {answer, sources[]}

## 核心流程

1. 文本切分（chunk_size=500，overlap=50）
2. DashScope Embedding 建 Chroma 向量库
3. 相似度召回 top-7
4. CrossEncoder 重排，取 top-3 作为上下文
5. qwen-turbo 生成回答
6. 返回 answer + sources（含重排 score 与原文）

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /health | 健康检查 |
| POST | /ask | `{question, top_k?}` → `{answer, sources[]}` |
| GET | /docs | Swagger UI |

## 评测结果

评测集：7 个知识库内问题 + 1 个知识库外问题

| 指标 | 结果 |
|---|---|
| 检索命中率 | 100.0% (7/7) |
| Faithfulness | 100.0% |
| 平均响应时间 | 1.46s |
| 来源引用完整率 | 100.0% |

运行环境：阿里云 ECS，2 核 2G，Ubuntu 22.04

## 部署

### 构建镜像

```bash
cd /opt/rag-app
docker build -t my-rag-app .