# 大模型基础：Transformer 架构

## 概述

Transformer 是 2017 年 Google 在论文《Attention is All You Need》中提出的架构，是现代大语言模型（GPT、BERT、LLaMA 等）的基础。

## 核心思想

### 1. 抛弃循环，用注意力

RNN/LSTM 必须按顺序处理序列，无法并行。Transformer 用自注意力机制，可以并行处理整个序列。

### 2. 注意力机制

核心公式：

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

- Q（Query）：查询
- K（Key）：键
- V（Value）：值
- $d_k$：维度，除以 $\sqrt{d_k}$ 防止梯度消失

### 3. 多头注意力

把 Q、K、V 拆成多个头，每个头独立计算注意力，最后拼接。

好处：让模型从不同子空间学习不同的关注模式。

## 整体结构

### Encoder

输入 → Embedding + 位置编码 → [多头自注意力 → Add & Norm → FFN → Add & Norm] × N → 输出

### Decoder

输入 → Embedding + 位置编码 → [Masked 多头自注意力 → Add & Norm → 交叉注意力 → Add & Norm → FFN → Add & Norm] × N → 输出

### 关键组件

- 位置编码：注入位置信息
- 残差连接：防止梯度消失
- Layer Norm：稳定训练
- FFN：非线性变换
- Dropout：防止过拟合

## 位置编码

### 为什么需要

自注意力本身没有位置概念，交换输入顺序结果不变。

### 正弦位置编码

$$
PE(pos, 2i) = \sin\left(\frac{pos}{10000^{2i/d}}\right)
$$

$$
PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{2i/d}}\right)
$$

### 其他方案

- 可学习位置编码：BERT 用
- 相对位置编码：T5、Transformer-XL 用
- RoPE：LLaMA、Qwen 用，旋转位置编码
- ALiBi：BLOOM 用，线性偏置

## GPT vs BERT

- 结构：GPT 是 Decoder-only，BERT 是 Encoder-only
- 训练目标：GPT 自回归，BERT 掩码语言模型
- 擅长：GPT 擅长生成，BERT 擅长理解
- 代表：GPT-3/4、LLaMA vs BERT、RoBERTa

## 参数量估算

以 LLaMA-7B 为例：

- 层数：32
- 隐藏维度：4096
- 注意力头数：32
- 参数量：约 67 亿

参数量 ≈ 12 × 层数 × 隐藏维度²

## 训练与推理

### 训练

- 数据：海量文本（万亿 token）
- 目标：预测下一个 token
- 优化：AdamW、学习率预热、梯度裁剪

### 推理

- Prefill：处理输入 prompt，计算 KV Cache
- Decode：逐个生成 token，用 KV Cache 加速

### KV Cache

缓存已计算的 K、V，避免重复计算。

代价：显存占用随序列长度线性增长。

## 常见优化

- FlashAttention：加速注意力计算
- KV Cache：加速推理
- 量化：降低显存
- LoRA：低成本微调
- 蒸馏：压缩模型

## 面试常问

1. 为什么用 $\sqrt{d_k}$ 缩放？
2. 多头注意力的作用是什么？
3. 位置编码有哪些方案？
4. GPT 和 BERT 的区别？
5. 为什么 Transformer 能并行？

## 延伸阅读

- 原论文：Attention is All You Need
- The Illustrated Transformer（图解）
- LLaMA、Qwen 等技术报告
