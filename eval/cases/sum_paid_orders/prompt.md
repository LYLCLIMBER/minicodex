# 跨文件统计已支付订单

请完善 `aggregate.py`：读取 `orders/` 下所有 JSON 文件中的订单，统计状态为 `paid` 的订单数量和金额总和，并将结果写入工作区根目录的 `summary.json`。

每个订单文件的顶层对象都有 `orders` 数组；订单包含 `status` 和 `amount` 字段。输出必须是合法 JSON，包含数值字段 `paid_order_count` 和 `total_amount`。未支付订单不能计入统计。
