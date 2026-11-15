# 自托管搜索模型与运行时

模型：Xenova/all-MiniLM-L6-v2，基础模型 sentence-transformers/all-MiniLM-L6-v2。

- 固定版本：`751bff37182d3f1213fa05d7196b954e230abad9`。
- 许可：[固定版本模型卡](https://huggingface.co/Xenova/all-MiniLM-L6-v2/blob/751bff37182d3f1213fa05d7196b954e230abad9/README.md) 声明 Apache-2.0；原文保存在 `MODEL_CARD.md`，许可证全文见 `APACHE-2.0.txt`。
- 四个模型文件及模型卡均于 2026-11-16 从上述固定版本下载核对，与本地已验证缓存的 SHA256 一致；哈希和大小见 `scripts/site/search_model.json`。
- 模型未修改；仅将其同源托管，使用 mean pooling 和 normalize，以兼容雷达已经生成的 384 维向量。
- Transformers.js 2.17.2：Apache-2.0，许可从已安装包的 LICENSE 保存。
- ONNX Runtime 1.14.0：MIT，许可原文来自 [v1.14.0 LICENSE](https://github.com/microsoft/onnxruntime/blob/v1.14.0/LICENSE)。WASM 从锁定的 Transformers.js 包内 dist 复制。

`node scripts/site/prepare_search_model.mjs` 优先读取通过哈希核对的本地缓存；没有缓存时下载固定版本并核验。模型卡需要重新获取时使用 `--refresh-model-card`。生成的 `docs/public/models/` 不提交到 Git。
