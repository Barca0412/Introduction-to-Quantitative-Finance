<script setup>
// 订阅框：点右上角"一键订阅"时在屏幕正中弹出（背后毛玻璃虚化）；站内看满 45 秒自动弹出时是右下角的小卡片，
// 在小卡片里点"选关心的方向"会换成正中的大框。
// 提交到 /api/subscribe/（服务器上的 scripts/site/subscribe/subscribe_server.py）。
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { withBase } from 'vitepress'
import GitHubStar from './GitHubStar.vue'
import { closeSubscribe, markSubscribed, subscribeState } from '../subscribe.js'
import { track } from '../analytics.js'

// 和论文雷达"金融领域 × 任务"同一套分类（scripts/arxiv_radar/vocab/taxonomy.yaml），去掉"通用金融"
const DOMAINS = [
  ['asset-pricing', '资产定价'], ['trading', '交易执行'], ['portfolio-risk', '组合风险'], ['derivatives', '衍生品'],
  ['credit-banking', '信用银行'], ['corporate-finance', '公司金融'], ['fin-nlp', '文本舆情'], ['crypto-defi', '加密资产'],
  ['macro-policy', '宏观政策'], ['insurance-household', '保险个人'], ['market-structure', '市场结构'],
]
const TASKS = [
  ['forecasting', '预测'], ['pricing', '定价'], ['decision', '交易决策'], ['signal-mining', '因子挖掘'],
  ['understanding', '理解问答'], ['risk-assessment', '风险评估'], ['generation', '生成'], ['simulation', '市场模拟'],
  ['multi-task', '多任务'],
]
const MAX = 9
// 公众号二维码：图片放到 docs/public/subscribe/wechat-qr.png 后把这里改成 true
const HAS_WECHAT_QR = false

const email = ref('')
const website = ref('') // 陷阱字段，真人看不到
const picks = ref([]) // 'd:<领域>' 整行 | 't:<任务>' 整列 | 'd:<领域>|t:<任务>' 一格
const expanded = ref(false)
const state = ref('idle') // idle | sending | done | error
const queued = ref(false) // 发信服务开通前：先登记，周报发出前再补发确认信
const error = ref('')
const input = ref(null)

const open = computed(() => subscribeState.open)
const centered = computed(() => subscribeState.source !== 'auto' || expanded.value)
const full = computed(() => picks.value.length >= MAX)
const endpoint = () => {
  const h = location.hostname
  if (h.endsWith('github.io')) return 'https://quant.hfthnu.com/api/subscribe/'
  if (h === 'localhost' || h === '127.0.0.1') return 'http://127.0.0.1:8731/api/subscribe/'
  return withBase('/api/subscribe/')
}

const rowKey = (d) => `d:${d}`
const colKey = (t) => `t:${t}`
const cellKey = (d, t) => `d:${d}|t:${t}`
const has = (k) => picks.value.includes(k)
const covered = (d, t) => has(rowKey(d)) || has(colKey(t))

function toggle(k) {
  const i = picks.value.indexOf(k)
  if (i >= 0) picks.value.splice(i, 1)
  else if (!full.value) picks.value.push(k)
}
function toggleRow(d) {
  if (!has(rowKey(d)) && !full.value) picks.value = picks.value.filter((k) => !k.startsWith(`${rowKey(d)}|`)) // 整行包含了这一行的格子
  toggle(rowKey(d))
}
function toggleCol(t) {
  if (!has(colKey(t)) && !full.value) picks.value = picks.value.filter((k) => !k.endsWith(`|${colKey(t)}`))
  toggle(colKey(t))
}
function toggleCell(d, t) { if (!covered(d, t)) toggle(cellKey(d, t)) }

const MESSAGES = {
  'bad-email': '这个邮箱格式好像不对，再检查一下？',
  'too-many': '提交次数有点多，过一会儿再试吧。',
  'mail-failed': '确认信没发出去，请稍后再试，或者去"投稿与联系"告诉我们。',
}

async function submit() {
  if (state.value === 'sending') return
  error.value = ''
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim())) { error.value = MESSAGES['bad-email']; return }
  state.value = 'sending'
  track('subscribe-submit', { source: subscribeState.source, picks: picks.value.length })
  try {
    const res = await fetch(endpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value.trim(), domains: picks.value, website: website.value }),
    })
    const body = await res.json().catch(() => ({}))
    if (!res.ok || !body.ok) throw new Error(body.error || 'failed')
    queued.value = Boolean(body.queued)
    state.value = 'done'
    markSubscribed()
  } catch (e) {
    state.value = 'error'
    error.value = MESSAGES[e.message] || '网络好像出了点问题，请稍后再试。'
  }
}

