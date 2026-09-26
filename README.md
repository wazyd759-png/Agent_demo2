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

## 启动容器
docker run -d \
  --name rag-app \
  --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -e DASHSCOPE_API_KEY="sk-..." \
  -e DATA_PATH="/app/data/产品1.txt" \
  -e HF_HUB_OFFLINE=1 \
  -v /opt/rag-app/data:/app/data \
  -v /opt/rag-app/chroma_db1:/app/chroma_db1 \
  -v /opt/rag-app/.cache/huggingface:/app/.cache/huggingface \
  my-rag-app

## Nginx 反代
/etc/nginx/conf.d/rag-app.conf：
server {
    listen 80;
    server_name _;
    client_max_body_size 20m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
## 运维命令

docker logs rag-app | tail -30     # 看最近日志
docker restart rag-app             # 重启
nginx -t && systemctl reload nginx # 重载 Nginx

## 目录结构
text
.
├── main.py                 # FastAPI 服务
├── rag_engine.py           # RAG 核心引擎
├── static/index.html       # 前端页面
├── data/产品1.txt           # 知识库
├── evaluation/eval.py      # 评测脚本
├── deploy/                 # 部署配置
├── screenshots/            # 运行截图
└── Dockerfile


