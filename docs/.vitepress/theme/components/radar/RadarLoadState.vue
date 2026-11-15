<script setup>
defineProps({ loading: Boolean, error: String })
defineEmits(['retry'])
</script>

<template>
  <p v-if="loading" class="radar-load-state" role="status">正在读取论文数据…</p>
  <div v-else-if="error" class="radar-load-state" role="alert">
    <p>暂时无法读取数据。{{ error }}</p>
    <button type="button" @click="$emit('retry')">重新加载</button>
  </div>
</template>

<style scoped>
.radar-load-state { padding: 28px 0; color: var(--muted); }
button { margin-top: 12px; padding: 8px 18px; border-radius: var(--radius); background: var(--ink); color: var(--bg); }
</style>
