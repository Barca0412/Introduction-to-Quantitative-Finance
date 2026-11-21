<script setup>
// 订阅卡片：右上角"一键订阅"和站内看满 45 秒自动弹出，都打开这一张。
// 提交到 /api/subscribe/（服务器上的 scripts/site/subscribe/subscribe_server.py），双重确认：先发确认信。
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { withBase } from 'vitepress'
import GitHubStar from './GitHubStar.vue'
import { closeSubscribe, markSubscribed, subscribeState } from '../subscribe.js'
import { track } from '../analytics.js'

// 雷达的金融领域（scripts/arxiv_radar/vocab/taxonomy.yaml），去掉"通用金融"
const DOMAINS = [
  ['asset-pricing', '资产定价与因子'], ['trading', '交易与执行'], ['portfolio-risk', '组合与风险'],
  ['derivatives', '衍生品'], ['credit-banking', '信用、银行与支付'], ['corporate-finance', '公司金融与会计'],
  ['fin-nlp', '金融文本与舆情'], ['crypto-defi', '加密资产'], ['macro-policy', '宏观与政策'],
  ['insurance-household', '保险与个人金融'], ['market-structure', '市场结构与行为'],
]
const MAX = 3
// 公众号二维码：图片放到 docs/public/subscribe/wechat-qr.png 后把这里改成 true
const HAS_WECHAT_QR = false

const email = ref('')
const website = ref('') // 陷阱字段，真人看不到
const picked = ref([])
const showDomains = ref(false)
const state = ref('idle') // idle | sending | done | error
const error = ref('')
const input = ref(null)
const card = ref(null)

const open = computed(() => subscribeState.open)
const endpoint = () => {
  const h = location.hostname
  if (h.endsWith('github.io')) return 'https://quant.hfthnu.com/api/subscribe/'
  if (h === 'localhost' || h === '127.0.0.1') return 'http://127.0.0.1:8731/api/subscribe/'
  return withBase('/api/subscribe/')
}

function toggle(id) {
  const i = picked.value.indexOf(id)
  if (i >= 0) picked.value.splice(i, 1)
  else if (picked.value.length < MAX) picked.value.push(id)
}

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
  track('subscribe-submit', { source: subscribeState.source, domains: picked.value.length })
  try {
    const res = await fetch(endpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value.trim(), domains: picked.value, website: website.value }),
    })
    const body = await res.json().catch(() => ({}))
    if (!res.ok || !body.ok) throw new Error(body.error || 'failed')
    state.value = 'done'
    markSubscribed()
  } catch (e) {
    state.value = 'error'
    error.value = MESSAGES[e.message] || '网络好像出了点问题，请稍后再试。'
  }
}

function onKey(e) { if (e.key === 'Escape' && open.value) closeSubscribe() }

watch(open, async (v) => {
  if (!v) return
  track('subscribe-shown', { source: subscribeState.source })
  if (state.value !== 'done') { state.value = 'idle'; error.value = '' }
  await nextTick()
  // 读者自己点开的才把光标放进邮箱框；自动弹出的不抢焦点
  if (subscribeState.source !== 'auto') input.value?.focus()
})
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <Transition name="sub">
    <section v-if="open" ref="card" class="sub-card" role="dialog" aria-modal="false" aria-labelledby="sub-title">
      <button type="button" class="sub-close" aria-label="关闭" @click="closeSubscribe">×</button>
      <template v-if="state !== 'done'">
        <h2 id="sub-title" class="sub-title"><i class="sub-dot" aria-hidden="true"></i>每周一，3 分钟读完全球 AI × 金融</h2>
        <p class="sub-lead">产业动态 · 监管政策 · 值得读的研究，一封邮件读完。随时可以退订。</p>
        <form class="sub-form" novalidate @submit.prevent="submit">
          <label class="sr-only" for="sub-email">邮箱</label>
          <input id="sub-email" ref="input" v-model="email" type="email" inputmode="email" autocomplete="email" placeholder="你的邮箱" maxlength="254" required>
          <input v-model="website" class="sub-trap" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
          <button type="submit" class="btn btn-accent sub-submit" :disabled="state === 'sending'">{{ state === 'sending' ? '提交中…' : '订阅' }}</button>
        </form>
        <p v-if="error" class="sub-error" role="alert">{{ error }}</p>
        <button type="button" class="sub-more" :aria-expanded="showDomains" @click="showDomains = !showDomains">更关心哪些方向？（可选，最多 3 个）</button>
        <div v-if="showDomains" class="sub-domains" role="group" aria-label="关心的方向">
          <button v-for="[id, name] in DOMAINS" :key="id" type="button" class="chip" :aria-pressed="picked.includes(id)" :disabled="!picked.includes(id) && picked.length >= MAX" @click="toggle(id)">{{ name }}</button>
        </div>
        <div v-if="HAS_WECHAT_QR" class="sub-wechat">
          <img :src="withBase('/subscribe/wechat-qr.png')" alt="湖南大学金融科技协会公众号二维码" width="88" height="88">
          <p>不想留邮箱？<br>扫码关注协会公众号，每周同步推送。</p>
        </div>
      </template>
      <template v-else>
        <h2 id="sub-title" class="sub-title"><i class="sub-dot" aria-hidden="true"></i>还差一步：去邮箱点确认</h2>
        <p class="sub-lead">确认信已经发到 <strong>{{ email.trim() }}</strong>。点信里的链接就订阅好了；没收到的话，看看垃圾邮件。</p>
      </template>
      <div class="sub-foot">
        <div class="sub-star"><GitHubStar /><span>觉得有用，去点个 Star</span></div>
        <p>欢迎交流 AI + 金融的新想法和需求，也欢迎<a :href="withBase('/contact')">参与贡献</a>。</p>
      </div>
    </section>
  </Transition>
