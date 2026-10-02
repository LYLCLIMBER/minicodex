# 服务配置要求

在本目录创建 `config.json`，使用以下结构（字段名称区分大小写）：

- `server`：对象，包含 `host`（字符串 `127.0.0.1`）和 `port`（整数 `8765`）。
- `paths`：对象，包含 `data_dir`（字符串 `./data`）和 `log_file`（字符串 `./logs/service.log`）。
- `features`：对象，包含 `cache_enabled`（布尔值 `true`）和 `debug_enabled`（布尔值 `false`）。

不要把端口或布尔值写成字符串。配置文件必须可由标准 JSON 解析器读取。
