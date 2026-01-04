<template>
  <aside
    class="w-[340px] flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1a2632] h-full flex-shrink-0 z-20 shadow-sm"
  >
    <!-- Course Header with Progress -->
    <div
      class="px-6 py-6 border-b border-slate-100 dark:border-slate-700/50 flex-shrink-0 bg-white dark:bg-[#1a2632]"
    >
      <h1 class="text-[#111418] dark:text-white text-xl font-bold leading-tight tracking-tight mb-4">
        {{ courseTitle }}
      </h1>
      <div class="flex flex-col gap-2">
        <div class="flex justify-between items-end">
          <p class="text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
            Прогресс курса
          </p>
          <p class="text-[#111418] dark:text-white text-sm font-bold">{{ courseProgress }}%</p>
        </div>
        <div class="h-2 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
          <div class="h-full rounded-full bg-primary" :style="{ width: `${courseProgress}%` }"></div>
        </div>
        <p class="text-slate-500 dark:text-slate-400 text-xs mt-1">
          {{ completedTopicsCount }}/{{ totalTopicsCount }} {{ totalTopicsCount === 1 ? 'урок завершен' : 'уроков завершено' }}
        </p>
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
          class="flex cursor-pointer items-center justify-between py-2 px-2 rounded-lg hover:bg-slate-50 dark:hover:bg-white/5 transition-colors select-none"
          @click.prevent="toggleLesson(lessonIndex)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex items-center justify-center w-6 h-6 rounded bg-slate-100 dark:bg-slate-700 text-xs font-bold text-slate-600 dark:text-slate-300"
            >
              {{ lessonIndex + 1 }}
            </div>
            <span class="text-sm font-bold text-slate-800 dark:text-white leading-none">
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
          class="pl-3 border-l-2 border-slate-100 dark:border-slate-800 ml-3 pb-2 mt-1 flex flex-col gap-1"
        >
          <!-- Topics -->
          <details
            v-for="(topic, topicIndex) in lesson.topics"
            :key="topicIndex"
            class="group/topic"
            :open="expandedTopics.includes(`${lessonIndex}-${topicIndex}`)"
          >
            <summary
              class="flex cursor-pointer items-center justify-between py-2 px-2 rounded-md hover:bg-slate-50 dark:hover:bg-white/5 transition-colors select-none"
              @click.prevent="toggleTopic(lessonIndex, topicIndex)"
            >
              <span
                class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                {{ lessonIndex + 1 }}.{{ topicIndex + 1 }} {{ topic.title }}
              </span>
              <span
                class="material-symbols-outlined text-slate-400 transition-transform text-[18px]"
                :class="{ 'rotate-180': expandedTopics.includes(`${lessonIndex}-${topicIndex}`) }"
              >
                expand_more
              </span>
            </summary>
            <div class="flex flex-col gap-1 pl-2 mt-1">
              <!-- Files in topic -->
              <div
                v-for="(file, fileIndex) in getTopicFiles(lessonIndex, topicIndex)"
                :key="fileIndex"
                :class="[
                  'flex items-start justify-between p-2 rounded-md cursor-pointer group/item transition-colors',
                  isActiveFile(lessonIndex, topicIndex, file)
                    ? 'bg-primary/10 border border-primary/20 shadow-sm'
                    : 'hover:bg-slate-50 dark:hover:bg-white/5'
                ]"
                @click="selectFile(lessonIndex, topicIndex, file)"
              >
                <div
                  :class="[
                    'flex items-start gap-3',
                    isActiveFile(lessonIndex, topicIndex, file)
                      ? ''
                      : 'opacity-75 group-hover/item:opacity-100 transition-opacity'
                  ]"
                >
                  <span
                    class="material-symbols-outlined text-[20px] mt-0.5"
                    :class="
                      isActiveFile(lessonIndex, topicIndex, file)
                        ? 'text-primary'
                        : 'text-slate-400 group-hover/item:text-slate-600 dark:text-slate-500'
                    "
                  >
                    {{ getFileIcon(file) }}
                  </span>
                  <div class="flex flex-col">
                    <span
                      :class="[
                        'text-sm leading-snug',
                        isActiveFile(lessonIndex, topicIndex, file)
                          ? 'font-semibold text-primary'
                          : 'font-medium text-slate-600 dark:text-slate-300 group-hover/item:text-slate-900 transition-colors'
                      ]"
                    >
                      {{ file.originalName || file.original_name || file.fileName || 'Файл' }}
                    </span>
                    <span
                      :class="[
                        'text-[11px] mt-0.5 font-medium',
                        isActiveFile(lessonIndex, topicIndex, file)
                          ? 'text-primary/70'
                          : 'text-slate-400'
                      ]"
                    >
                      {{ getFileTypeLabel(file) }} • {{ topic.duration || '15 мин' }}
                    </span>
                  </div>
                </div>
                <div
                  v-if="isActiveFile(lessonIndex, topicIndex, file)"
                  class="w-1.5 h-1.5 rounded-full bg-primary mt-2 mr-1"
                ></div>
                <span
                  v-else-if="isFileCompleted(lessonIndex, topicIndex, file)"
                  class="material-symbols-outlined text-emerald-500 text-[18px] mt-0.5"
                >
                  check
                </span>
              </div>

              <!-- Empty state if no files -->
              <div
                v-if="!getTopicFiles(lessonIndex, topicIndex) || getTopicFiles(lessonIndex, topicIndex).length === 0"
                class="p-2 text-xs text-slate-400"
              >
                Нет материалов
              </div>
            </div>
          </details>

          <!-- Lesson Test -->
          <div
            :class="[
              'flex items-start justify-between p-2 rounded-md cursor-pointer group/item transition-colors border-t border-slate-200 dark:border-slate-800 mt-1',
              isCurrentTest(lessonIndex)
                ? 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800'
                : 'hover:bg-slate-50 dark:hover:bg-white/5'
            ]"
            @click="selectTest(lessonIndex)"
          >
            <div
              :class="[
                'flex items-start gap-3',
                isCurrentTest(lessonIndex)
                  ? ''
                  : 'opacity-75 group-hover/item:opacity-100 transition-opacity'
              ]"
            >
              <span
                class="material-symbols-outlined text-[20px] mt-0.5"
                :class="
                  isCurrentTest(lessonIndex)
                    ? 'text-purple-600 dark:text-purple-400'
                    : 'text-slate-400 group-hover/item:text-slate-600 dark:text-slate-500'
                "
              >
                description
              </span>
              <div class="flex flex-col">
                <span
                  :class="[
                    'text-sm leading-snug',
                    isCurrentTest(lessonIndex)
                      ? 'font-semibold text-purple-600 dark:text-purple-400'
                      : 'font-medium text-slate-600 dark:text-slate-300 group-hover/item:text-slate-900 transition-colors'
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

    <!-- User Profile Footer -->
    <div class="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-[#151f28]">
      <div class="flex items-center gap-3">
        <div
          class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 font-bold text-xs"
        >
          {{ userInitials }}
        </div>
        <div class="flex flex-col">
          <p class="text-xs font-medium text-slate-900 dark:text-white">{{ userName }}</p>
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
    default: 'Курс обучения'
  },
  courseProgress: {
    type: Number,
    default: 0
  },
  currentFile: {
    type: Object,
    default: null
  },
  stationId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select-lesson', 'select-test', 'toggle-sidebar', 'select-file'])

