<template>
  <button
    :class="[
      'px-3 py-1.5 md:px-4 md:py-2 min-h-10 rounded-lg text-xs md:text-sm font-medium',
      'transition-colors shadow-sm hover:shadow active:scale-95 transform duration-100',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      variantClasses,
      disabled && 'opacity-50 cursor-not-allowed'
    ]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // 'primary' | 'secondary' | 'success' | 'ghost'
    validator: (value) => ['primary', 'secondary', 'success', 'ghost'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-primary hover:bg-blue-600 text-white focus:ring-primary',
    secondary: 'bg-slate-200 hover:bg-slate-300 text-slate-700 focus:ring-slate-400',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-100 hover:bg-emerald-100 focus:ring-emerald-400',
    ghost: 'bg-transparent hover:bg-slate-100 text-slate-700 focus:ring-slate-400'
  }
  return variants[props.variant] || variants.primary
})
</script>

