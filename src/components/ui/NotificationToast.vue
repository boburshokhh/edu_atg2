<template>
  <div 
    class="notification-toast relative w-full max-w-md overflow-hidden rounded-xl shadow-2xl ring-1 ring-black/5 p-4 mb-4 transform transition-all duration-300 ease-in-out hover:translate-x-1 border-l-4"
    :class="containerClass"
  >
    <!-- Прогресс бар времени жизни -->
    <div 
      v-if="notification.duration > 0"
      class="absolute bottom-0 left-0 h-1 transition-all ease-linear opacity-60"
      :class="progressColorClass"
      :style="{ width: progressWidth + '%' }"
    />

    <div class="flex items-start gap-4">
      <!-- Иконка -->
      <div class="flex-shrink-0">
        <component 
          :is="iconComponent" 
          class="h-8 w-8" 
          :class="iconColorClass" 
          aria-hidden="true" 
        />
      </div>

      <!-- Контент -->
      <div class="flex-1 pt-0.5">
        <p
          v-if="notification.title"
          class="text-base font-bold text-gray-900 mb-1"
        >
          {{ notification.title }}
        </p>
        <p class="text-sm text-gray-700 font-medium leading-relaxed">
          {{ notification.message }}
        </p>

        <!-- Кнопки действий -->
        <div
          v-if="notification.actions && notification.actions.length"
          class="mt-4 flex flex-wrap gap-3"
        >
          <button
            v-for="(action, idx) in notification.actions"
            :key="idx"
            class="inline-flex items-center px-4 py-2 border text-sm font-semibold rounded-lg shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 transform active:scale-95"
            :class="getActionClass(action)"
            @click="handleAction(action)"
          >
            {{ action.label }}
          </button>
        </div>
      </div>

      <!-- Кнопка закрытия -->
      <div class="flex-shrink-0 -mt-1 -mr-1">
        <button
          class="rounded-lg p-1.5 inline-flex text-gray-400 hover:text-gray-600 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
          @click="$emit('close')"
        >
          <span class="sr-only">Закрыть</span>
          <svg
            class="h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
// Используем Solid иконки для большей заметности
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  InformationCircleIcon, 
  XCircleIcon 
} from '@heroicons/vue/24/solid'

const props = defineProps({
  notification: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

// Логика прогресс бара
const progressWidth = ref(100)
let progressInterval

onMounted(() => {
  if (props.notification.duration > 0) {
    const step = 100 / (props.notification.duration / 50) // более плавная анимация (50мс)
    progressInterval = setInterval(() => {
      progressWidth.value -= step
      if (progressWidth.value <= 0) {
        clearInterval(progressInterval)
      }
    }, 50)
  }
})

onUnmounted(() => {
  if (progressInterval) clearInterval(progressInterval)
})

const handleAction = (action) => {
  if (action.onClick) action.onClick()
  emit('close')
}

// Стили контейнера (фон и бордер)
const containerClass = computed(() => {
  switch (props.notification.type) {
    case 'success': return 'bg-green-50 border-green-500'
    case 'error': return 'bg-red-50 border-red-500'
    case 'warning': return 'bg-amber-50 border-amber-500'
    default: return 'bg-blue-50 border-blue-500'
  }
})

// Иконки (Solid)
const iconComponent = computed(() => {
  switch (props.notification.type) {
    case 'success': return CheckCircleIcon
    case 'error': return XCircleIcon
    case 'warning': return ExclamationCircleIcon
    default: return InformationCircleIcon
  }
})

// Цвет иконок
const iconColorClass = computed(() => {
  switch (props.notification.type) {
    case 'success': return 'text-green-600'
    case 'error': return 'text-red-600'
    case 'warning': return 'text-amber-600'
    default: return 'text-blue-600'
  }
})

// Цвет прогресс бара
const progressColorClass = computed(() => {
  switch (props.notification.type) {
    case 'success': return 'bg-green-600'
    case 'error': return 'bg-red-600'
    case 'warning': return 'bg-amber-600'
    default: return 'bg-blue-600'
  }
})

// Стили кнопок
const getActionClass = (action) => {
  if (action.variant === 'outline') {
    return 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900 ring-1 ring-black/5'
  }
  
  switch (props.notification.type) {
    case 'success': return 'bg-green-600 hover:bg-green-700 text-white border-transparent focus:ring-green-500'
    case 'error': return 'bg-red-600 hover:bg-red-700 text-white border-transparent focus:ring-red-500'
    case 'warning': return 'bg-amber-600 hover:bg-amber-700 text-white border-transparent focus:ring-amber-500'
    default: return 'bg-blue-600 hover:bg-blue-700 text-white border-transparent focus:ring-blue-500'
  }
}
</script>
