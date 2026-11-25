// "一键订阅"的状态：谁打开了订阅卡片、读者在站内累计看了多久、是否已经弹过。
// 只用 localStorage，不用 cookie；存的只是秒数和"已经弹过/已订阅"，不存邮箱。
import { reactive } from 'vue'

export const AUTO_AFTER_SECONDS = 45
const KEY_SECONDS = 'iqf-subscribe-seconds'
const KEY_DONE = 'iqf-subscribe-done' // 'shown' | 'dismissed' | 'subscribed'

export const subscribeState = reactive({ open: false, source: '' })

const read = (k) => { try { return localStorage.getItem(k) } catch { return null } }
const write = (k, v) => { try { localStorage.setItem(k, v) } catch { /* private mode: just no memory */ } }

export function openSubscribe(source = 'header') {
  subscribeState.source = source
  subscribeState.open = true
}

export function closeSubscribe() {
  subscribeState.open = false
  if (read(KEY_DONE) !== 'subscribed') write(KEY_DONE, 'dismissed')
}

export function markSubscribed() {
  write(KEY_DONE, 'subscribed')
}

// 站内累计计时：只在页面可见时计数，换页、刷新都接着算；到 45 秒弹一次，之后再也不自动弹。
export function installSubscribeTimer(seconds = AUTO_AFTER_SECONDS) {
  if (typeof window === 'undefined' || read(KEY_DONE)) return
  let total = Number(read(KEY_SECONDS)) || 0
  const tick = setInterval(() => {
    if (document.visibilityState !== 'visible') return
    total += 1
    if (total % 5 === 0) write(KEY_SECONDS, String(total))
    if (total >= seconds) {
      clearInterval(tick)
      write(KEY_SECONDS, String(total))
      if (read(KEY_DONE)) return
      write(KEY_DONE, 'shown')
      if (!subscribeState.open) openSubscribe('auto')
    }
  }, 1000)
}