</template>

<style scoped>
.sub-card { position: fixed; inset-inline-end: 24px; inset-block-end: 24px; z-index: 60; inline-size: min(400px, calc(100vw - 48px)); max-block-size: calc(100svh - 48px); overflow-y: auto; padding: 24px 24px 20px; background: var(--bg); color: var(--ink); border: 1px solid var(--rule); border-radius: var(--box); box-shadow: 0 18px 48px rgba(13, 42, 28, 0.16); }
.sub-close { position: absolute; inset-block-start: 10px; inset-inline-end: 10px; inline-size: 36px; block-size: 36px; border-radius: 50%; font-size: 22px; line-height: 1; color: var(--muted); }
.sub-close:hover { background: var(--surface); color: var(--ink); }
.sub-title { display: flex; gap: 10px; align-items: baseline; text-wrap: balance; padding-inline-end: 28px; font-size: 1.1875rem; font-weight: 700; line-height: 1.35; letter-spacing: -0.01em; }
.sub-dot { flex: none; inline-size: 11px; block-size: 11px; border-radius: 50%; background: var(--accent); border: 1.5px solid var(--ink); transform: translateY(-1px); }
.sub-lead { margin-block-start: 8px; color: var(--muted); font-size: 0.9375rem; line-height: 1.6; }
.sub-lead strong { color: var(--ink); font-weight: 600; word-break: break-all; }
.sub-form { display: flex; gap: 8px; margin-block-start: 16px; }
.sub-form input[type="email"] { flex: 1; min-inline-size: 0; block-size: 44px; padding-inline: 16px; border: 1px solid var(--control); border-radius: var(--radius); background: #fff; color: var(--ink); font-size: 1rem; }
.sub-form input[type="email"]:focus-visible { outline: 2px solid var(--focus); outline-offset: 1px; }
.sub-submit { block-size: 44px; padding-inline: 20px; }
.sub-submit:disabled { opacity: 0.6; }
.sub-trap { position: absolute; inline-size: 1px; block-size: 1px; opacity: 0; pointer-events: none; }
.sub-error { margin-block-start: 8px; color: #9a2b13; font-size: var(--step-small); }
.sub-more { margin-block-start: 12px; min-block-size: 32px; color: var(--muted); font-size: var(--step-small); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; }
.sub-more:hover { color: var(--ink); }
.sub-domains { display: flex; flex-wrap: wrap; gap: 6px; margin-block-start: 6px; }
.chip { min-block-size: 32px; padding-inline: 12px; border-radius: var(--radius); background: var(--surface); color: var(--ink); font-size: var(--step-small); }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); font-weight: 600; }
.chip:disabled { opacity: 0.45; }
.sub-wechat { display: flex; gap: 14px; align-items: center; margin-block-start: 16px; padding-block-start: 16px; border-block-start: 1px solid var(--rule); font-size: var(--step-small); color: var(--muted); }
.sub-wechat img { border-radius: var(--fig-radius); background: #fff; }
.sub-foot { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; margin-block-start: 18px; padding-block-start: 16px; border-block-start: 1px solid var(--rule); }
.sub-star { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: var(--step-small); }
.sub-foot p { color: var(--muted); font-size: var(--step-small); line-height: 1.6; }
.sub-foot p a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--control); text-underline-offset: 4px; }
.sr-only { position: absolute; inline-size: 1px; block-size: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.sub-enter-active, .sub-leave-active { transition: opacity 180ms ease-out, transform 180ms ease-out; }
.sub-enter-from, .sub-leave-to { opacity: 0; transform: translateY(12px); }
@media (prefers-reduced-motion: reduce) { .sub-enter-active, .sub-leave-active { transition: none; } }
/* 手机：从底部升起，占满宽度 */
@media (max-width: 640px) {
  .sub-card { inset-inline: 0; inset-block-end: 0; inline-size: 100%; max-block-size: 85svh; border-radius: var(--box) var(--box) 0 0; border-inline: 0; border-block-end: 0; padding: 20px 20px calc(16px + env(safe-area-inset-bottom)); }
}
</style>
