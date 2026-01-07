<template>
  <aside
    :class="[
      'w-80 flex flex-col shrink-0 overflow-y-auto transition-colors duration-200 border-r z-20',
      isDark 
        ? 'bg-gray-800 border-gray-700' 
        : 'bg-white border-gray-200',
      isMobile ? 'sidebar-mobile' : 'sidebar-desktop hidden lg:flex'
    ]"
  >
    <!-- Header -->
    <div 
      :class="[
        'p-4 border-b sticky top-0 z-10 transition-colors duration-200',
        isDark 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]"
    >
      <div class="flex items-center justify-between mb-2">
        <h2 
          :class="[
            'font-bold text-lg tracking-tight uppercase',
            isDark ? 'text-gray-100' : 'text-gray-900'
          ]"
        >
          Содержание
        </h2>
        <button 
          :class="[
            'p-1 rounded transition-colors',
            isDark 
              ? 'hover:bg-gray-700 text-gray-500' 
              : 'hover:bg-gray-100 text-gray-500'
          ]"
        >
          <span class="material-symbols-outlined text-sm">filter_list</span>
        </button>
      </div>
      <button 
        class="text-sm text-primary font-medium hover:underline"
        @click="expandAll"
      >
        Развернуть всё
      </button>
    </div>

    <!-- Modules List -->
    <div class="py-2">
      <div 
        v-for="(lesson, lessonIndex) in lessons" 
        :key="lessonIndex"
        :class="[
          'border-b last:border-0',
          isDark ? 'border-gray-700' : 'border-gray-100'
        ]"
      >
        <!-- Module Header -->
        <div
          :class="[
            'px-4 py-3 flex items-start justify-between cursor-pointer transition-colors group',
            isDark 
              ? 'hover:bg-gray-700/50' 
              : 'hover:bg-gray-50'
          ]"
          @click="toggleLesson(lessonIndex)"
        >
          <div>
            <span class="text-xs font-semibold text-primary uppercase tracking-wider">
              Модуль {{ lessonIndex + 1 }}
            </span>
            <h3 
              :class="[
                'text-sm font-semibold mt-0.5',
                (!lesson.topics || lesson.topics.length === 0) ? 'opacity-60' : '',
                isDark ? 'text-gray-100' : 'text-gray-900'
              ]"
            >
              {{ lesson.title }}
            </h3>
            <p 
              :class="[
                'text-xs mt-1',
                isDark ? 'text-gray-400' : 'text-gray-500'
              ]"
            >
              {{ lesson.topics?.length || 0 }} темы
            </p>
          </div>
          <span 
            :class="[
              'material-symbols-outlined transition-colors',
              isDark 
                ? 'text-gray-500 group-hover:text-primary' 
                : 'text-gray-400 group-hover:text-primary'
            ]"
          >
            {{ expandedLessons.includes(lessonIndex) ? 'expand_less' : 'expand_more' }}
          </span>
        </div>

        <!-- Topics List -->
        <div 
          v-if="expandedLessons.includes(lessonIndex) && lesson.topics?.length > 0"
          :class="[
            isDark ? 'bg-gray-900/10' : 'bg-gray-50/50'
          ]"
        >
          <!-- Topics -->
          <div
            v-for="(topic, topicIndex) in lesson.topics"
            :key="topicIndex"
          >
            <!-- Topic Item -->
            <div
              :class="[
                'flex items-start gap-3 px-4 py-3 cursor-pointer border-l-4 transition-all',
                isCurrentTopic(lessonIndex, topicIndex)
                  ? isDark 
                    ? 'bg-blue-900/20 border-primary' 
                    : 'bg-blue-50 border-primary'
                  : isDark
                    ? 'hover:bg-gray-700/50 border-transparent'
                    : 'hover:bg-gray-100 border-transparent'
              ]"
              @click="selectTopic(lessonIndex, topicIndex)"
            >
              <div 
                :class="[
                  'mt-0.5',
                  isTopicCompleted(lessonIndex, topicIndex) 
                    ? 'text-primary' 
                    : isDark ? 'text-gray-500' : 'text-gray-400'
                ]"
              >
                <span class="material-symbols-outlined text-lg">
                  {{ isTopicCompleted(lessonIndex, topicIndex) ? 'check_circle' : 'radio_button_unchecked' }}
                </span>
              </div>
              <div class="flex-1">
                <p 
                  :class="[
                    'text-sm font-medium',
                    isCurrentTopic(lessonIndex, topicIndex) 
                      ? 'text-primary' 
                      : isDark ? 'text-gray-100' : 'text-gray-900'
                  ]"
                >
                  {{ topic.title }}
                </p>
                <p 
                  :class="[
                    'text-xs mt-0.5',
                    isDark ? 'text-gray-400' : 'text-gray-500'
                  ]"
                >
                  {{ topic.files?.length || 0 }} материалов
                </p>
              </div>
              <span 
                v-if="isCurrentTopic(lessonIndex, topicIndex)"
                class="material-symbols-outlined text-primary text-sm ml-auto"
              >
                play_arrow
              </span>
            </div>

            <!-- Files in Topic (collapsible) -->
            <div 
              v-if="isCurrentTopic(lessonIndex, topicIndex) && topic.files?.length > 0"
              :class="[
                'pl-12 pb-2',
                isDark ? 'bg-gray-900/20' : 'bg-gray-100/50'
              ]"
            >
              <div
                v-for="(file, fileIndex) in topic.files"
                :key="fileIndex"
                :class="[
                  'flex items-center gap-2 px-3 py-2 text-xs cursor-pointer rounded-md mx-2 transition-colors',
                  isCurrentFile(lessonIndex, topicIndex, file)
                    ? 'bg-primary/10 text-primary font-medium'
                    : isDark 
                      ? 'hover:bg-gray-700 text-gray-400'
                      : 'hover:bg-gray-200 text-gray-600'
                ]"
                @click.stop="selectFile(lessonIndex, topicIndex, file)"
              >
                <span class="material-symbols-outlined text-sm">
                  {{ getFileIcon(file) }}
                </span>
                <span class="truncate flex-1">
                  {{ cleanFileName(file.originalName || file.original_name || file.fileName) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Module Test -->
          <div
            :class="[
              'flex items-start gap-3 px-4 py-3 cursor-pointer border-l-4 transition-all',
              isCurrentTest(lessonIndex)
                ? isDark 
                  ? 'bg-purple-900/20 border-purple-500' 
                  : 'bg-purple-50 border-purple-500'
                : isDark
                  ? 'hover:bg-gray-700/50 border-transparent'
                  : 'hover:bg-gray-100 border-transparent'
            ]"
            @click="selectTest(lessonIndex)"
          >
            <div 
              :class="[
                'mt-0.5',
                isLessonTestPassed(lessonIndex) 
                  ? 'text-purple-500' 
                  : isDark ? 'text-gray-500' : 'text-gray-400'
              ]"
            >
              <span class="material-symbols-outlined text-lg">
                {{ isLessonTestPassed(lessonIndex) ? 'check_circle' : 'assignment' }}
              </span>
            </div>
            <div class="flex-1">
              <p 
                :class="[
                  'text-sm font-medium',
                  isCurrentTest(lessonIndex) 
                    ? 'text-purple-600' 
                    : isDark ? 'text-gray-100' : 'text-gray-900'
                ]"
              >
                Тест модуля {{ lessonIndex + 1 }}
              </p>
              <p 
                :class="[
                  'text-xs mt-0.5',
                  isDark ? 'text-gray-400' : 'text-gray-500'
                ]"
              >
                Проверка знаний
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, watch } from 'vue'

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
  },
  isDark: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-lesson', 'select-test', 'select-file', 'toggle-sidebar'])

