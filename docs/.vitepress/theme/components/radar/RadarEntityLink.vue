<script setup>
import { computed } from 'vue'
import { entityUrl } from './sectionData.js'
const props = defineProps({ kind: { type: String, default: 'institution' }, item: { type: Object, required: true } })
const href = computed(() => entityUrl(props.kind, props.item.page))
</script>
<!-- These query-driven detail pages must reload when only ?id changes. VitePress 1.x
     keeps route.path unchanged in that case; an explicit target preserves native navigation. -->
<template><a v-if="href" :href="href" target="_self">{{ item.name }}</a><span v-else>{{ item.name }}</span></template>
