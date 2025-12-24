<template>
  <div class="lesson-sidebar bg-white border-r border-gray-200 flex flex-col">
    <!-- Compact Header -->
    <div class="p-4 border-b border-gray-200 relative">
      <div class="flex items-center justify-between mb-1">
        <h2 class="text-sm font-bold text-gray-900 uppercase tracking-wide">
          Содержание
        </h2>
        <el-button
          :icon="Fold"
          circle
          size="small"
          class="sidebar-toggle-btn"
          title="Свернуть сайдбар"
          @click="handleToggleSidebar"
        />
      </div>
      <button 
        class="text-xs text-blue-600 hover:text-blue-700 font-medium"
        @click="toggleAllLessons"
      >
        {{ allExpanded ? 'Свернуть' : 'Развернуть' }}
      </button>
    </div>

    <!-- Lessons List -->
    <div class="lessons-list-container">
      <div
        v-for="(lesson, lessonIndex) in lessons"
        :key="lessonIndex"
        class="border-b border-gray-100"
      >
        <!-- Compact Lesson Header -->
        <button
          class="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors group"
          @click="toggleLesson(lessonIndex)"
        >
          <div class="flex-1 text-left min-w-0">
            <div class="text-xs font-semibold text-blue-600 mb-0.5">
              Модуль {{ lessonIndex + 1 }}
            </div>
            <div class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
              {{ lesson.title }}
            </div>
            <div class="text-xs text-gray-500 mt-0.5">
              {{ lesson.topics?.length || 0 }} {{ lesson.topics?.length === 1 ? 'тема' : 'тем' }}
            </div>
          </div>
          <el-icon 
            :class="[
              'text-gray-400 transition-transform duration-200 flex-shrink-0 ml-2',
              expandedLessons.includes(lessonIndex) ? 'rotate-180' : ''
            ]"
            :size="14"
          >
            <ArrowDown />
          </el-icon>
        </button>

        <!-- Compact Topics -->
        <el-collapse-transition>
          <div
            v-show="expandedLessons.includes(lessonIndex)"
            class="bg-gray-50"
          >
            <!-- Topics -->
            <button
              v-for="(topic, topicIndex) in lesson.topics"
              :key="topicIndex"
              :class="[
                'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3',
                isCurrentTopic(lessonIndex, topicIndex)
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-transparent'
              ]"
              @click="selectTopic(lessonIndex, topicIndex)"
            >
              <!-- Compact Status Icon -->
              <div class="flex-shrink-0 mt-0.5">
                <div 
                  v-if="isTopicCompleted(lessonIndex, topicIndex)"
                  class="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center"
                >
                  <el-icon
                    class="text-white"
                    :size="12"
                  >
                    <Check />
                  </el-icon>
                </div>
                <div 
                  v-else-if="isCurrentTopic(lessonIndex, topicIndex)"
                  class="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center"
                >
                  <el-icon
                    class="text-white"
                    :size="12"
                  >
                    <VideoPlay />
                  </el-icon>
                </div>
                <div 
                  v-else
                  class="w-5 h-5 rounded-full border-2 border-gray-300 flex items-center justify-center"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-300" />
                </div>
              </div>

              <!-- Compact Topic Info -->
              <div class="flex-1 min-w-0">
                <div 
                  :class="[
                    'text-xs font-medium mb-0.5 leading-tight',
                    isCurrentTopic(lessonIndex, topicIndex)
                      ? 'text-blue-600'
                      : 'text-gray-900'
                  ]"
                >
                  {{ lessonIndex + 1 }}.{{ topicIndex + 1 }}: {{ topic.title }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ topic.duration || '15 мин' }}
                </div>
              </div>

              <!-- Play Icon for current -->
              <div
                v-if="isCurrentTopic(lessonIndex, topicIndex)"
                class="flex-shrink-0"
              >
                <el-icon
                  class="text-blue-600"
                  :size="14"
                >
                  <CaretRight />
                </el-icon>
              </div>
            </button>

            <!-- Lesson Test -->
            <button
              :class="[
                'w-full px-4 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition-colors text-left border-l-3 border-t border-gray-200',
                isCurrentTest(lessonIndex)
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-transparent'
              ]"
              @click="selectTest(lessonIndex)"
            >
              <!-- Test Icon -->
              <div class="flex-shrink-0 mt-0.5">
                <div 
                  v-if="isLessonTestPassed(lessonIndex)"
                  class="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center"
                >
                  <el-icon
                    class="text-white"
                    :size="12"
                  >
                    <Check />
                  </el-icon>
                </div>
                <div 
                  v-else-if="isCurrentTest(lessonIndex)"
                  class="w-5 h-5 rounded-full bg-purple-500 flex items-center justify-center"
                >
                  <el-icon
                    class="text-white"
                    :size="12"
                  >
                    <Document />
                  </el-icon>
                </div>
                <div 
                  v-else
                  class="w-5 h-5 rounded-lg border-2 border-purple-300 flex items-center justify-center"
                >
                  <el-icon
                    class="text-purple-500"
                    :size="12"
                  >
                    <Document />
                  </el-icon>
                </div>
              </div>

              <!-- Test Info -->
              <div class="flex-1 min-w-0">
                <div 
                  :class="[
                    'text-xs font-medium mb-0.5 leading-tight flex items-center gap-1',
                    isCurrentTest(lessonIndex)
                      ? 'text-purple-600'
                      : 'text-gray-900'
                  ]"
                >
                  <span>Тест модуля {{ lessonIndex + 1 }}</span>
                  <el-tag
                    v-if="isLessonTestPassed(lessonIndex)"
                    type="success"
                    size="small"
                    class="ml-1"
                  >
                    ✓
                  </el-tag>
                </div>
                <div class="text-xs text-gray-500">
                  Проверка знаний
                </div>
              </div>

              <!-- Arrow Icon for current -->
              <div
                v-if="isCurrentTest(lessonIndex)"
                class="flex-shrink-0"
              >
                <el-icon
                  class="text-purple-600"
                  :size="14"
                >
                  <CaretRight />
                </el-icon>
              </div>
            </button>
          </div>
        </el-collapse-transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowDown, Check, VideoPlay, CaretRight, Document, Fold } from '@element-plus/icons-vue'

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
  }
})

