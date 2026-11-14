# 参与贡献

欢迎修正错误、补充资料、改进讲义。动手之前，可以先在 [Discussions](https://github.com/Barca0412/Introduction-to-Quantitative-Finance/discussions) 说一下想法；小的修正可以直接提 Pull Request。

## 仓库里有什么

| 目录 | 内容 |
|:-----|:-----|
| `docs/tutorials/` | 讲义，每一讲一个文件夹 |
| `docs/wiki/` | 知识库概念页 |
| `docs/library/` | 研报与论文目录（`reports.md`、`papers.md` 由脚本生成，不要手改） |
| `docs/arxiv/` | FinPaperRadar 论文雷达页面 |
| `docs/resources/` | 资源清单 |
| `资料/`、`论文/` | 研报、论文和代码原文件 |
| `data/registry/` | 资源清单的数据（YAML），站点资源页和 README 精选由它生成 |
| `templates/tutorial/`、`templates/wiki-page.md` | 讲义模板、知识库概念页模板 |
| `scripts/` | 论文雷达流水线（`arxiv_radar/`）和站点生成脚本（`site/`） |

本地预览：

```bash
npm install
npm run docs:dev
```

## 写一讲新讲义

1. 把 `templates/tutorial/` 整个复制到 `docs/tutorials/<两位编号>-<英文短名>/`，例如 `docs/tutorials/01-factor-ic-test/`。
2. 改 `index.md` 开头的字段：标题、80–120 字的描述、难度、时长、前置知识、数据来源、署名、授权，以及用到的知识库页面和研报。
3. 正文按模板的八节写：要解决的问题、你会做出什么、数据与环境、分步实现、结果与解读、常见的坑、延伸阅读、练习。
4. 完整代码放 `code/`，要能在全新环境里从头跑通；只能用读者免费拿得到的数据，必要时在 `data/sample/` 放小样本。
5. 写完、审完后，删掉开头的 `draft: true`，讲义就会出现在讲义列表里。

几条硬规则：

- "常见的坑"一节至少检查前视偏差、幸存者偏差和交易成本。
- 不放课程作业的标准答案；作业相关内容晚于课程进度发布。
- 结论只写数据支持的部分，不写收益承诺，不构成投资建议。
- 图片用自己画的，或许可证允许转载的（例如 CC BY）。

## 往资源清单里加项目

资源清单由 `data/registry/` 里的 YAML 生成，站点页面和 README 精选都不要手改。字段和命令见 [data/registry/README.md](./data/registry/README.md)。

两种方式都可以：

- **提 issue**：用"推荐一个资源"模板填写，维护者整理后加入。
- **直接提 PR**：在 `data/registry/items/<页面>.yaml` 里新增一条，`reviewed` 留空，运行 `npm run registry:check` 通过后提交。

我们希望清单里的每一项都值得推荐，提交时请写清：

- 一句话说明它解决什么问题、适合谁（`why_zh`，60 字以内，自己写，不要照搬别处的描述）；
- 它和清单里已有的同类项目有什么不同；
- 项目仍在维护（近一年有更新）。

**商业产品和自荐**：可以推荐，但必须在 PR 或 issue 里说明你和项目的关系，收费产品要标明 `pricing`。纯广告或和量化研究关系不大的会被婉拒。

维护者会在 **7 天内** 首次回复每个 PR 和 issue。

## AtomGit 镜像

仓库在 AtomGit 上有一份镜像（[Barca12345/Introduction-to-Quantitative-Finance](https://atomgit.com/Barca12345/Introduction-to-Quantitative-Finance)），由 GitHub Actions 自动把 GitHub 的 `main` 推过去。请在 GitHub 上提交修改；直接在 AtomGit `main` 上的提交会在下一次同步时被覆盖。

## 研报与论文

`资料/` 和 `论文/` 下的文件不要改名、不要移动，站点目录和外部链接都依赖这些路径。新增文件放进对应的系列或主题目录即可，目录页会在下次构建时自动更新。
