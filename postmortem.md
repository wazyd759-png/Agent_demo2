
### 2. `D:\demo1\postmortem.md`（新建）

```markdown
# 上线复盘

## 目标

将本地 RAG 脚本容器化，部署到云服务器，通过 Nginx 提供公网访问，并做基础评测。

## 交付结果

- 线上地址：http://121.40.172.119/
- 评测：检索命中率 100%，Faithfulness 100%，平均响应 1.46s
- 架构：Docker + Nginx + FastAPI + Chroma

## 遇到的关键问题

### 1. Docker Hub 拉不动

**现象**：`failed to resolve source metadata ... i/o timeout`
**原因**：国内直连 Docker Hub 超时
**解决**：配 `/etc/docker/daemon.json` 的 `registry-mirrors`

### 2. apt/pip 慢

**现象**：`apt-get install` 卡 300+ 秒
**解决**：Dockerfile 里 `sed` 换清华源；pip 命令加 `-i https://pypi.tuna.tsinghua.edu.cn/simple`

### 3. torch 版本冲突

**现象**：`[transformers] Disabling PyTorch because PyTorch >= 2.5 is required but found 2.2.2`
**原因**：transformers 5.x 要求 torch >= 2.5
**解决**：`torch==2.5.1`

### 4. dashscope 中文 header bug

**现象**：`UnicodeEncodeError: 'latin-1' codec can't encode characters`
**原因**：dashscope 1.27.6 把中文参数塞进 HTTP header
**解决**：降到 `dashscope==1.26.4`

### 5. 挂载点无法删除

**现象**：`OSError: [Errno 16] Device or resource busy: '/app/chroma_db1'`
**原因**：`shutil.rmtree` 删挂载点本身
**解决**：改代码，只清空目录内容，保留目录

### 6. HuggingFace 联网超时

**现象**：`The handshake operation timed out ... processor_config.json`
**解决**：`-e HF_HUB_OFFLINE=1` 用本地缓存

### 7. Windows 换行符导致 sed 不匹配

**现象**：`sed 's/^dashscope$/.../'` 匹配不上
**原因**：文件里有 `\r`（`dashscope^M$`）
**解决**：`sed -i 's/\r$//' requirements.txt`

## 已知问题与改进方向

### 1. 检索无相似度阈值过滤

**现象**：知识库外问题"今天天气怎么样"仍召回 3 条 sources
**影响**：增加 token 消耗；理论上可能被无关上下文带偏
**改进**：用 `similarity_search_with_relevance_scores` + 阈值过滤

```python
results = self.db.similarity_search_with_relevance_scores(question, k=7)
retrieved_docs = [doc for doc, score in results if score >= 0.3]