<template>
  <div class="user-statistics animate-fade-in">
    <!-- Карточки с ключевыми показателями -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <div class="stat-card group">
        <div class="flex items-center gap-4 mb-3">
          <div class="stat-icon bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white">
            <el-icon><Trophy /></el-icon>
          </div>
          <span class="text-sm text-gray-500 font-medium">Средний балл</span>
        </div>
        <div class="flex items-end gap-2">
          <div class="text-4xl font-bold text-gray-900">
            {{ averageTestScore }}/100
          </div>
          <div class="text-sm text-gray-400 mb-1.5">
            по тестам
          </div>
        </div>
      </div>

      <div class="stat-card group">
        <div class="flex items-center gap-4 mb-3">
          <div class="stat-icon bg-orange-50 text-orange-600 group-hover:bg-orange-600 group-hover:text-white">
            <el-icon><Timer /></el-icon>
          </div>
          <span class="text-sm text-gray-500 font-medium">Активные курсы</span>
        </div>
        <div class="flex items-end gap-2">
          <div class="text-4xl font-bold text-gray-900">
            {{ activeCourses }}
          </div>
          <div class="text-sm text-gray-400 mb-1.5">
            в процессе
          </div>
        </div>
      </div>

      <div class="stat-card group">
        <div class="flex items-center gap-4 mb-3">
          <div class="stat-icon bg-purple-50 text-purple-600 group-hover:bg-purple-600 group-hover:text-white">
            <el-icon><Files /></el-icon>
          </div>
          <span class="text-sm text-gray-500 font-medium">Пройдено тестов</span>
        </div>
        <div class="flex items-end gap-2">
          <div class="text-4xl font-bold text-gray-900">
            {{ testsCompleted }}
          </div>
          <div class="text-sm text-green-500 mb-1.5 font-medium">
            {{ completedCourses }} курсов
          </div>
        </div>
      </div>
    </div>

    <!-- Графики: Первый ряд -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Карта компетенций -->
      <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-gray-900">
            Карта компетенций
          </h3>
          <span class="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-md">WKC-1</span>
        </div>
        <div class="h-[320px] flex items-center justify-center">
          <apexchart 
            type="radar" 
            height="320" 
            :options="radarOptions" 
            :series="radarSeries"
            class="w-full"
          />
        </div>
      </div>

      <!-- Активность обучения -->
      <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-gray-900">
            Активность обучения
          </h3>
          <select class="text-xs border-none bg-gray-100 text-gray-600 rounded-md px-2 py-1 focus:ring-0 cursor-pointer hover:bg-gray-200 transition-colors">
            <option>За неделю</option>
            <option>За месяц</option>
          </select>
        </div>
        <div class="h-[320px]">
          <apexchart 
            type="area" 
            height="320" 
            :options="areaOptions" 
            :series="areaSeries"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- Графики: Второй ряд -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Распределение времени -->
      <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col">
        <h3 class="text-lg font-bold text-gray-900 mb-4">
          Типы активности
        </h3>
        <div class="flex-1 flex items-center justify-center">
          <apexchart 
            type="donut" 
            height="280" 
            :options="donutOptions" 
            :series="donutSeries"
            class="w-full"
          />
        </div>
      </div>

      <!-- Успеваемость по модулям -->
      <div class="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <h3 class="text-lg font-bold text-gray-900 mb-4">
          Результативность по модулям
        </h3>
        <div class="h-[280px]">
          <apexchart 
            type="bar" 
            height="280" 
            :options="barOptions" 
            :series="barSeries"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- Нижний блок: История и Рекомендации -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- История тестов -->
      <div class="xl:col-span-2 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-gray-900">
            История тестирования
          </h3>
          <button class="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors">
            Все результаты
          </button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-4 py-3 rounded-l-lg font-semibold tracking-wider">
                  Модуль / Тема
                </th>
                <th class="px-4 py-3 font-semibold tracking-wider hidden sm:table-cell">
                  Дата
                </th>
                <th class="px-4 py-3 font-semibold tracking-wider">
                  Результат
                </th>
                <th class="px-4 py-3 rounded-r-lg font-semibold tracking-wider text-right">
                  Статус
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="(test, i) in recentTests"
                :key="i"
                class="group hover:bg-blue-50/50 transition-colors"
              >
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900 group-hover:text-blue-700 transition-colors">
                    {{ test.name }}
                  </div>
                  <div class="text-xs text-gray-500 mt-0.5 truncate max-w-[200px] sm:max-w-xs">
                    {{ test.topic }}
                  </div>
                </td>
                <td class="px-4 py-3 text-gray-500 whitespace-nowrap hidden sm:table-cell">
                  {{ test.date }}
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden hidden sm:block">
                      <div 
                        class="h-full rounded-full transition-all duration-1000 ease-out" 
                        :class="getScoreColor(test.score)"
                        :style="{ width: `${test.score}%` }"
                      />
                    </div>
                    <span
                      class="font-bold"
                      :class="getTextScoreColor(test.score)"
                    >{{ test.score }}%</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-right">
                  <span 
                    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                    :class="test.passed ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'"
                  >
                    <span
                      class="w-1.5 h-1.5 rounded-full"
                      :class="test.passed ? 'bg-green-500' : 'bg-red-500'"
                    />
                    {{ test.passed ? 'Сдан' : 'Не сдан' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Слабые места (Рекомендации) -->
      <div class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow h-fit">
        <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div class="p-1.5 bg-red-50 rounded text-red-500">
            <el-icon><Warning /></el-icon>
          </div>
          Зоны роста
        </h3>
        <p class="text-sm text-gray-500 mb-4">
          Темы, требующие повторного изучения на основе результатов тестов
        </p>
        
        <div class="space-y-4">
          <div
            v-for="(topic, i) in weakTopics"
            :key="i"
            class="group"
          >
            <div class="flex justify-between items-center mb-1.5">
              <span class="text-sm font-medium text-gray-800 group-hover:text-blue-600 transition-colors duration-300">{{ topic.name }}</span>
              <span class="text-xs font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded">{{ topic.score }}%</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
              <div
                class="bg-red-500 h-1.5 rounded-full transition-all duration-500"
                :style="{ width: topic.score + '%' }"
              />
            </div>
            <div class="flex justify-between items-center mt-1.5">
              <span class="text-[10px] text-gray-400">{{ topic.lesson }}</span>
              <a
                href="#"
                class="text-[10px] font-medium text-blue-500 hover:text-blue-700 flex items-center gap-1 transition-colors"
              >
                Перейти к уроку <el-icon><ArrowRight /></el-icon>
              </a>
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-gray-100">
          <button class="w-full py-2.5 px-4 bg-blue-50 hover:bg-blue-100 text-blue-600 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2">
            <el-icon><Reading /></el-icon>
            Создать план повторения
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { Trophy, Timer, Files, Warning, ArrowRight, Reading } from '@element-plus/icons-vue'
import { stationsData } from '@/data/stationsData.js'

export default {
  name: 'UserStatistics',
  components: {
    apexchart: VueApexCharts,
    Trophy, Timer, Files, Warning, ArrowRight, Reading
  },
  props: {
    detailed: {
      type: Boolean,
      default: false
    },
    stats: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const averageTestScore = computed(() => Math.round(props.stats?.average_test_score || 0))
    const activeCourses = computed(() => props.stats?.active_courses || 0)
    const completedCourses = computed(() => props.stats?.completed_courses || 0)
    const testsCompleted = computed(() => props.stats?.materials?.test || 0)
    const materialStats = computed(() => ({
      video: props.stats?.materials?.video || 0,
      pdf: props.stats?.materials?.pdf || 0,
      text: props.stats?.materials?.text || 0,
      presentation: props.stats?.materials?.presentation || 0
    }))
    // Используем данные из stationsData для реалистичности
    const courseData = stationsData[1].courseProgram

    // --- Radar Chart (Компетенции) ---
    const radarSeries = ref([{
      name: 'Уровень владения',
      data: [85, 70, 92, 65, 88, 75]
    }])
    
    const radarOptions = ref({
      chart: {
        type: 'radar',
        toolbar: { show: false },
        fontFamily: 'Inter, sans-serif',
        background: 'transparent'
      },
      labels: ['Эксплуатация ГПА', 'Автоматика и КИП', 'Безопасность', 'Электрооборудование', 'Пожаротушение', 'Метрология'],
      stroke: { width: 2, colors: ['#2563eb'] },
      fill: { opacity: 0.1, colors: ['#2563eb'] },
      markers: { size: 3, colors: ['#2563eb'], strokeColors: '#fff', strokeWidth: 2, hover: { size: 5 } },
      yaxis: { show: false, min: 0, max: 100 },
      xaxis: {
        labels: {
          style: {
            colors: Array(6).fill('#64748b'),
            fontSize: '11px',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600
          }
        }
      },
      plotOptions: {
        radar: {
          polygons: {
            strokeColors: '#e2e8f0',
            connectorColors: '#e2e8f0'
          }
        }
      },
      tooltip: { theme: 'light' }
    })

    // --- Area Chart (Активность) ---
    const areaSeries = ref([{
      name: 'Часов обучения',
      data: [2.5, 3.2, 1.8, 4.5, 3.0, 5.1, 2.2]
    }])

    const areaOptions = ref({
      chart: {
        type: 'area',
        toolbar: { show: false },
        fontFamily: 'Inter, sans-serif',
        zoom: { enabled: false },
        background: 'transparent'
      },
      dataLabels: { enabled: false },
      stroke: { curve: 'smooth', width: 3, colors: ['#f97316'] },
      fill: {
        type: 'gradient',
        gradient: {
          shadeIntensity: 1,
          opacityFrom: 0.4,
          opacityTo: 0.05,
          stops: [0, 100],
          colorStops: [
            { offset: 0, color: '#f97316', opacity: 0.4 },
            { offset: 100, color: '#f97316', opacity: 0.0 }
          ]
        }
      },
      xaxis: {
        categories: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
        labels: { style: { colors: '#9ca3af' } },
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: {
        labels: { style: { colors: '#9ca3af' }, formatter: (val) => `${val}ч` }
      },
      grid: { borderColor: '#f3f4f6', strokeDashArray: 4 },
      colors: ['#f97316'],
      tooltip: {
        y: { formatter: (val) => `${val} часов` }
      }
    })

    // --- Donut Chart (Распределение) ---
    const donutSeries = ref([0, 0, 0])
    const donutOptions = ref({
      chart: { type: 'donut', fontFamily: 'Inter, sans-serif' },
      labels: ['Видео', 'PDF', 'Тексты и презентации'],
      colors: ['#3b82f6', '#f59e0b', '#10b981'],
      plotOptions: {
        pie: {
          donut: {
            size: '75%',
            labels: {
              show: true,
              name: { show: true, fontSize: '12px', color: '#64748b' },
              value: { show: true, fontSize: '20px', fontWeight: 700, color: '#1e293b' },
              total: {
                show: true,
                label: 'Всего',
                color: '#64748b',
                formatter: (w) => String(w.globals.seriesTotals.reduce((a, b) => a + b, 0))
              }
            }
          }
        }
      },
      legend: { position: 'bottom', fontSize: '12px' },
      dataLabels: { enabled: false },
      stroke: { show: false }
    })

    // --- Bar Chart (Успеваемость) ---
    // Берем названия уроков из реальных данных
    const lessonTitles = courseData.lessons.map(l => l.title.split(':')[0].replace('Урок № ', 'Модуль '))
    
    const barSeries = ref([{
      name: 'Средний балл',
      data: [92, 85, 78, 88] // Mock data matching 4 lessons
    }])

    const barOptions = ref({
      chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'Inter, sans-serif' },
      plotOptions: {
        bar: { borderRadius: 6, columnWidth: '30%', distributed: true }
      },
      colors: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'],
      xaxis: {
        categories: lessonTitles,
        labels: { 
          style: { colors: '#64748b', fontSize: '11px', fontWeight: 500 },
          rotate: -45,
          trim: true
        },
        axisBorder: { show: false },
        axisTicks: { show: false }
      },
      yaxis: { max: 100, labels: { style: { colors: '#9ca3af' } } },
      grid: { borderColor: '#f3f4f6', strokeDashArray: 4 },
      legend: { show: false },
      tooltip: {
        y: { formatter: (val) => `${val}%` }
      }
    })

    // --- Mock Data Generation from Real Content ---
    const recentTests = ref([])
    const weakTopics = ref([])

    watch(
      materialStats,
      (stats) => {
        donutSeries.value = [
          stats.video,
          stats.pdf,
          stats.text + stats.presentation
        ]
      },
      { immediate: true }
    )

    onMounted(() => {
      // Генерация истории тестов на основе реальных тем
      const lessons = courseData.lessons
      
      // Тест 1
      recentTests.value.push({
        name: 'Итоговый тест: Зона замера газа',
        topic: lessons[0].topics[0].title + ', ' + lessons[0].topics[1].title,
        date: '23.11.2025',
        score: 95,
        passed: true
      })
      
      // Тест 2
      recentTests.value.push({
        name: 'Промежуточный контроль: ГПА',
        topic: lessons[1].topics[2].title + ' (Titan 130)',
        date: '21.11.2025',
        score: 88,
        passed: true
      })

      // Тест 3 (Проваленный для примера)
      recentTests.value.push({
        name: 'Системы безопасности ГПА',
        topic: lessons[1].topics[12].title + ' и ' + lessons[1].topics[13].title,
        date: '19.11.2025',
        score: 55,
        passed: false
      })

      // Тест 4
      recentTests.value.push({
        name: 'Вспомогательное оборудование',
        topic: lessons[2].topics[3].title,
        date: '15.11.2025',
        score: 92,
        passed: true
      })

      // Тест 5
      recentTests.value.push({
        name: 'Газогенератор Jenbacher',
        topic: lessons[3].topics[0].title,
        date: '12.11.2025',
        score: 84,
        passed: true
      })

      // Генерация слабых мест из реальных данных
      weakTopics.value = [
        { 
          name: lessons[1].topics[12].title, // Антипомпажная система
          lesson: lessons[1].title,
          score: 45 
        },
        { 
          name: lessons[1].topics[8].title, // Электроснабжение ГПА
          lesson: lessons[1].title,
          score: 58 
        },
        {
           name: lessons[2].topics[8].title, // Система ЭХЗ
           lesson: lessons[2].title,
           score: 62
        }
      ]
    })

    const getScoreColor = (score) => {
      if (score >= 80) return 'bg-green-500'
      if (score >= 60) return 'bg-yellow-500'
      return 'bg-red-500'
    }

    const getTextScoreColor = (score) => {
      if (score >= 80) return 'text-green-600'
      if (score >= 60) return 'text-yellow-600'
      return 'text-red-600'
    }

    return {
      radarSeries, radarOptions,
      areaSeries, areaOptions,
      donutSeries, donutOptions,
      barSeries, barOptions,
      recentTests,
      weakTopics,
      getScoreColor, getTextScoreColor,
      averageTestScore,
      activeCourses,
      completedCourses,
      testsCompleted
    }
  }
}
</script>

<style scoped>
.user-statistics {
  @apply w-full;
}

.stat-card {
  @apply bg-white p-5 rounded-2xl border border-gray-100 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1;
}

.stat-icon {
  @apply w-10 h-10 rounded-xl flex items-center justify-center transition-colors duration-300;
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Custom Scrollbar */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}
.overflow-x-auto::-webkit-scrollbar-track {
  background: #f8fafc;
  border-radius: 4px;
}
.overflow-x-auto::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}
.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
