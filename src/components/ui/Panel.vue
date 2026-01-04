<template>
  <div
    :class="[
      'bg-white rounded-lg shadow-2xl',
      paddingClass,
      additionalClasses
    ]"
  >
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  padding: {
    type: String,
    default: 'md', // 'none' | 'sm' | 'md' | 'lg'
    validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
  },
  additionalClasses: {
    type: String,
    default: ''
  }
})

const paddingClass = computed(() => {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-8 sm:p-12',
    lg: 'p-12 sm:p-16'
  }
  return paddings[props.padding] || paddings.md
})
</script>