function close() { closeSubscribe(); expanded.value = false }
function onKey(e) { if (e.key === 'Escape' && open.value) close() }

watch(open, async (v) => {
  if (!v) return
  track('subscribe-shown', { source: subscribeState.source })
  if (state.value !== 'done') { state.value = 'idle'; error.value = '' }
  await nextTick()
  // 读者自己点开的才把光标放进邮箱框；自动弹出的不抢焦点
  if (subscribeState.source !== 'auto') input.value?.focus()
})
// 正中弹框打开时，页面本身不跟着滚
watch(() => open.value && centered.value, (lock) => { document.documentElement.style.overflow = lock ? 'hidden' : '' })
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => { window.removeEventListener('keydown', onKey); document.documentElement.style.overflow = '' })
</script>

<template>
  <Transition name="sub-fade">
    <div v-if="open && centered" class="sub-scrim" aria-hidden="true" @click="close"></div>
  </Transition>
  <Transition :name="centered ? 'sub-pop' : 'sub'">
    <section v-if="open" class="sub-card" :class="{ centered }" role="dialog" :aria-modal="centered ? 'true' : 'false'" aria-labelledby="sub-title">
      <button type="button" class="sub-close" aria-label="关闭" @click="close">×</button>
      <template v-if="state !== 'done'">
        <h2 id="sub-title" class="sub-title"><i class="sub-dot" aria-hidden="true"></i>每周一，3 分钟读完全球 AI × 金融</h2>
        <p class="sub-lead">产业动态 · 监管政策 · 顶会顶刊与权威机构的最新研究，一封邮件读完。随时可以退订。</p>
        <form class="sub-form" novalidate @submit.prevent="submit">
          <label class="sr-only" for="sub-email">邮箱</label>
          <input id="sub-email" ref="input" v-model="email" type="email" inputmode="email" autocomplete="email" placeholder="你的邮箱" maxlength="254" required>
          <input v-model="website" class="sub-trap" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
          <button type="submit" class="btn btn-accent sub-submit" :disabled="state === 'sending'">{{ state === 'sending' ? '提交中…' : '订阅' }}</button>
        </form>
        <p v-if="error" class="sub-error" role="alert">{{ error }}</p>

        <button v-if="!centered" type="button" class="sub-more" @click="expanded = true">选关心的方向（可选）</button>
        <div v-else class="sub-pick">
          <div class="sub-pick-head">
            <p class="sub-pick-title">更关心哪些方向？<span>可选，最多 {{ MAX }} 个，不选就收全部</span></p>
            <p class="sub-pick-count"><span class="num">{{ picks.length }}/{{ MAX }}</span><button v-if="picks.length" type="button" @click="picks = []">清空</button></p>
          </div>
          <div class="sub-grid-wrap">
            <table class="sub-grid">
              <caption>点一格选一个组合；点行名或列名，选整行或整列（各算 1 个）。</caption>
              <thead>
                <tr>
                  <th scope="col" class="corner"><span class="sr-only">金融领域 / 任务</span></th>
                  <th v-for="[t, tn] in TASKS" :key="t" scope="col" class="col-h">
                    <button type="button" :aria-pressed="has(colKey(t))" :disabled="full && !has(colKey(t))" :title="`整列：${tn}`" @click="toggleCol(t)"><span>{{ tn }}</span></button>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="[d, dn] in DOMAINS" :key="d">
                  <th scope="row" class="row-h">
                    <button type="button" :aria-pressed="has(rowKey(d))" :disabled="full && !has(rowKey(d))" :title="`整行：${dn}`" @click="toggleRow(d)">{{ dn }}</button>
                  </th>
                  <td v-for="[t, tn] in TASKS" :key="t" class="cell">
                    <button type="button" :class="{ on: has(cellKey(d, t)), covered: covered(d, t) }" :aria-pressed="has(cellKey(d, t)) || covered(d, t)"
                      :disabled="covered(d, t) || (full && !has(cellKey(d, t)))" :aria-label="`${dn} × ${tn}`" :title="`${dn} × ${tn}`" @click="toggleCell(d, t)"><i></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="HAS_WECHAT_QR" class="sub-wechat">
          <img :src="withBase('/subscribe/wechat-qr.png')" alt="湖南大学金融科技协会公众号二维码" width="88" height="88">
          <p>不想留邮箱？<br>扫码关注协会公众号，每周同步推送。</p>
        </div>
      </template>
      <template v-else>
        <template v-if="queued">
          <h2 id="sub-title" class="sub-title"><i class="sub-dot" aria-hidden="true"></i>订阅成功</h2>
          <p class="sub-lead">已经记下 <strong>{{ email.trim() }}</strong>。第一期周报发出前，我们会先给这个邮箱发一封确认信，点一下确认就好。</p>
        </template>
        <template v-else>
          <h2 id="sub-title" class="sub-title"><i class="sub-dot" aria-hidden="true"></i>还差一步：去邮箱点确认</h2>
          <p class="sub-lead">确认信已经发到 <strong>{{ email.trim() }}</strong>。点信里的链接就订阅好了；没收到的话，看看垃圾邮件。</p>
        </template>
      </template>
      <div class="sub-foot">
        <div class="sub-star"><GitHubStar /><span>觉得有用，去点个 Star</span></div>
        <p>欢迎交流 AI + 金融的新想法和需求，也欢迎<a :href="withBase('/contact')">参与贡献</a>。</p>
      </div>
    </section>
  </Transition>
