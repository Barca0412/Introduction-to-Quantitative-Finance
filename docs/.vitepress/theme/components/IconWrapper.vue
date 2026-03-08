<template>
  <component :is="iconComponent" :size="size" :color="color" :strokeWidth="strokeWidth" />
</template>

<script setup>
import { computed } from 'vue'
import * as LucideIcons from 'lucide-vue-next'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: Number,
    default: 16
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  strokeWidth: {
    type: Number,
    default: 2
  }
})

// Convert kebab-case to PascalCase (e.g., "file-text" -> "FileText")
const toPascalCase = (str) => {
  return str
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('')
}

const iconComponent = computed(() => {
  const componentName = toPascalCase(props.name)
  return LucideIcons[componentName] || LucideIcons.Circle
})
</script>