const expandedLessons = ref([props.currentLessonIndex])
const expandedTopics = ref([])

// User data
const userName = computed(() => {
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
  const user = authService.getCurrentUser()
  if (!user) return 'Студент'
  const roles = {
    admin: 'Администратор',
    instructor: 'Инструктор',
    user: 'Студент'
  }
  return roles[user.role] || 'Студент'
})

// Progress calculation
const totalTopicsCount = computed(() => {
  let total = 0
  props.lessons.forEach(lesson => {
    total += lesson.topics?.length || 0
  })
  return total
})

const completedTopicsCount = computed(() => {
  return props.completedTopics.size
})

// Methods
const toggleLesson = (index) => {
  const idx = expandedLessons.value.indexOf(index)
  if (idx > -1) {
    expandedLessons.value.splice(idx, 1)
    // Also collapse all topics in this lesson
    expandedTopics.value = expandedTopics.value.filter(
      key => !key.startsWith(`${index}-`)
    )
  } else {
    expandedLessons.value.push(index)
  }
}

const toggleTopic = (lessonIndex, topicIndex) => {
  const key = `${lessonIndex}-${topicIndex}`
  const idx = expandedTopics.value.indexOf(key)
  if (idx > -1) {
    expandedTopics.value.splice(idx, 1)
  } else {
    expandedTopics.value.push(key)
  }
}

