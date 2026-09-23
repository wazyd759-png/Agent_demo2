import json
import time
import statistics
import requests

BASE_URL = "http://121.40.172.119"

CASES = [
    {"q": "GPT5.6系列产品如何被推出的",         "keywords": ["GPT-5.6", "推出"]},
    {"q": "GPT5.6是怎么发布上线的",             "keywords": ["GPT-5.6"]},
    {"q": "GPT5.6有哪些版本",                   "keywords": ["Sol", "Terra", "Luna"]},
    {"q": "GPT5.6的推出背景和目标", "keywords": ["GPT-5.6"]},  # 只要求包含 GPT-5.6
    {"q": "GPT-5.6 Sol 在哪些基准测试里破纪录", "keywords": ["HumanEval"]},
    {"q": "OpenAI 的定价策略是什么",           "keywords": ["定价"]},
    {"q": "测试时训练是什么",                   "keywords": ["测试时训练"]},
    {"q": "今天天气怎么样",                     "keywords": []},
]

def is_hit(sources, keywords):
    if not keywords:
        return None
    text = " ".join(s["content"] for s in sources)
    return all(k in text for k in keywords)

def is_faithful(answer, keywords):
    if keywords:
        return None
    deny = ["不知道", "未包含", "没有", "无法", "不包含", "未提及"]
    return any(d in answer for d in deny)

rows = []
print(f"{'问题':<40} {'耗时':>6}  {'来源数':>5}  {'命中':>5}")
print("-" * 70)
for c in CASES:
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/ask",
                          json={"question": c["q"], "top_k": 3},
                          timeout=120)
        elapsed = time.time() - t0
        data = r.json()
    except Exception as e:
        print(f"{c['q']:<40}  ERROR: {e}")
        continue

    hit = is_hit(data.get("sources", []), c["keywords"])
    faith = is_faithful(data.get("answer", ""), c["keywords"])
    rows.append({
        "question": c["q"],
        "answer": data.get("answer", ""),
        "sources_count": len(data.get("sources", [])),
        "hit": hit,
        "faithful": faith,
        "elapsed_s": round(elapsed, 2),
    })
    print(f"{c['q']:<40} {elapsed:>5.2f}s  {len(data.get('sources', [])):>5}  {str(hit):>5}")

in_kb = [r for r in rows if r["hit"] is not None]
times = [r["elapsed_s"] for r in rows]
hit_rate = sum(1 for r in in_kb if r["hit"]) / len(in_kb) if in_kb else 0
faith_rows = [r for r in rows if r["faithful"] is not None]
faith_rate = sum(1 for r in faith_rows if r["faithful"]) / len(faith_rows) if faith_rows else 0
src_rate = sum(1 for r in rows if r["sources_count"] > 0) / len(rows) if rows else 0

print("\n===== 评测汇总 =====")
print(f"检索命中率      : {hit_rate:.1%}")
print(f"Faithfulness    : {faith_rate:.1%}")
print(f"平均响应时间    : {statistics.mean(times):.2f}s")
print(f"来源引用完整率  : {src_rate:.1%}")

with open("eval_result.json", "w", encoding="utf-8") as f:
    json.dump({
        "summary": {
            "hit_rate": hit_rate,
            "faithfulness": faith_rate,
            "avg_elapsed_s": round(statistics.mean(times), 2),
            "source_rate": src_rate,
        },
        "details": rows,
    }, f, ensure_ascii=False, indent=2)
print("\n结果已保存到 eval_result.json")