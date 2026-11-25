---
layout: page
sidebar: false
head:
  - - meta
    - name: robots
      content: noindex
title: 订阅好了
description: 之后每周一份全球 AI × 金融资讯精选会发到你的邮箱。每封信底部都有退订链接，随时可以退订。
---

<script setup>
import { onMounted } from 'vue'
import { markSubscribed } from '../.vitepress/theme/subscribe.js'
import { track } from '../.vitepress/theme/analytics.js'
onMounted(() => { markSubscribed(); track('subscribe-confirmed') })
</script>

<SiteArticle>

## 接下来

- 每周收到一份精选：本周大事、产业动态、监管与政策，以及顶会顶刊与权威机构的新研究，每条都有中文摘要和原文链接。
- 看到值得分享的 AI × 金融资讯，直接回复周报邮件推荐给大家，我们会在下一期选登并署上你的名字。
- 觉得有用，欢迎去 [GitHub](https://github.com/Barca0412/Introduction-to-Quantitative-Finance) 点一个 Star。

等第一封信的时候，可以先去 [AI × 金融论文雷达](/arxiv/) 看看最近的论文。

</SiteArticle>
