<template>
  <aside
    :class="[
      'fixed lg:relative inset-y-0 z-40',
      'w-full max-w-sm lg:w-80 flex flex-col',
      'border-l border-slate-200',
      'bg-white',
      'transition-transform duration-300 ease-in-out',
      isOpen ? 'translate-x-0' : 'translate-x-full lg:hidden',
      'h-full flex-shrink-0 shadow-sm',
      additionalClasses
    ]"
  >
    <!-- Header -->
    <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
      <h3 class="text-[#111418] text-base font-bold">
        <slot name="header" />
      </h3>
      <button
        v-if="showCloseButton"
        @click="$emit('close')"
        class="text-slate-400 hover:text-slate-600 transition-colors lg:hidden p-2 min-w-10 min-h-10"
        aria-label="Закрыть"
      >
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <slot />
    </div>

    <!-- Footer (optional) -->
    <div v-if="$slots.footer" class="border-t border-slate-100">
      <slot name="footer" />
    </div>
  </aside>
</template>

<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: true
  },
  showCloseButton: {
    type: Boolean,
    default: true
  },
  additionalClasses: {
    type: String,
    default: ''
  }
})

defineEmits(['close'])
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>

