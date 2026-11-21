# 首页访问统计（此刻在线 / 累计访客 / AI 读取）

首页首屏那两行小字的数据由这里的 `site_stats.py` 生成。它每分钟在网站服务器上跑一次，写出一个只有总数的 JSON。

| 东西 | 位置 |
|---|---|
| 脚本（服务器上的副本） | `~qgh/site-stats/site_stats.py` |
| 状态文件（累计数、读到日志的哪里） | `~qgh/site-stats/state.json` |
| 错误日志 | `~qgh/site-stats/error.log` |
| 公开的 JSON | `/var/lib/site-stats/site-stats.json`，由 nginx 提供为 https://quant.hfthnu.com/site-stats.json（配置在 `/etc/nginx/conf.d/quant.hfthnu.com.conf`） |
| 读的 nginx 日志 | `/var/log/nginx/quant.hfthnu.com.access.log`（`qgh` 在 adm 组，可读） |
| 定时任务 | `qgh` 的 crontab：`* * * * * /usr/bin/python3 $HOME/site-stats/site_stats.py >/dev/null 2>>$HOME/site-stats/error.log` |

## 数据怎么来

- **人**：用 `docker exec umami-db-1 psql` 跑只读查询。
  - "此刻"是最近 5 分钟内有活动的 Umami 会话。
  - "累计访客"是所有 Umami 会话。
  - 两者都扣掉 ExaSearchBot 的会话。它用真浏览器抓网页，会被 Umami 当成人；识别规则见脚本里的 `EXA_PATTERN`。
- **AI**：增量读 nginx 日志，按 User-Agent 匹配 `AI_AGENTS` 名单。
  - 一个请求只算一次，脚本、样式、字体、图片这类静态文件不算。
  - 日志每天轮转一次，脚本会先读完 `.1` 里剩下的部分，再接着读新文件。
  - `kind = "user"` 的（ChatGPT-User、Claude-User 等）是"有人让 AI 来读"，另外单独计数。
  - Google、Bing、百度这类普通搜索引擎不算 AI。
- 查不到 Umami 时沿用上次的累计数，"此刻在看"不显示，不会写成 0。网页上数据超过 10 分钟没更新，那两行字整块隐藏。

## 常用操作

```bash
ssh hft
# 停：注释掉 crontab 里那一行
crontab -e
# 手动跑一次，看输出
python3 ~/site-stats/site_stats.py
# 更新脚本：在仓库里改好、跑完测试后
scp scripts/site/stats/site_stats.py hft:site-stats/site_stats.py
```

- **改 AI 名单**：改脚本里的 `AI_AGENTS`，跑测试，再复制到服务器。改动只影响以后的计数，已经累计的数不会重算。
- **测试**：`python3 -m unittest scripts/site/stats/test_site_stats.py`
- **自测时要扣回**：用假冒的 User-Agent 测试（比如 `curl -A GPTBot`）也会被计数。测完要从 `state.json` 的 `agent_totals` 里减掉。
