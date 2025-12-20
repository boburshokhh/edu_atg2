<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-100">
      <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <BookOpenIcon class="w-6 h-6 text-blue-600" />
        Программа тренинга
      </h2>
      <div class="text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-lg">
        <span class="font-semibold text-gray-900">{{ courseStats.lessons }}</span> уроков
        <span v-if="courseStats.topics > 0"> • 
          <span class="font-semibold text-gray-900">{{ courseStats.topics }}</span> тем
        </span>
        <span v-if="courseStats.tests > 0"> • 
          <span class="font-semibold text-gray-900">{{ courseStats.tests }}</span> тестов
        </span>
      </div>
    </div>

    <!-- Course Lessons -->
    <div class="p-6">
      <div class="space-y-4">
        <div 
          v-for="(lesson, lessonIndex) in curriculum" 
          :key="lessonIndex" 
          class="border-2 border-gray-200 rounded-2xl overflow-hidden transition-all duration-300 hover:border-blue-300 hover:shadow-lg"
        >
          <!-- Lesson Header -->
          <button 
            @click="toggleLesson(lessonIndex)"
            class="w-full bg-gradient-to-r from-white to-gray-50 hover:from-blue-50 hover:to-blue-50/50 transition-all duration-300"
          >
            <div class="flex items-center justify-between p-5">
              <div class="flex items-center space-x-4 flex-1 text-left">
                <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-lg flex-shrink-0">
                  {{ lessonIndex + 1 }}
                </div>
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-base mb-0.5">{{ getLessonTitle(lesson.title) }}</h3>
                  <div class="flex items-center gap-3 text-xs text-gray-500">
                    <span class="flex items-center gap-1">
                      <BookOpenIcon class="w-4 h-4 text-blue-600" />
                      {{ lesson.topics?.length || 0 }} тем
                    </span>
                    <span v-if="lesson.duration" class="flex items-center gap-1">
                      <ClockIcon class="w-4 h-4 text-blue-600" />
                      {{ lesson.duration }}
                    </span>
                  </div>
                </div>
              </div>
              <svg 
                class="w-6 h-6 text-gray-400 transition-transform duration-300 flex-shrink-0"
                :class="{ 'rotate-180': expandedLessons.includes(lessonIndex) }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
          </button>

          <!-- Lesson Topics -->
          <transition name="expand">
            <div v-if="expandedLessons.includes(lessonIndex)" class="border-t-2 border-gray-100 bg-white">
              <div class="p-5 space-y-2">
                <!-- Topics -->
                <div v-for="(topic, topicIndex) in lesson.topics" :key="topicIndex">
                  <div class="flex items-center p-3 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-transparent hover:border-blue-200">
                    <div class="flex items-center space-x-3 flex-1">
                      <div class="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center flex-shrink-0">
                        <BookOpenIcon class="w-5 h-5 text-blue-600" />
                      </div>
                      <div class="flex-1">
                        <p class="font-semibold text-gray-900">
                          <span v-if="topic.code" class="text-blue-600 mr-2">{{ topic.code }}</span>
                          {{ topic.title }}
                        </p>
                        <div v-if="topic.duration" class="flex items-center gap-3 mt-1">
                          <span class="text-xs text-gray-500">{{ topic.duration }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Test -->
                <div v-if="lesson.test">
                  <div class="flex items-center p-3 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-transparent hover:border-blue-200">
                    <div class="flex items-center space-x-3 flex-1">
                      <div class="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                      </div>
                      <div class="flex-1">
                        <p class="font-semibold text-gray-900">
                          {{ lesson.test.title }}
                        </p>
                        <div class="flex items-center gap-3 mt-1">
                          <span class="text-xs text-gray-500">{{ lesson.test.questions || lesson.test.questionsCount || 10 }} вопросов</span>
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
        <div v-if="finalTest" class="border-2 border-gray-200 rounded-2xl overflow-hidden transition-all duration-300 hover:border-blue-300 hover:shadow-lg">
          <div class="p-5">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center flex-shrink-0">
                <TrophyIcon class="w-5 h-5 text-blue-600" />
              </div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">
                  {{ finalTest.title || 'Итоговый тест' }}
                </p>
                <div class="flex items-center gap-3 mt-1">
                  <span class="text-xs text-gray-500">{{ finalTest.questions || finalTest.questionsCount || 10 }} вопросов</span>
                </div>
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
import { ClockIcon, BookOpenIcon, TrophyIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'CourseCurriculum',
  components: {
    ClockIcon,
    BookOpenIcon,
    TrophyIcon
  },
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

