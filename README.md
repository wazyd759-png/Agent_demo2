# Agent Transfer

这是一个基于大语言模型 + SQLite 的简易“自然语言查询数据库”示例程序。

用户输入自然语言问题后，程序会让大模型先生成对应的 SQL，再执行查询，并将查询结果再转换成中文自然语言回答。

## 项目功能

- 从自然语言提问生成 SQLite 查询语句
- 对 SQL 进行安全校验
- 仅允许单条 `SELECT` 查询执行
- 使用 SQLite 数据库存储订单数据
- 记录每次请求的日志，便于排查问题

## 技术栈

- Python 3.10+
- SQLite
- LangChain Community
- 阿里云通义千问（Qwen）模型

## 目录结构

```text
.
├─ Agent_transfer.py      # 主程序
├─ orders.db              # SQLite 数据库文件
├─ agent_transfer.log     # 运行日志
├─ README.md              # 项目说明
├─ requirements.txt       # Python 依赖
├─ .env.example           # 环境变量示例
└─ .gitignore             # 可选，建议忽略数据库和日志文件
```

## 环境准备

1. 创建并激活虚拟环境

```powershell
cd d:\demo2
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. 安装依赖

```powershell
pip install -r requirements.txt
```

3. 配置环境变量

复制 `.env.example` 为 `.env`，并填写真实的 API Key：

```powershell
copy .env.example .env
```

然后编辑 `.env`：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

## 启动方式

### 方式 1：交互式输入问题

```powershell
cd d:\demo2
.\venv\Scripts\Activate.ps1
python Agent_transfer.py
```

运行后会提示：

```text
请输入问题:
```

例如：

```text
销售额最高的 3 个产品是什么
```

### 方式 2：直接在代码中修改入口问题

也可以直接在 `if __name__ == "__main__":` 处修改默认问题。

## 运行示例

示例输入：

```text
销售额最高的 3 个产品是什么
```

可能输出：

```text
销售额最高的三个产品是：4K显示器、蓝牙耳机和机械键盘。
```

## 日志说明

程序会将每次请求的关键行为写入日志文件：

- 用户问题
- 生成的 SQL
- 执行结果
- 是否发生异常
- 最终回答

日志文件：

```text
agent_transfer.log
```

## 安全说明

本程序仅允许执行单条 `SELECT` 查询，默认拦截以下危险操作：

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- CREATE
- PRAGMA
- EXEC

同时在数据库连接层使用了只读模式，进一步降低误操作风险。

## 演示地址

本项目是本地命令行应用，不部署为 Web 服务，因此没有在线演示地址。

本地演示方式：

```text
http://localhost: 无（本地脚本运行）
```

如需演示，可直接在本地终端运行：

```powershell
python Agent_transfer.py
```

## 提交记录

当前工作目录不是 Git 仓库，因此没有可用的提交历史记录。

如果你之后初始化 Git，可以执行：

```bash
git init
git add .
git commit -m "Initial commit"
```

## 常见问题

### 1. 报错：`DASHSCOPE_API_KEY` 未设置

请确保在 `.env` 文件中配置了有效的密钥。

### 2. 报错：Model / API 调用失败

请确认：

- 网络可用
- API Key 正确
- 访问权限已开通

### 3. 日志为空

确认脚本已经执行，并检查：

- `agent_transfer.log` 是否生成
- 日志配置是否正确

## 许可证

该项目仅用于学习与演示用途。
