# 双站发布与维护

主站为 `https://quant.hfthnu.com`；海外入口为 `https://Barca0412.github.io/Introduction-to-Quantitative-Finance/`。两个站点使用同一份公开数据快照，canonical、sitemap、结构化数据都指向主站。

## 本地验证

使用项目的 Python 环境生成公开数据；不要使用缺少依赖的系统 Python。已有内部历史数据和向量时：

```sh
python -m scripts.arxiv_radar.build_site_data
npm run test:site
npm run docs:build:dual
```

结果为 `.site-build/server/` 和 `.site-build/pages/`。生成脚本会检查模型与 WASM 的固定 SHA256、10 MiB 文件上限的唯一精确例外、两站 manifest 一致性和站内链接。模型仅在用户执行语义查询时于 Worker 加载，普通访问不下载模型。

## 发布前配置

须先核验服务器 ED25519 指纹，再保存完整 known_hosts 行。不要在工作流中动态信任 ssh-keyscan 结果。2026-11-16 管理员经用户确认的指纹为：

`SHA256:yA0y7TrY627Xav6sh0wYM+zoOOsulj7UdahAcsvtYdM`

仓库 Variables：

| 名称 | 值 |
|---|---|
| DEPLOY_HOST | 106.53.153.215 |
| DEPLOY_PORT | 22 |
| DEPLOY_USER | deploy |
| DEPLOY_TARGET | / |
| DEPLOY_KNOWN_HOSTS | 已核验的完整主机公钥行 |

`DEPLOY_SSH_KEY` 是已有仓库 Secret。不要将私钥写入仓库、报告或聊天。可复用工作流显式声明该 Secret，每日流水线显式传入。服务器实测启用只写 rrsync，所以目标必须是其受限目录根 `/`，不能再拼 `/var/www/quant/`。不要修改 Nginx、服务器权限或 rrsync 限制。

本地预演使用 GNU rsync。macOS 自带 openrsync 分开传递短选项，已被该服务器的 rrsync 参数校验拒绝；GitHub Ubuntu 使用 GNU rsync。

## 首次覆盖旧站

1. 本地准备可审查的提交、双站产物和验证记录。
2. 分别取得推送、开 PR、仓库配置修改、线上部署的明确授权；PR 由用户合并。
3. 先保存旧站完整备份、文件清单及 SHA256，备份放在 webroot 之外。只写部署密钥不能直接通过 SSH 下载旧站，但可以从公开 HTTPS 保存静态文件：先用本地空目录作源执行 `rsync --dry-run --delete` 获取完整清单，逐项下载，再从备份向服务器执行 `rsync --checksum --dry-run --delete`。只有内容差异、新增和删除均为零，才能将该本地副本归档为可回滚版本。文件无法公开读取或校验不一致时，须由管理员归档 `/var/www/quant`；不能将部分下载视为完整备份。
4. 用同一份候选产物执行 GNU rsync `--dry-run --delete --delay-updates --itemize-changes`，展示新增、覆盖和删除清单。预演不代表已经部署。
5. 确认备份和具体部署授权后，再运行工作流。工作流日志保留一次同参数 dry-run，随后才上传。
6. `verify_deployment.py` 校验关键页面 HTML 的 SHA256、manifest 和 build-info，防止相同数据下旧 UI 被误认为发布成功。

## 自动运行

`daily-arxiv.yml` 完成采集和数据发布后调用 `deploy-site.yml`。每次只恢复和生成一次数据，产出两站；两个部署 job 仅依赖公共构建，互不依赖。Pages 专属步骤全部在 Pages job 中。

完整发布使用 `site-release` 串行锁。每个部署 job 在上传前核对产物 commit 仍是 origin/main，并拒绝比目标站 built_at 更旧的产物。网络失败、坏元数据均停止该目标部署；目标首次没有 build-info（HTTP 404）允许迁移。重跑失败 job 使用它原构建的确切 artifact 名，不会误取其他运行的文件。

## 回滚

- 首次改版回滚：将已核验的旧站压缩包解压到本地临时目录，先确认文件哈希，再以其中 `site/` 为源向 rrsync 目标 `/` 做 dry-run，经授权后恢复。管理员保存的服务器归档也可由管理员恢复。不要直接叠加解压到当前站点并保留新文件。
- 后续回滚：每次 Actions 通用双站 artifact 保留 30 天。选择已验证版本下载并检查哈希；批准后用相应站点目录恢复。回滚是明确的人工操作，不能通过重跑旧任务绕过防旧覆盖检查。
- 恢复后核验旧版本 manifest、关键页面和文件哈希；有 build-info 时一并核对，旧站没有该文件时以备份清单和全量 checksum dry-run 为准。记录恢复版本和时间。需要暂停每日发布时，另行取得停用工作流授权。

## 日常检查

1. 查看最近一次每日任务的采集、NBER、数据发布、公共构建和两站部署各步骤，不以整个任务绿色代替来源核对。
2. 对比两站 manifest 的 latest_published_date、论文数和哈希，查看 build-info 的 commit / built_at。
3. 抽查实际新收录 ID 与原文地址；来源无新论文可能正常，接口错误或连续落后需要看对应日志。
4. 检查模型首用、失败降级、HTTPS 和移动导航。大陆网络手机访问须由用户实机确认。
5. 首次获准完整发布后，在当前任务继续验证下一次定时运行；尚未运行的步骤必须标为待验。

完整数据集仍沿用原有发布策略。公开站点产物不含英文摘要及研究者邮箱；本次没有发布未审核周报，也没有移动仓库 PDF。
