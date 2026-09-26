# AI 工程师 学习路线与技能树

## 岗位方向

AI 领域岗位大致分几类：

- 算法工程师：训练模型、优化效果。核心技能：ML、DL、论文。
- AI 应用工程师：用大模型做产品。核心技能：LLM、RAG、工程。
- 数据工程师：数据处理、管道。核心技能：SQL、Spark、ETL。
- MLOps：模型部署、运维。核心技能：Docker、K8s、监控。

本文重点：AI 应用工程师（大模型方向）。

## 技能树

### 1. 编程基础

- Python（必须熟练）：语法、数据结构、面向对象、异步编程、类型注解
- Linux（必须）：常用命令、Shell 脚本、进程、网络排查
- Git（必须）：基本操作、分支管理、PR 流程

### 2. 机器学习基础

- 线性回归、逻辑回归
- 决策树、随机森林
- 聚类（K-means）
- 降维（PCA）
- 评估指标（准确率、召回率、F1、AUC）
- 过拟合与正则化

### 3. 深度学习

- 神经网络基础
- 反向传播
- CNN、RNN、Transformer
- 优化器（SGD、Adam）
- 正则化（Dropout、BN）

### 4. 大模型

- Transformer 架构
- 预训练、微调
- Prompt Engineering
- RAG
- Agent
- 常见模型（GPT、LLaMA、Qwen）

### 5. 工程能力

- Web 框架：FastAPI、Flask
- 数据库：MySQL、PostgreSQL、Redis
- 向量库：Chroma、FAISS、Milvus
- 容器：Docker、Docker Compose
- 编排：Kubernetes（进阶）
- 云服务：阿里云、AWS

### 6. 工具链

- 深度学习：PyTorch、Hugging Face
- LLM 框架：LangChain、LlamaIndex
- 向量库：Chroma、FAISS
- 部署：FastAPI、vLLM、TGI
- 监控：Prometheus、Grafana

## 学习路线（6 个月）

### 第 1-2 月：基础

- Python 进阶
- Linux 基础
- 机器学习入门（吴恩达课程）
- 深度学习入门（李沐《动手学深度学习》）

### 第 3 月：大模型基础

- Transformer 原理
- Hugging Face 使用
- Prompt Engineering
- 跑通一个 LLaMA 推理

### 第 4 月：RAG

- 向量检索原理
- LangChain / LlamaIndex
- 做一个 RAG 问答系统
- 评测与优化

### 第 5 月：微调

- LoRA 原理
- 用 LLaMA-Factory 微调一个模型
- 数据集准备
- 评估微调效果

### 第 6 月：工程化

- FastAPI 服务化
- Docker 部署
- Nginx 反向代理
- 上线一个完整项目

## 项目建议

### 入门项目

1. 基于 RAG 的文档问答系统
2. 文本分类 / 情感分析
3. 简单的聊天机器人

### 进阶项目

1. 多轮对话 + 工具调用的 Agent
2. 垂直领域微调模型
3. 大规模 RAG 系统（百万文档）

### 加分项目

1. 开源贡献（LangChain、vLLM）
2. 技术博客
3. Kaggle 比赛

## 面试准备

### 基础

- ML / DL 核心概念
- Transformer 细节
- 常见优化器、损失函数

### 大模型

- RAG 流程与优化
- 微调方法对比
- Prompt Engineering
- 幻觉、对齐、评测

### 工程

- 系统设计
- 部署方案
- 性能优化

### 编程

- LeetCode 中等题
- 手写 Attention、K-means

## 常见误区

### 1. 只学不练

看了很多课，没做过项目。项目经验 > 课程证书。

### 2. 只调包不懂原理

会用 LangChain，但不知道 RAG 为什么这么设计。

### 3. 追新不扎实

天天追新模型，基础不牢。基础决定上限。

### 4. 不做工程化

模型训完就完，不会部署、不会服务化。工业界要的是能上线的系统。

### 5. 不看论文

只看博客和视频，不读原论文。论文是最权威的信息源。

## 资源推荐

### 课程

- 吴恩达《机器学习》
- 李沐《动手学深度学习》
- CS224N（NLP）
- Fast.ai

### 书籍

- 《深度学习》（花书）
- 《动手学深度学习》
- 《大模型应用开发》

### 论文

- Attention is All You Need
- BERT、GPT 系列
- LoRA、QLoRA
- RAG 综述

### 社区

- Hugging Face
- GitHub Trending
- 知乎、掘金
- arXiv

## 职业发展

### 初级（0-2 年）

- 能独立完成模块开发
- 熟悉常用工具
- 能读懂论文

### 中级（2-5 年）

- 能主导项目
- 能设计方案
- 能优化效果

### 高级（5+ 年）

- 能定技术方向
- 能带团队
- 有行业影响力

## 一句话总结

AI 工程师 = 算法能力 + 工程能力 + 业务理解

三者缺一不可。只懂算法是研究员，只懂工程是普通开发，能把算法落地成产品的才是 AI 工程师。

## 最后建议

- 动手 > 看书
- 项目 > 证书
- 深度 > 广度
- 坚持 > 突击
