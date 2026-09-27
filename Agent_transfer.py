"""SQL Agent 核心逻辑：自然语言 → SQL → 执行 → 解释。"""
import logging
import os
import re
import sqlite3

from langchain_community.llms import Tongyi

DB_PATH = os.getenv("DB_PATH", "data/orders.db")
LOG_PATH = os.getenv("LOG_PATH", "data/agent_transfer.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
logger = logging.getLogger("agent_transfer")

# Tongyi 自动从 DASHSCOPE_API_KEY 环境变量读 key
llm = Tongyi(model="qwen-turbo")

SCHEMA = "表 orders(id, product, amount)，amount 是销售额（元）"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS orders(
            id      INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            amount  REAL NOT NULL
        );
    """)
    if conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO orders(id, product, amount) VALUES(?,?,?)",
            [
                (1,  "智能手表",    10788.0),
                (2,  "蓝牙耳机",    14970.0),
                (3,  "机械键盘",    10782.0),
                (4,  "4K显示器",    15992.0),
                (5,  "人体工学椅",   6495.0),
                (6,  "智能手表",     6293.0),
                (7,  "蓝牙耳机",     7485.0),
                (8,  "机械键盘",    13178.0),
                (9,  "4K显示器",     5997.0),
                (10, "人体工学椅",  11691.0),
            ],
        )
        conn.commit()
    conn.execute("PRAGMA query_only = ON")
    return conn


BANNED = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "REPLACE",
    "TRUNCATE", "ATTACH", "DETACH", "PRAGMA", "VACUUM", "GRANT",
    "REVOKE", "EXEC", "EXECUTE",
}

MUTATION_INTENT = (
    "删除", "删掉", "更新", "修改", "更改", "改成", "设置", "写入", "插入",
    "新增", "创建", "清空", "移除", "drop", "delete", "update", "insert",
    "alter", "create", "replace", "truncate", "vacuum", "attach", "detach",
)


def clean_sql(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip().rstrip(";").strip()


def is_safe(sql: str):
    if not sql:
        return False, "SQL 为空"
    if ";" in sql:
        return False, "检测到多条语句（;），只允许一条查询"
    upper = sql.upper()
    if not re.match(r"^SELECT\b", upper):
        return False, "只允许 SELECT 查询"
    for kw in BANNED:
        if re.search(rf"\b{kw}\b", upper):
            return False, f"检测到危险关键字 [{kw}]"
    return True, ""


def has_mutation_intent(question: str):
    normalized = (question or "").lower()
    return any(keyword in normalized for keyword in MUTATION_INTENT)


def ask_agent(question: str) -> dict:
    """返回 {answer, sql, rejected, reason}。"""
    logger.info("开始处理请求，用户问题：%s", question)
    conn = init_db()

    try:
        if has_mutation_intent(question):
            reason = "检测到数据修改意图，只允许执行只读 SELECT 查询"
            logger.warning("拒绝：%s，问题：%s", reason, question)
            return {"answer": f"拒绝执行：{reason}", "sql": "", "rejected": True, "reason": reason}

        sql_prompt = (
            f"你是一个 SQLite 专家。表结构：{SCHEMA}\n"
            f"只输出一条仅含 SELECT 的 SQL，不要解释，不要代码块，不要分号。\n"
            f"问题：{question}"
        )
        sql = clean_sql(llm.invoke(sql_prompt))
        logger.info("生成的 SQL：%s", sql)

        ok, reason = is_safe(sql)
        if not ok:
            logger.warning("SQL 安全校验失败：%s，SQL：%s", reason, sql)
            return {"answer": f"拒绝执行：{reason}", "sql": sql, "rejected": True, "reason": reason}

        cur = conn.execute(sql)
        columns = [d[0] for d in (cur.description or [])]
        rows = cur.fetchall()
        logger.info("查询成功，列名：%s，结果：%s", columns, rows)

        explain_prompt = (
            f"用户问题：{question}\n"
            f"SQL：{sql}\n"
            f"列名：{columns}\n"
            f"查询结果：{rows}\n"
            f"请用一句简洁自然的中文回答用户，数字带上单位或说明。"
        )
        answer = llm.invoke(explain_prompt).strip()
        logger.info("最终回答：%s", answer)
        return {"answer": answer, "sql": sql, "rejected": False, "reason": ""}
    except Exception as e:
        logger.exception("请求处理异常：%s", e)
        return {"answer": f"SQL 执行出错：{e}", "sql": "", "rejected": True, "reason": str(e)}
    finally:
        conn.close()