const selectTopic = (lessonIndex, topicIndex) => {
  emit('select-lesson', { lessonIndex, topicIndex })
}

const selectFile = (lessonIndex, topicIndex, file) => {
  // First select the topic, then the file
  selectTopic(lessonIndex, topicIndex)
  emit('select-file', { lessonIndex, topicIndex, file })
}

const selectTest = (lessonIndex) => {
  emit('select-test', { lessonIndex })
}

const isCurrentTopic = (lessonIndex, topicIndex) => {
  return (
    lessonIndex === props.currentLessonIndex &&
    topicIndex === props.currentTopicIndex &&
    !props.isTestMode
  )
}

const isCurrentTest = (lessonIndex) => {
  return lessonIndex === props.currentLessonIndex && props.isTestMode
}

const isTopicCompleted = (lessonIndex, topicIndex) => {
  // Check if topic is completed - format is: `${stationId}-${lessonIndex}-${topicIndex}`
  if (props.stationId !== null && props.stationId !== undefined) {
    const topicId = `${props.stationId}-${lessonIndex}-${topicIndex}`
    return props.completedTopics.has(topicId)
  }
  // Fallback: check simple format
  const topicId = `${lessonIndex}-${topicIndex}`
  return props.completedTopics.has(topicId)
}

const isLessonTestPassed = (lessonIndex) => {
  const testId = `test-module-${lessonIndex + 1}`
  return props.passedTests.has(testId)
}

const getTopicFiles = (lessonIndex, topicIndex) => {
  const lesson = props.lessons[lessonIndex]
  if (!lesson || !lesson.topics) return []
  const topic = lesson.topics[topicIndex]
  if (!topic || !topic.files) return []
  const files = topic.files || []
  // Sort files: main files first, then by order_index
  return [...files].sort((a, b) => {
    const aMain = a.isMain ?? a.is_main ?? false
    const bMain = b.isMain ?? b.is_main ?? false
    if (aMain !== bMain) {
      return aMain ? -1 : 1 // Main files first
    }
    const aOrder = a.orderIndex ?? a.order_index ?? 0
    const bOrder = b.orderIndex ?? b.order_index ?? 0
    return aOrder - bOrder
  })
}

const isActiveFile = (lessonIndex, topicIndex, file) => {
  if (!props.currentFile) return false
  if (
    lessonIndex !== props.currentLessonIndex ||
    topicIndex !== props.currentTopicIndex
  ) {
    return false
  }
  const fileKey = file.objectKey || file.object_key || file.objectName || file.object_name
  const currentKey =
    props.currentFile.objectKey ||
    props.currentFile.object_key ||
    props.currentFile.objectName ||
    props.currentFile.object_name
  return fileKey === currentKey
}

const isFileCompleted = (lessonIndex, topicIndex, file) => {
  // File is considered completed if topic is completed
  return isTopicCompleted(lessonIndex, topicIndex)
}

const getFileIcon = (file) => {
  const fileName = (file.originalName || file.original_name || file.fileName || '').toLowerCase()
  const fileType = (file.fileType || file.file_type || '').toLowerCase()
  
  if (fileType === 'pdf' || fileName.endsWith('.pdf')) {
    return 'picture_as_pdf'
  }
  if (fileType === 'video' || fileName.endsWith('.mp4') || fileName.endsWith('.webm') || fileName.endsWith('.mov')) {
    return 'play_circle'
  }
  return 'description'
}

const getFileTypeLabel = (file) => {
  const isMain = file.isMain ?? file.is_main ?? false
  return isMain ? 'Основной материал' : 'Дополнительный'
}

// Watch for current lesson changes to auto-expand
watch(
  () => props.currentLessonIndex,
  (newIndex) => {
    if (!expandedLessons.value.includes(newIndex)) {
      expandedLessons.value.push(newIndex)
    }
    // Auto-expand current topic
    if (props.currentTopicIndex >= 0) {
      const topicKey = `${newIndex}-${props.currentTopicIndex}`
      if (!expandedTopics.value.includes(topicKey)) {
        expandedTopics.value.push(topicKey)
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
details > summary {
  list-style: none;
}

details > summary::-webkit-details-marker {
  display: none;
}
</style>
