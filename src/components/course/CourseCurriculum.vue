<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm dark:shadow-none border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 gap-4">
      <div class="flex items-center gap-3">
        <span class="material-icons-outlined text-blue-600 text-3xl">menu_book</span>
        <h2 class="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          Программа тренинга
        </h2>
      </div>
      <div class="bg-gray-50 dark:bg-gray-900 px-4 py-2 rounded-full text-sm font-medium text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700">
        <span class="text-blue-600 dark:text-blue-400 font-bold">{{ courseStats.lessons }}</span> уроков
        <span v-if="courseStats.topics > 0"> • 
          <span class="text-blue-600 dark:text-blue-400 font-bold">{{ courseStats.topics }}</span> тем
        </span>
        <span v-if="courseStats.tests > 0"> • 
          <span class="text-blue-600 dark:text-blue-400 font-bold">{{ courseStats.tests }}</span> тестов
        </span>
      </div>
    </div>

    <!-- Course Lessons -->
    <div class="p-6">
      <div class="space-y-4">
        <div 
          v-for="(lesson, lessonIndex) in curriculum" 
          :key="lessonIndex" 
          :class="[
            'group rounded-xl p-5 transition-all duration-300 cursor-pointer flex items-center justify-between',
            expandedLessons.includes(lessonIndex)
              ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 shadow-inner relative overflow-hidden'
              : 'bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 hover:shadow-md'
          ]"
          @click="toggleLesson(lessonIndex)"
        >
          <div v-if="expandedLessons.includes(lessonIndex)" class="absolute left-0 top-0 w-1 h-full bg-blue-600 dark:bg-blue-400 rounded-l-xl"></div>
          <div class="flex items-center gap-5 relative z-10">
            <div :class="[
              'flex-shrink-0 w-12 h-12 rounded-full text-white flex items-center justify-center text-xl font-bold shadow-lg transition-transform',
              expandedLessons.includes(lessonIndex)
                ? 'bg-blue-600 dark:bg-blue-500 shadow-blue-500/30'
                : 'bg-blue-600 dark:bg-blue-500 shadow-blue-500/30 group-hover:scale-110'
            ]">
              {{ lessonIndex + 1 }}
            </div>
            <div>
              <h3 :class="[
                'text-lg mb-1 transition-colors',
                expandedLessons.includes(lessonIndex)
                  ? 'font-bold text-gray-900 dark:text-white'
                  : 'font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400'
              ]">
                {{ getLessonTitle(lesson.title) }}
              </h3>
              <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <div class="flex items-center gap-1">
                  <span :class="[
                    'material-icons-outlined text-base',
                    expandedLessons.includes(lessonIndex) ? 'text-blue-600 dark:text-blue-400' : ''
                  ]">library_books</span>
                  <span>{{ lesson.topics?.length || 0 }} тем</span>
                </div>
                <div
                  v-if="lesson.duration"
                  class="flex items-center gap-1"
                >
                  <span :class="[
                    'material-icons-outlined text-base',
                    expandedLessons.includes(lessonIndex) ? 'text-blue-600 dark:text-blue-400' : ''
                  ]">schedule</span>
                  <span>{{ lesson.duration }}</span>
                </div>
              </div>
            </div>
          </div>
          <span :class="[
            'material-icons-outlined transition-transform relative z-10',
            expandedLessons.includes(lessonIndex)
              ? 'text-blue-600 dark:text-blue-400 transform rotate-180'
              : 'text-gray-400 dark:text-gray-500 group-hover:text-blue-600 dark:group-hover:text-blue-400'
          ]">expand_more</span>

          <!-- Lesson Topics (Expanded Content) -->
          <transition name="expand">
            <div
              v-if="expandedLessons.includes(lessonIndex)"
              class="w-full mt-4 pt-4 border-t border-blue-200 dark:border-blue-700"
            >
              <div class="space-y-2">
                <!-- Topics -->
                <div
                  v-for="(topic, topicIndex) in lesson.topics"
                  :key="topicIndex"
                  class="flex items-center p-3 rounded-lg hover:bg-blue-100/50 dark:hover:bg-blue-900/20 transition-all duration-200"
                >
                  <div class="flex items-center space-x-3 flex-1">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <span class="material-icons-outlined text-blue-600 dark:text-blue-400 text-lg">library_books</span>
                    </div>
                    <div class="flex-1">
                      <p class="font-semibold text-gray-900 dark:text-white text-sm">
                        <span
                          v-if="topic.code"
                          class="text-blue-600 dark:text-blue-400 mr-2"
                        >{{ topic.code }}</span>
                        {{ topic.title }}
                      </p>
                      <div
                        v-if="topic.duration"
                        class="flex items-center gap-3 mt-1"
                      >
                        <span class="text-xs text-gray-500 dark:text-gray-400">{{ topic.duration }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Test -->
                <div v-if="lesson.test">
                  <div class="flex items-center p-3 rounded-lg hover:bg-blue-100/50 dark:hover:bg-blue-900/20 transition-all duration-200">
                    <div class="flex items-center space-x-3 flex-1">
                      <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
                        <span class="material-icons-outlined text-blue-600 dark:text-blue-400 text-lg">quiz</span>
                      </div>
                      <div class="flex-1">
                        <p class="font-semibold text-gray-900 dark:text-white text-sm">
                          {{ lesson.test.title }}
                        </p>
                        <div class="flex items-center gap-3 mt-1">
                          <span class="text-xs text-gray-500 dark:text-gray-400">{{ lesson.test.questions || lesson.test.questionsCount || 10 }} вопросов</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>

        <!-- Final Test -->
        <div
          v-if="finalTest"
          class="group bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 hover:shadow-md transition-all duration-300 cursor-pointer"
        >
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="material-icons-outlined text-blue-600 dark:text-blue-400 text-lg">emoji_events</span>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900 dark:text-white text-sm">
                {{ finalTest.title || 'Итоговый тест' }}
              </p>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ finalTest.questions || finalTest.questionsCount || 10 }} вопросов</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'CourseCurriculum',
  props: {
    // Структура курса: массив уроков
    lessons: {
      type: Array,
      required: true,
      default: () => []
    },
    // Итоговый тест (опционально)
    finalTest: {
      type: Object,
      default: null
    }
  },
  emits: ['start-test', 'start-final-test'],
  setup(props) {
    const expandedLessons = ref([])

    // Структура контента курса
    const curriculum = computed(() => {
      return props.lessons || []
    })

    // Статистика курса
    const courseStats = computed(() => {
      const lessons = curriculum.value || []
      let totalTopics = 0
      let totalTests = 0

      lessons.forEach(lesson => {
        totalTopics += (lesson.topics || []).length
        if (lesson.test) {
          totalTests++
        }
      })

      if (props.finalTest) {
        totalTests++
      }

      return {
        lessons: lessons.length,
        topics: totalTopics,
        tests: totalTests
      }
    })

    const toggleLesson = (index) => {
      const idx = expandedLessons.value.indexOf(index)
      if (idx > -1) {
        expandedLessons.value.splice(idx, 1)
      } else {
        expandedLessons.value.push(index)
      }
    }

    // Функция для удаления префикса "Урок N" из названия
    const getLessonTitle = (title) => {
      if (!title) return ''
      // Убираем паттерны: "Урок N:", "Урок № N:", "Урок N " и т.д.
      return title
        .replace(/^Урок\s*№?\s*\d+\s*:?\s*/i, '') // Убираем "Урок N:" или "Урок № N:"
        .replace(/^Урок\s*№?\s*\d+\s*/i, '') // Убираем "Урок N " или "Урок № N "
        .trim()
    }

    return {
      expandedLessons,
      curriculum,
      courseStats,
      toggleLesson,
      getLessonTitle
    }
  }
}
</script>

<style scoped>
/* Material Icons support */
.material-icons-outlined {
  font-family: 'Material Icons Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  font-feature-settings: 'liga';
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}

/* Expand Animation */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 3000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>

