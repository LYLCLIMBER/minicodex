import json
from pathlib import Path


def summarize():
    # TODO: 读取 orders/ 下的所有 JSON 文件，汇总已支付订单。
    return {"paid_order_count": 0, "total_amount": 0}


if __name__ == "__main__":
    Path("summary.json").write_text(
        json.dumps(summarize(), ensure_ascii=False), encoding="utf-8"
    )
