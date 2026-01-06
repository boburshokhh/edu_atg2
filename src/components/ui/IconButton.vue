<template>
  <button
    :class="[
      'p-2.5 min-w-10 min-h-10 rounded-lg transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
      'focus:outline-none',
      variantClasses,
      disabled && 'opacity-50 cursor-not-allowed'
    ]"
    :disabled="disabled"
    :aria-label="ariaLabel || icon"
    :title="title"
    @click="$emit('click', $event)"
  >
    <span 
      class="material-symbols-outlined"
      :class="iconSizeClass"
    >
      {{ icon }}
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'default', // 'default' | 'primary' | 'ghost'
    validator: (value) => ['default', 'primary', 'ghost'].includes(value)
  },
  size: {
    type: String,
    default: 'md', // 'sm' | 'md' | 'lg'
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['click'])

const variantClasses = computed(() => {
  const variants = {
    default: 'text-slate-500 hover:bg-slate-100',
    primary: 'text-primary bg-primary/10 hover:bg-primary/20',
    ghost: 'text-slate-500 hover:bg-slate-50'
  }
  return variants[props.variant] || variants.default
})

const iconSizeClass = computed(() => {
  const sizes = {
    sm: 'text-[18px]',
    md: 'text-[20px] md:text-[24px]',
    lg: 'text-[28px]'
  }
  return sizes[props.size] || sizes.md
})
</script>