</template>

<style scoped>
/* 毛玻璃背景：只在正中弹框时出现 */
.sub-scrim { position: fixed; inset: 0; z-index: 59; background: rgba(247, 247, 247, 0.38); backdrop-filter: blur(10px) saturate(1.05); -webkit-backdrop-filter: blur(10px) saturate(1.05); }
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) { .sub-scrim { background: rgba(247, 247, 247, 0.86); } }

.sub-card { position: fixed; inset-inline-end: 24px; inset-block-end: 24px; z-index: 60; inline-size: min(400px, calc(100vw - 48px)); max-block-size: calc(100svh - 48px); overflow-y: auto; padding: 24px 24px 20px; background: var(--bg); color: var(--ink); border: 1px solid var(--rule); border-radius: var(--box); box-shadow: 0 18px 48px rgba(13, 42, 28, 0.16); }
.sub-card.centered { inset: 50% auto auto 50%; transform: translate(-50%, -50%); inline-size: min(600px, calc(100vw - 32px)); max-block-size: calc(100svh - 40px); padding: 28px 32px 22px; box-shadow: 0 24px 64px rgba(13, 42, 28, 0.18); }
.sub-close { position: absolute; inset-block-start: 10px; inset-inline-end: 10px; inline-size: 36px; block-size: 36px; border-radius: 50%; font-size: 22px; line-height: 1; color: var(--muted); }
.sub-close:hover { background: var(--surface); color: var(--ink); }
.sub-title { display: flex; gap: 10px; align-items: baseline; text-wrap: balance; padding-inline-end: 28px; font-size: 1.1875rem; font-weight: 700; line-height: 1.35; letter-spacing: -0.01em; }
.centered .sub-title { font-size: 1.375rem; }
.sub-dot { flex: none; inline-size: 11px; block-size: 11px; border-radius: 50%; background: var(--accent); border: 1.5px solid var(--ink); transform: translateY(-1px); }
.sub-lead { margin-block-start: 8px; color: var(--muted); font-size: 0.9375rem; line-height: 1.6; }
.sub-lead strong { color: var(--ink); font-weight: 600; word-break: break-all; }
.sub-form { display: flex; gap: 8px; margin-block-start: 16px; }
/* 邮箱框在浅色、深色模式下都是白底，所以文字、光标、占位字都用固定的深色，不跟主题变 */
.sub-form input[type="email"] { flex: 1; min-inline-size: 0; block-size: 44px; padding-inline: 16px; border: 1px solid var(--control); border-radius: var(--radius); background: #fff; color: #0d2a1c; caret-color: #0d2a1c; font-size: 1rem; }
.sub-form input[type="email"]::placeholder { color: #6b7670; opacity: 1; }
.sub-form input[type="email"]:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
.sub-submit { block-size: 44px; padding-inline: 20px; }
.sub-submit:disabled { opacity: 0.6; }
.sub-trap { position: absolute; inline-size: 1px; block-size: 1px; opacity: 0; pointer-events: none; }
.sub-error { margin-block-start: 8px; color: #9a2b13; font-size: var(--step-small); }
.sub-more { margin-block-start: 12px; min-block-size: 32px; color: var(--muted); font-size: var(--step-small); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; }
.sub-more:hover { color: var(--ink); }

/* 金融领域 × 任务 选择表：和论文雷达同一种圆点格子 */
.sub-pick { margin-block-start: 20px; padding-block-start: 16px; border-block-start: 1px solid var(--rule); }
.sub-pick-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.sub-pick-title { font-weight: 600; font-size: 0.9375rem; }
.sub-pick-title span { margin-inline-start: 8px; color: var(--muted); font-weight: 400; font-size: var(--step-small); }
.sub-pick-count { display: flex; gap: 10px; align-items: baseline; color: var(--muted); font-size: var(--step-small); white-space: nowrap; }
.sub-pick-count button { color: var(--ink); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 3px; }
.sub-grid-wrap { margin-block-start: 8px; overflow-x: auto; }
.sub-grid { --cell: 34px; --dot: 16px; border-collapse: collapse; margin-inline: auto; font-size: 12.5px; }
.sub-grid caption { caption-side: bottom; padding-block-start: 10px; color: var(--muted); font-size: 12px; text-align: start; }
.sub-grid th { padding: 0; font-weight: 400; white-space: nowrap; }
.sub-grid button { color: var(--ink); }
.col-h { inline-size: var(--cell); vertical-align: bottom; padding-block-end: 6px !important; }
.col-h button { display: inline-flex; justify-content: center; inline-size: 100%; min-block-size: 64px; align-items: flex-end; padding-block: 4px; border-radius: 8px; }
.col-h button span { writing-mode: vertical-rl; letter-spacing: 0.05em; line-height: 1.2; }
.row-h { padding-inline-end: 8px !important; text-align: start; }
.row-h button { min-block-size: 28px; padding-inline: 8px; border-radius: 8px; text-align: start; }
.col-h button:hover:not(:disabled), .row-h button:hover:not(:disabled) { background: var(--surface); }
.col-h button[aria-pressed="true"], .row-h button[aria-pressed="true"] { background: var(--ink); color: var(--bg); font-weight: 600; }
/* 已选中的行名/列名：悬停时背景变浅，文字同时换成深色，保证看得清 */
.col-h button[aria-pressed="true"]:hover, .row-h button[aria-pressed="true"]:hover { background: var(--surface); color: var(--ink); }
.sub-grid th button:disabled { opacity: 0.4; }
.cell { inline-size: var(--cell); block-size: 30px; padding: 0; text-align: center; }
.cell button { display: inline-grid; place-items: center; inline-size: 30px; block-size: 28px; border-radius: 8px; }
.cell button i { inline-size: 9px; block-size: 9px; border-radius: 50%; border: 1.5px solid var(--control); transition: transform 100ms ease-out, background-color 100ms ease-out; }
.cell button:hover:not(:disabled) i { border-color: var(--ink); transform: scale(1.25); }
.cell button.on i { inline-size: var(--dot); block-size: var(--dot); background: var(--accent); border-color: var(--ink); }
.cell button.covered i { inline-size: 12px; block-size: 12px; background: var(--ink); border-color: var(--ink); }
.cell button:disabled:not(.covered) { opacity: 0.35; }

.sub-wechat { display: flex; gap: 14px; align-items: center; margin-block-start: 16px; padding-block-start: 16px; border-block-start: 1px solid var(--rule); font-size: var(--step-small); color: var(--muted); }
.sub-wechat img { border-radius: var(--fig-radius); background: #fff; }
.sub-foot { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; margin-block-start: 18px; padding-block-start: 16px; border-block-start: 1px solid var(--rule); }
.centered .sub-foot { flex-direction: row; align-items: center; justify-content: space-between; flex-wrap: wrap; }
.sub-star { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: var(--step-small); }
.sub-foot p { color: var(--muted); font-size: var(--step-small); line-height: 1.6; }
.sub-foot p a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; }
.sr-only { position: absolute; inline-size: 1px; block-size: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

.sub-enter-active, .sub-leave-active { transition: opacity 180ms ease-out, transform 180ms ease-out; }
.sub-enter-from, .sub-leave-to { opacity: 0; transform: translateY(12px); }
.sub-pop-enter-active, .sub-pop-leave-active { transition: opacity 180ms ease-out, transform 180ms ease-out; }
.sub-pop-enter-from, .sub-pop-leave-to { opacity: 0; transform: translate(-50%, -48%) scale(0.98); }
.sub-fade-enter-active, .sub-fade-leave-active { transition: opacity 180ms ease-out; }
.sub-fade-enter-from, .sub-fade-leave-to { opacity: 0; }
@media (prefers-reduced-motion: reduce) { .sub-enter-active, .sub-leave-active, .sub-pop-enter-active, .sub-pop-leave-active, .sub-fade-enter-active, .sub-fade-leave-active { transition: none; } }

@media (max-width: 640px) {
  /* 自动弹出的小卡片：从底部升起 */
  .sub-card:not(.centered) { inset-inline: 0; inset-block-end: 0; inline-size: 100%; max-block-size: 85svh; border-radius: var(--box) var(--box) 0 0; border-inline: 0; border-block-end: 0; padding: 20px 20px calc(16px + env(safe-area-inset-bottom)); }
  .sub-card.centered { padding: 22px 16px 18px; max-block-size: calc(100svh - 24px); }
  .sub-grid { --cell: 27px; font-size: 12px; }
  .cell button { inline-size: 26px; }
  .row-h button { padding-inline: 4px; }
}
</style>
