# 大模型微调：LoRA 与全参微调

## 为什么要微调

预训练模型虽然强大，但在特定领域或任务上表现不够：

- 领域知识不足（医疗、法律）
- 输出格式不符合要求
- 语气风格不匹配

微调就是让模型适应特定任务。

## 微调方式对比

- 全参微调：显存需求极高，效果最好，成本高
- LoRA：显存需求低，效果接近全参，成本低
- QLoRA：显存需求更低，效果略降，成本最低
- Prompt Tuning：显存需求极低，效果一般，成本极低

## 全参微调

### 原理

更新模型所有参数。

### 显存估算

以 7B 模型为例：

- 模型参数：7B × 2 字节（fp16）= 14 GB
- 梯度：14 GB
- 优化器状态（Adam）：7B × 8 字节 = 56 GB
- 激活值：取决于 batch size

总计：至少 80 GB 显存，需要 A100 80G。

### 适用场景

- 数据量大（百万级）
- 追求极致效果
- 有充足算力

## LoRA

### 原理

在原始权重旁加一个低秩矩阵，只训练这个小矩阵。

$$
W' = W + BA
$$

- W：原始权重（冻结）
- B：$d \times r$ 矩阵
- A：$r \times d$ 矩阵
- r：秩，通常 8-64

### 参数量

假设 $d=4096$，$r=8$：

- 原始：$4096 \times 4096 = 16M$
- LoRA：$4096 \times 8 \times 2 = 65K$

只有原始的 0.4%。

### 优点

- 显存需求低（7B 模型 16G 显存可训）
- 训练快
- 可插拔（一个基座 + 多个 LoRA）
- 效果好（接近全参）

### 关键参数

- r：秩，常用 8、16、32
- alpha：缩放因子，常用 16、32
- dropout：防过拟合，常用 0.05、0.1
- target_modules：应用层，常用 q_proj、v_proj

### 代码示例

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(base_model, config)
```
