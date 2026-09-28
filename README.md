相关资源链接：
- [OpenAI API doc](https://developers.openai.com/api/docs/guides)
- [DeepSeek API doc](https://api-docs.deepseek.com/zh-cn/api/)

按照 https://openai.com/zh-Hans-CN/index/unrolling-the-codex-agent-loop 构建一个简单的 minicodex，它应该能够完成一个轻量但完整的 agent loop，期间能：
1. 调用工具
2. 做好基本的上下文管理，比如 instruction，tool_calls 等
