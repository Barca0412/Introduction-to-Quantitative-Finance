# 资源注册表

站点"资源"栏目的每一条都记在这里，页面和 README 精选由 `scripts/site/gen_resources.mjs` 自动生成。**改资源只改这里的 YAML，不要改生成出来的页面。**

## 文件

| 文件 | 内容 | 谁来改 |
|---|---|---|
| `pages.yaml` | 资源页面和子分类的定义 | 人 |
| `items/<页面 key>.yaml` | 该页面的条目 | 人 |
| `sources.yaml` | 参考过的上游清单、许可证和使用方式 | 人 |
| `stats.json` | GitHub 星数、最近提交、是否归档 | 只由 `npm run registry:stats` 写入 |

## 条目字段

```yaml
items:
  - id: microsoft/qlib          # 必填，全库唯一。GitHub 项目写 owner/name，其他写英文短名
    name: Qlib                  # 必填，显示名称
    url: https://github.com/microsoft/qlib   # 链接（book 类可以只填 publisher_url）
    repo: microsoft/qlib        # GitHub 项目填写，用来取星数和判断是否停更
    sub: research-platforms     # 必填，pages.yaml 里该页面的子分类 key
    tier: A                     # 必填，A 或 B
    why_zh: 微软开源的 AI 量化研究平台，覆盖数据、因子、模型到回测的完整流程，适合做机器学习选股。  # A 级必填，最多 60 字，自己写
    tags: [机器学习, A股]
    lang: zh                    # zh 或 en；en 会显示"英文"标签
    market: cn                  # cn / us / global / crypto
    pricing: free               # free / freemium / paid（data 类必填）
    status: stale               # 可选，人工指定 active / stale / archived；不填则按 stats.json 判断
    pick: true                  # 可选，进入 README 精选
    lectures: [01-factor-ic-test]   # 可选，关联讲义
    sources: [wilsonfreitas-awesome-quant, thuquant-awesome-quant]  # 出自哪些上游清单；自己发现的写 []
    added: 2026-11-16           # 必填，加入日期
    reviewed: 2026-11-18        # 维护者审核通过的日期；留空的条目不会显示在站点上
```

不同类型的额外字段：

- **book**：`authors`（必填，列表）、`year`、`edition`、`publisher_url`、`free_url`（只填作者或出版社提供的合法免费版）、`title_zh`
- **course**：`provider`（必填）、`free`（`false` 表示收费）、`format`
- **community**：`type`（必填）：forum / blog / newsletter / podcast / video / wechat / research-center / exchange / regulator / jobs / question-bank / other
- **data**：`pricing` 必填

## 规则

- 推荐理由 `why_zh` 必须自己写：说清楚它解决什么问题、适合谁。不要翻译或照搬上游清单的描述，尤其是 `use: link-only` 的来源。
- A 级全部收；B 级只收能补上空缺的，或至少 2 个来源都列了、还在维护、星数 ≥ 500 的；C 级不收。
- 不链接任何盗版或未授权转载的电子书。生成脚本发现这类域名会直接让构建失败。
- 商业产品可以收，但要标 `pricing`，且自荐必须在 PR 里说明与项目的关系。
- 新条目先以 `reviewed:` 留空提交，维护者审核通过后再填日期。

## 常用命令

```bash
npm run docs:gen          # 校验并生成页面
npm run registry:check    # 只校验
npm run registry:stats    # 刷新 stats.json（需要 GITHUB_TOKEN 或已登录 gh）
npm run registry:urls     # 列出所有链接，给链接检查用
npm run test:site         # 生成脚本的测试
```
