<template>
  <div class="date-filter">
    <span class="filter-label">Date:</span>
    <select v-model="selectedDate" class="date-select" @change="emitFilter">
      <option value="">All Dates</option>
      <option v-for="date in uniqueDates" :key="date" :value="date">
        {{ formatDate(date) }}
      </option>
    </select>
    <button v-if="selectedDate" class="clear-btn" @click="clear">
      Clear
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  papers: {
    type: Array,
    required: true
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['filter', 'update:modelValue'])
const selectedDate = ref(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    selectedDate.value = value || ''
  }
)

const uniqueDates = computed(() => {
  const dates = new Set()
  props.papers.forEach((paper) => {
    if (paper.published_date) {
      dates.add(String(paper.published_date).slice(0, 10))
    }
  })
  return Array.from(dates).sort().reverse()
})

const emitFilter = () => {
  emit('update:modelValue', selectedDate.value)
  emit('filter', selectedDate.value)
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric'
  })
}

const clear = () => {
  selectedDate.value = ''
  emitFilter()
}
</script>

<style scoped>
.date-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.date-select {
  padding: 0.5rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background-color: white;
  cursor: pointer;
  min-width: 180px;
}

.date-select:focus {
  outline: none;
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.clear-btn {
  padding: 0.45rem 0.8rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  color: #dc2626;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.clear-btn:hover {
  background: #fecaca;
}
</style>
