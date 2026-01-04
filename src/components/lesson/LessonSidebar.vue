<template>
  <aside
    :class="[
      'w-[340px] flex flex-col border-r border-slate-200 bg-white h-full flex-shrink-0 z-20 shadow-sm',
      isMobile ? 'sidebar-mobile' : 'sidebar-desktop'
    ]"
  >
    <!-- Course Header with Progress -->
    <div
      class="px-6 py-6 border-b border-slate-100 flex-shrink-0 bg-white"
    >
      <h1 class="text-[#111418] text-xl font-bold leading-tight tracking-tight mb-4">
        {{ courseTitle || 'Курс обучения' }}
      </h1>
      <div class="flex flex-col gap-2">
        <div class="flex justify-between items-end">
          <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider">
            Прогресс курса
          </p>
          <p class="text-[#111418] text-sm font-bold">{{ courseProgress }}%</p>
        </div>
        <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
          <div class="h-full rounded-full bg-primary" :style="{ width: `${courseProgress}%` }"></div>
        </div>
        <p class="text-slate-500 text-xs mt-1">{{ completedCount }}/{{ totalCount }} Уроков завершено</p>
      </div>
    </div>

    <!-- Lessons List -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-3 flex flex-col">
      <details
        v-for="(lesson, lessonIndex) in lessons"
        :key="lessonIndex"
        class="group mb-1"
        :open="expandedLessons.includes(lessonIndex)"
      >
        <summary
          class="flex cursor-pointer items-center justify-between py-2 px-2 rounded-lg hover:bg-slate-50 transition-colors select-none"
          @click.prevent="toggleLesson(lessonIndex)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex items-center justify-center w-6 h-6 rounded bg-slate-100 text-xs font-bold text-slate-600"
            >
              {{ lessonIndex + 1 }}
            </div>
            <span class="text-sm font-bold text-slate-800 leading-none">
              {{ lesson.title }}
            </span>
          </div>
          <span
            class="material-symbols-outlined text-slate-400 transition-transform text-[20px]"
            :class="{ 'rotate-180': expandedLessons.includes(lessonIndex) }"
          >
            expand_more
          </span>
        </summary>
        <div
          class="pl-3 border-l-2 border-slate-100 ml-3 pb-2 mt-1 flex flex-col gap-1"
        >
          <details
            v-for="(topic, topicIndex) in lesson.topics"
            :key="topicIndex"
            class="group/topic"
            :open="expandedTopics[`${lessonIndex}-${topicIndex}`] || isCurrentTopic(lessonIndex, topicIndex)"
          >
            <summary
              class="flex cursor-pointer items-center justify-between py-2 px-2 rounded-md hover:bg-slate-50 transition-colors select-none"
              @click.prevent="toggleTopic(lessonIndex, topicIndex)"
            >
              <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {{ lessonIndex + 1 }}.{{ topicIndex + 1 }} {{ topic.title }}
              </span>
              <span
                class="material-symbols-outlined text-slate-400 transition-transform text-[18px]"
                :class="{ 'rotate-180': expandedTopics[`${lessonIndex}-${topicIndex}`] || isCurrentTopic(lessonIndex, topicIndex) }"
              >
                expand_more
              </span>
            </summary>
            <div class="flex flex-col gap-1 pl-2 mt-1">
              <!-- Files in topic -->
              <template v-if="(topic.files || []).length > 0">
                <div
                  v-for="(file, fileIndex) in (topic.files || [])"
                  :key="`file-${file.id || fileIndex}`"
                  :class="[
                    'flex items-start justify-between p-2 rounded-md cursor-pointer transition-colors',
                    isCurrentFile(lessonIndex, topicIndex, file)
                      ? 'bg-primary/10 border border-primary/20 shadow-sm'
                      : 'hover:bg-slate-50 group/item'
                  ]"
                  @click="selectFile(lessonIndex, topicIndex, file)"
                >
                <div
                  :class="[
                    'flex items-start gap-3',
                    isCurrentFile(lessonIndex, topicIndex, file)
                      ? ''
                      : 'opacity-75 group-hover/item:opacity-100 transition-opacity'
                  ]"
                >
                  <span
                    class="material-symbols-outlined text-[20px] mt-0.5"
                    :class="
                      isCurrentFile(lessonIndex, topicIndex, file)
                        ? 'text-primary'
                        : 'text-slate-400 group-hover/item:text-slate-600'
                    "
                  >
                    {{ getFileIcon(file) }}
                  </span>
                  <div class="flex flex-col">
                    <span
                      :class="[
                        'text-sm leading-snug',
                        isCurrentFile(lessonIndex, topicIndex, file)
                          ? 'font-semibold text-primary'
                          : 'font-medium text-slate-600 group-hover/item:text-slate-900 transition-colors'
                      ]"
                    >
                      {{ file.originalName || file.original_name || file.fileName || file.file_name || 'Файл' }}
                    </span>
                    <span
                      :class="[
                        'text-[11px] mt-0.5',
                        isCurrentFile(lessonIndex, topicIndex, file)
                          ? 'text-primary/70 font-medium'
                          : 'text-slate-400'
                      ]"
                    >
                      {{ getFileLabel(file) }} • {{ formatDuration(file) }}
                    </span>
                  </div>
                </div>
                <div v-if="isCurrentFile(lessonIndex, topicIndex, file)" class="w-1.5 h-1.5 rounded-full bg-primary mt-2 mr-1"></div>
                <span
                  v-else-if="isFileCompleted(lessonIndex, topicIndex, file)"
                  class="material-symbols-outlined text-emerald-500 text-[18px] mt-0.5"
                >
                  check
                </span>
                </div>
              </template>
              <div
                v-else
                class="px-2 py-1 text-xs text-slate-400"
              >
                Нет материалов
              </div>
            </div>
          </details>

          <!-- Lesson Test -->
          <div
            :class="[
              'flex items-start justify-between p-2 rounded-md cursor-pointer transition-colors border-t border-slate-200 mt-1',
              isCurrentTest(lessonIndex)
                ? 'bg-purple-50 border-purple-200'
                : 'hover:bg-slate-50'
            ]"
            @click="selectTest(lessonIndex)"
          >
            <div class="flex items-start gap-3">
              <span
                class="material-symbols-outlined text-[20px] mt-0.5"
                :class="isCurrentTest(lessonIndex) ? 'text-purple-600' : 'text-slate-400'"
              >
                description
              </span>
              <div class="flex flex-col">
                <span
                  :class="[
                    'text-sm font-medium leading-snug',
                    isCurrentTest(lessonIndex) ? 'text-purple-600' : 'text-slate-600'
                  ]"
                >
                  Тест модуля {{ lessonIndex + 1 }}
                </span>
                <span class="text-[11px] text-slate-400 mt-0.5">Проверка знаний</span>
              </div>
            </div>
            <span
              v-if="isLessonTestPassed(lessonIndex)"
              class="material-symbols-outlined text-emerald-500 text-[18px] mt-0.5"
            >
              check
            </span>
          </div>
        </div>
      </details>
    </div>

    <!-- User Profile -->
    <div class="p-4 border-t border-slate-100 bg-slate-50">
      <div class="flex items-center gap-3">
        <div
          class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold text-xs"
        >
          {{ userInitials }}
        </div>
        <div class="flex flex-col">
          <p class="text-xs font-medium text-slate-900">{{ userName }}</p>
          <p class="text-[10px] text-slate-500">{{ userRole }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import authService from '@/services/auth'

const props = defineProps({
  lessons: {
    type: Array,
    default: () => []
  },
  currentLessonIndex: {
    type: Number,
    default: 0
  },
  currentTopicIndex: {
    type: Number,
    default: 0
  },
  currentFile: {
    type: Object,
    default: null
  },
  completedTopics: {
    type: Set,
    default: () => new Set()
  },
  passedTests: {
    type: Set,
    default: () => new Set()
  },
  isTestMode: {
    type: Boolean,
    default: false
  },
  courseTitle: {
    type: String,
    default: ''
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-lesson', 'select-test', 'select-file', 'toggle-sidebar'])

const expandedLessons = ref([props.currentLessonIndex])
const expandedTopics = ref({})

// User data
const userDataVersion = ref(0)
const userName = computed(() => {
  userDataVersion.value
  const user = authService.getCurrentUser()
  if (user) {
    return user.full_name || user.username || 'Пользователь'
  }
  return 'Пользователь'
})

const userInitials = computed(() => {
  const name = userName.value
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.charAt(0).toUpperCase()
})

const userRole = computed(() => {
  userDataVersion.value
  const user = authService.getCurrentUser()
  const role = user ? user.role : 'user'
  const roles = {
    admin: 'Администратор',
    instructor: 'Инструктор',
    user: 'Студент'
  }
  return roles[role] || 'Студент'
})

// Course progress
const totalCount = computed(() => {
  let total = 0
  props.lessons.forEach(lesson => {
    total += lesson.topics?.length || 0
  })
  return total
})

const completedCount = computed(() => {
  return props.completedTopics.size
})

const courseProgress = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

// Methods
const toggleLesson = (index) => {
  const idx = expandedLessons.value.indexOf(index)
  if (idx > -1) {
    expandedLessons.value.splice(idx, 1)
  } else {
    expandedLessons.value.push(index)
  }
}

const toggleTopic = (lessonIndex, topicIndex) => {
  const key = `${lessonIndex}-${topicIndex}`
  expandedTopics.value[key] = !expandedTopics.value[key]
}

const selectTopic = (lessonIndex, topicIndex) => {
  emit('select-lesson', { lessonIndex, topicIndex })
}

const selectFile = (lessonIndex, topicIndex, file) => {
  emit('select-file', { lessonIndex, topicIndex, file })
}

const selectTest = (lessonIndex) => {
  emit('select-test', { lessonIndex })
}

const isCurrentTopic = (lessonIndex, topicIndex) => {
  return lessonIndex === props.currentLessonIndex && topicIndex === props.currentTopicIndex && !props.isTestMode
}

const isCurrentTest = (lessonIndex) => {
  return lessonIndex === props.currentLessonIndex && props.isTestMode
}

const isCurrentFile = (lessonIndex, topicIndex, file) => {
  if (!props.currentFile) return false
  if (lessonIndex !== props.currentLessonIndex || topicIndex !== props.currentTopicIndex) return false
  if (props.isTestMode) return false
  
  const fileKey = file.objectName || file.object_key || file.objectKey
  const currentKey = props.currentFile.objectName || props.currentFile.object_key || props.currentFile.objectKey
  
  return fileKey === currentKey
}

const isFileCompleted = (lessonIndex, topicIndex, file) => {
  // Можно добавить логику для отслеживания завершенных файлов
  return false
}

const isLessonTestPassed = (lessonIndex) => {
  const testId = `test-module-${lessonIndex + 1}`
  return props.passedTests.has(testId)
}

const getFileIcon = (file) => {
  const fileType = (file.fileType || file.file_type || '').toLowerCase()
  const fileName = (file.originalName || file.original_name || file.fileName || file.file_name || '').toLowerCase()
  
  if (fileType === 'video' || fileName.endsWith('.mp4') || fileName.endsWith('.webm') || fileName.endsWith('.mov')) {
    return 'play_circle'
  }
  if (fileType === 'pdf' || fileName.endsWith('.pdf')) {
    return 'picture_as_pdf'
  }
  return 'description'
}

const getFileLabel = (file) => {
  const isMain = file.isMain ?? file.is_main ?? false
  return isMain ? 'Основной материал' : 'Дополнительный материал'
}

const formatDuration = (file) => {
  // Можно добавить реальную длительность из файла
  return '5 мин'
}

// Watch for current lesson changes to auto-expand
watch(() => props.currentLessonIndex, (newIndex) => {
  if (!expandedLessons.value.includes(newIndex)) {
    expandedLessons.value.push(newIndex)
  }
  // Auto-expand current topic
  if (props.currentTopicIndex >= 0) {
    const key = `${newIndex}-${props.currentTopicIndex}`
    expandedTopics.value[key] = true
  }
}, { immediate: true })

// Refresh user data
watch(() => authService.getCurrentUser(), () => {
  userDataVersion.value++
}, { immediate: true })
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 20px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #cbd5e1;
}

details > summary {
  list-style: none;
}

details > summary::-webkit-details-marker {
  display: none;
}

/* Desktop styles */
.sidebar-desktop {
  position: sticky;
  top: 0;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
}

/* Mobile styles */
.sidebar-mobile {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 40;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}
</style>