const emit = defineEmits(['select-lesson', 'select-test', 'toggle-sidebar'])

const expandedLessons = ref([props.currentLessonIndex])
const allExpanded = ref(false)

// Methods
const toggleLesson = (index) => {
  const idx = expandedLessons.value.indexOf(index)
  if (idx > -1) {
    expandedLessons.value.splice(idx, 1)
  } else {
    expandedLessons.value.push(index)
  }
}

const toggleAllLessons = () => {
  if (allExpanded.value) {
    expandedLessons.value = [props.currentLessonIndex]
    allExpanded.value = false
  } else {
    expandedLessons.value = props.lessons.map((_, index) => index)
    allExpanded.value = true
  }
}

const selectTopic = (lessonIndex, topicIndex) => {
  emit('select-lesson', { lessonIndex, topicIndex })
}

const selectTest = (lessonIndex) => {
  emit('select-test', { lessonIndex })
}

const handleToggleSidebar = () => {
  emit('toggle-sidebar')
}

const isCurrentTopic = (lessonIndex, topicIndex) => {
  return lessonIndex === props.currentLessonIndex && topicIndex === props.currentTopicIndex && !props.isTestMode
}

const isCurrentTest = (lessonIndex) => {
  return lessonIndex === props.currentLessonIndex && props.isTestMode
}

const isTopicCompleted = (lessonIndex, topicIndex) => {
  const topicId = `${lessonIndex}-${topicIndex}`
  return props.completedTopics.has(topicId)
}

const isLessonTestPassed = (lessonIndex) => {
  // Проверяем, есть ли пройденный тест для этого модуля
  const testId = `test-module-${lessonIndex + 1}` // Например test-module-1, test-module-2
  return props.passedTests.has(testId)
}

// Watch for current lesson changes to auto-expand
watch(() => props.currentLessonIndex, (newIndex) => {
  if (!expandedLessons.value.includes(newIndex)) {
    expandedLessons.value.push(newIndex)
  }
}, { immediate: true })
</script>

<style scoped>
.lesson-sidebar {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  width: 100%;
  max-width: 100%;
}

/* Desktop styles */
.sidebar-desktop {
  position: sticky;
  top: clamp(3.5rem, 10vw, 4rem);
  height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  max-height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  overflow: hidden;
  width: clamp(16rem, 25vw, 20rem);
  min-width: clamp(16rem, 25vw, 20rem);
  max-width: clamp(16rem, 25vw, 20rem);
}

/* Mobile styles */
.sidebar-mobile {
  position: fixed;
  left: 0;
  top: clamp(3.5rem, 10vw, 4rem);
  height: calc(100vh - clamp(3.5rem, 10vw, 4rem));
  z-index: 40;
  overflow: hidden;
  width: clamp(16rem, 80vw, 20rem);
  max-width: 85vw;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.lessons-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  width: 100%;
}

.rotate-180 {
  transform: rotate(180deg);
}

.sidebar-toggle-btn {
  flex-shrink: 0;
  margin-left: clamp(0.25rem, 1vw, 0.5rem);
  width: clamp(1.75rem, 4vw, 2rem);
  height: clamp(1.75rem, 4vw, 2rem);
}

/* Кастомный скроллбар для сайдбара */
.lessons-list-container::-webkit-scrollbar {
  width: clamp(0.25rem, 0.75vw, 0.375rem);
}

.lessons-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.lessons-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: clamp(0.125rem, 0.375vw, 0.1875rem);
}

.lessons-list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Media Queries */
/* Mobile phones (max-width: 480px) */
@media (max-width: 480px) {
  .sidebar-mobile {
    width: 85vw;
    max-width: 85vw;
  }

  .sidebar-desktop {
    width: clamp(14rem, 30vw, 18rem);
    min-width: clamp(14rem, 30vw, 18rem);
    max-width: clamp(14rem, 30vw, 18rem);
  }
}

/* Tablets (max-width: 768px) */
@media (max-width: 768px) {
  .sidebar-mobile {
    width: clamp(18rem, 75vw, 22rem);
    max-width: 80vw;
  }

  .sidebar-desktop {
    width: clamp(16rem, 28vw, 20rem);
    min-width: clamp(16rem, 28vw, 20rem);
    max-width: clamp(16rem, 28vw, 20rem);
  }
}

/* Small laptops (max-width: 1024px) */
@media (max-width: 1024px) {
  .sidebar-desktop {
    width: clamp(16rem, 30vw, 20rem);
    min-width: clamp(16rem, 30vw, 20rem);
    max-width: clamp(16rem, 30vw, 20rem);
  }
}

/* Desktop (min-width: 1025px) */
@media (min-width: 1025px) {
  .sidebar-desktop {
    width: clamp(18rem, 22vw, 20rem);
    min-width: clamp(18rem, 22vw, 20rem);
    max-width: clamp(18rem, 22vw, 20rem);
  }
}

/* Wide monitors (min-width: 1440px) */
@media (min-width: 1440px) {
  .sidebar-desktop {
    width: 20rem;
    min-width: 20rem;
    max-width: 20rem;
  }
}
</style>

