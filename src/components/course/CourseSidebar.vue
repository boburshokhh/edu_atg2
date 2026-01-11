<template>
  <div class="sticky top-28 space-y-6">
    <!-- Video Player Card -->
    <div
      v-if="sidebarVideoUrl"
      class="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 overflow-hidden"
    >
      <h3 class="text-sm font-bold text-gray-900 mb-3 uppercase tracking-wide">
        Видео
      </h3>
      <div
        class="relative w-full rounded-lg overflow-hidden bg-black"
        style="aspect-ratio: 16/9;"
      >
        <video
          ref="sidebarVideoPlayer"
          class="w-full h-full"
          :src="sidebarVideoUrl"
          controls
          preload="metadata"
          playsinline
          crossorigin="anonymous"
          @error="handleVideoError"
        >
          Ваш браузер не поддерживает воспроизведение видео.
        </video>
        <div
          v-if="loadingSidebarVideo"
          class="absolute inset-0 bg-black/50 flex items-center justify-center"
        >
          <div class="text-white text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2" />
            <p class="text-xs">
              Загрузка видео...
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Enrollment Card -->
    <el-card
      class="enrollment-card"
      shadow="always"
    >
      <div class="enrollment-card-content">
        <el-button 
          type="primary"
          size="large"
          class="start-learning-btn"
          @click="$emit('start-learning')"
        >
          <template #icon>
            <PlayCircleIcon class="w-5 h-5" />
          </template>
          Начать обучение
        </el-button>

        <el-divider />
        
        <div class="enrollment-info">
          <div class="enrollment-info-item">
            <div class="enrollment-info-label">
              <ClockIcon class="w-4 h-4" />
              <span>Формат</span>
            </div>
            <span class="enrollment-info-value">Онлайн</span>
          </div>
          
          <el-divider />
          
          <div class="enrollment-info-item">
            <div class="enrollment-info-label">
              <BookOpenIcon class="w-4 h-4" />
              <span>Доступ</span>
            </div>
            <span class="enrollment-info-value">Навсегда</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ClockIcon, PlayCircleIcon, BookOpenIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'CourseSidebar',
  components: {
    ClockIcon,
    PlayCircleIcon,
    BookOpenIcon
  },
  props: {
    sidebarVideoUrl: {
      type: String,
      default: null
    },
    loadingSidebarVideo: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start-learning', 'video-error'],
  setup(props, { emit }) {
    const sidebarVideoPlayer = ref(null)

    const handleVideoError = (event) => {
      console.error('Ошибка воспроизведения видео:', event)
      emit('video-error', event)
    }

    return {
      sidebarVideoPlayer,
      handleVideoError
    }
  }
}
</script>

<style scoped>
/* Enrollment Card Styles */
.enrollment-card {
  border: 2px solid #3b82f6;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
}

.enrollment-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 128px;
  height: 128px;
  background: #3b82f6;
  opacity: 0.1;
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.enrollment-card-content {
  position: relative;
  z-index: 1;
}

.start-learning-btn {
  width: 100%;
  margin-bottom: 24px;
  font-weight: 700;
  font-size: 16px;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.start-learning-btn:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.enrollment-info {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.enrollment-info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.enrollment-info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.enrollment-info-value {
  font-weight: 700;
  color: #111827;
  font-size: 14px;
}

:deep(.el-divider) {
  margin: 12px 0;
}
</style>