const expandedLessons = ref([props.currentLessonIndex])

// Methods
const toggleLesson = (index) => {
  const idx = expandedLessons.value.indexOf(index)
  if (idx > -1) {
    expandedLessons.value.splice(idx, 1)
  } else {
    expandedLessons.value.push(index)
  }
}

const expandAll = () => {
  expandedLessons.value = props.lessons.map((_, i) => i)
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
  return lessonIndex === props.currentLessonIndex && 
         topicIndex === props.currentTopicIndex && 
         !props.isTestMode
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

const isTopicCompleted = (lessonIndex, topicIndex) => {
  // Check using the same format as parent component
  const topicId = `${props.currentLessonIndex}-${lessonIndex}-${topicIndex}`
  return props.completedTopics.has(topicId)
}

const isLessonTestPassed = (lessonIndex) => {
  const testId = `test-module-${lessonIndex + 1}`
  return props.passedTests.has(testId)
}

// Функция для очистки названия файла от "_OUTLINE"
const cleanFileName = (fileName) => {
  if (!fileName) return 'Файл'
  // Убираем "_OUTLINE" из названия (может быть в начале или в конце)
  return fileName.replace(/^O_OUTLINE\s+/i, '').replace(/\s*_OUTLINE$/i, '').replace(/\s*OUTLINE$/i, '')
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

// Watch for current lesson changes to auto-expand
watch(() => props.currentLessonIndex, (newIndex) => {
  if (!expandedLessons.value.includes(newIndex)) {
    expandedLessons.value.push(newIndex)
  }
}, { immediate: true })
</script>

<style scoped>
/* Desktop styles */
.sidebar-desktop {
  position: sticky;
  top: 0;
  height: calc(100vh - 4rem);
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
}

/* Mobile styles */
.sidebar-mobile {
  position: fixed;
  left: 0;
  top: 4rem;
  height: calc(100vh - 4rem);
  z-index: 40;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

/* Custom scrollbar */
aside::-webkit-scrollbar {
  width: 6px;
}

aside::-webkit-scrollbar-track {
  background: transparent;
}

aside::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

aside::-webkit-scrollbar-thumb:hover {
  background-color: rgba(107, 114, 128, 0.8);
}
</style>
