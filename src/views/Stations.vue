<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="text-center mb-12">
          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Компрессорные станции
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Обучающие программы по эксплуатации и техническому обслуживанию компрессорных станций газопровода
          </p>
        </div>

        <!-- Stations Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <div 
            v-for="station in stations" 
            :key="station.id"
            class="card-hover overflow-hidden"
          >
            <div class="aspect-video relative overflow-hidden">
              <img 
                :src="`/stations/${station.image}`" 
                :alt="station.name"
                class="w-full h-full object-cover"
              />
              <div class="absolute inset-0 bg-black bg-opacity-20"></div>
              <div class="absolute top-4 right-4">
                <el-tag 
                  :type="station.status === 'active' ? 'success' : 'warning'"
                  size="small"
                >
                  {{ station.status === 'active' ? 'Активна' : 'В ремонте' }}
                </el-tag>
              </div>
            </div>
            
            <div class="p-6">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                {{ station.name }}
              </h3>
              
              <p class="text-gray-600 mb-4">
                {{ station.description }}
              </p>
              
              <div class="space-y-2 mb-4">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-500">Мощность:</span>
                  <span class="font-medium">{{ station.power }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-500">Дата ввода:</span>
                  <span class="font-medium">{{ station.commissionDate }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-500">Курсов:</span>
                  <span class="font-medium">{{ station.coursesCount }}</span>
                </div>
              </div>
              
              <div class="flex gap-2">
                <el-button 
                  @click="$router.push(`/station/${station.id}`)"
                  type="primary"
                  class="flex-1"
                >
                  Подробнее
                </el-button>
                <el-button 
                  @click="$router.push(`/station/${station.id}/courses`)"
                  type="success"
                  plain
                >
                  Курсы
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Pipeline Map -->
        <div class="card p-8 mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Схема газопровода
          </h2>
          <div class="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-8">
            <div class="flex items-center justify-between mb-8">
              <div class="text-center">
                <div class="w-4 h-4 bg-green-500 rounded-full mx-auto mb-2"></div>
                <span class="text-sm font-medium">Туркменистан</span>
              </div>
              <div class="flex-1 h-1 bg-blue-500 mx-4"></div>
              <div class="text-center">
                <div class="w-4 h-4 bg-blue-500 rounded-full mx-auto mb-2"></div>
                <span class="text-sm font-medium">Узбекистан</span>
              </div>
              <div class="flex-1 h-1 bg-blue-500 mx-4"></div>
              <div class="text-center">
                <div class="w-4 h-4 bg-blue-500 rounded-full mx-auto mb-2"></div>
                <span class="text-sm font-medium">Казахстан</span>
              </div>
              <div class="flex-1 h-1 bg-blue-500 mx-4"></div>
              <div class="text-center">
                <div class="w-4 h-4 bg-red-500 rounded-full mx-auto mb-2"></div>
                <span class="text-sm font-medium">Китай</span>
              </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div 
                v-for="station in stations" 
                :key="station.id"
                class="text-center"
              >
                <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span class="text-white text-xs font-bold">{{ station.id }}</span>
                </div>
                <span class="text-xs font-medium">{{ station.shortName }}</span>
              </div>
            </div>
            
            <div class="mt-6 text-center text-gray-600">
              <p class="text-sm">Общая протяженность: <span class="font-semibold">1586 км</span></p>
              <p class="text-sm">Годовая пропускная способность: <span class="font-semibold">55 млрд м³</span></p>
            </div>
          </div>
        </div>

        <!-- Training Programs -->
        <div class="card p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">
            Программы обучения
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div 
              v-for="program in trainingPrograms" 
              :key="program.id"
              class="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-colors"
            >
              <div class="flex items-center gap-4 mb-4">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <el-icon :size="24" class="text-blue-600">
                    <component :is="program.icon" />
                  </el-icon>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">{{ program.title }}</h3>
                  <p class="text-sm text-gray-600">{{ program.duration }}</p>
                </div>
              </div>
              
              <p class="text-gray-600 mb-4">{{ program.description }}</p>
              
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <el-icon class="text-gray-500"><User /></el-icon>
                  <span class="text-sm text-gray-600">{{ program.participants }} участников</span>
                </div>
                <el-button @click="$router.push(`/program/${program.id}`)" type="primary" size="small">
                  Подробнее
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Stations',
  components: {
    AppLayout
  },
  setup() {
    const stations = ref([
      {
        id: 1,
        name: 'Компрессорная станция WKC1',
        shortName: 'WKC1',
        description: 'Головная компрессорная станция в Миришкорском районе Кашкадарьинской области',
        image: 'WKC1.jpg',
        power: '25 МВт',
        commissionDate: '25.11.2009',
        coursesCount: 8,
        status: 'active'
      },
      {
        id: 2,
        name: 'Компрессорная станция WKC2',
        shortName: 'WKC2',
        description: 'Компрессорная станция на участке газопровода',
        image: 'WKC2.jpg',
        power: '22 МВт',
        commissionDate: '01.12.2009',
        coursesCount: 7,
        status: 'active'
      },
      {
        id: 3,
        name: 'Компрессорная станция WKC3',
        shortName: 'WKC3',
        description: 'Компрессорная станция на участке газопровода',
        image: 'WKC3.jpg',
        power: '20 МВт',
        commissionDate: '15.06.2010',
        coursesCount: 6,
        status: 'active'
      },
      {
        id: 4,
        name: 'Компрессорная станция UCS1',
        shortName: 'UCS1',
        description: 'Компрессорная станция на территории Бухарской области',
        image: 'UCS1.jpg',
        power: '20 МВт',
        commissionDate: '30.07.2014',
        coursesCount: 6,
        status: 'active'
      },
      {
        id: 5,
        name: 'Компрессорная станция UCS3',
        shortName: 'UCS3',
        description: 'Компрессорная станция в Навоийской области',
        image: 'UCS3.jpg',
        power: '18 МВт',
        commissionDate: '30.07.2014',
        coursesCount: 5,
        status: 'active'
      },
      {
        id: 6,
        name: 'Газокомпрессорная станция GCS',
        shortName: 'GCS',
        description: 'Газокомпрессорная станция на магистральном газопроводе',
        image: 'GCS.jpg',
        power: '24 МВт',
        commissionDate: '20.08.2010',
        coursesCount: 7,
        status: 'active'
      },
      {
        id: 7,
        name: 'Модульная станция MS',
        shortName: 'MS',
        description: 'Модульная компрессорная станция',
        image: 'MS.jpg',
        power: '16 МВт',
        commissionDate: '10.05.2012',
        coursesCount: 4,
        status: 'active'
      },
      {
        id: 8,
        name: 'Узбекская компрессорная станция UKMS',
        shortName: 'UKMS',
        description: 'Узбекская компрессорная станция магистрального газопровода',
        image: 'UKMS.jpg',
        power: '21 МВт',
        commissionDate: '12.03.2011',
        coursesCount: 6,
        status: 'maintenance'
      }
    ])

    const trainingPrograms = ref([
      {
        id: 1,
        title: 'Эксплуатация компрессорных станций',
        description: 'Обучение персонала работе с газокомпрессорным оборудованием',
        icon: 'Setting',
        duration: '40 часов',
        participants: 45
      },
      {
        id: 2,
        title: 'Техническое обслуживание',
        description: 'Плановое и аварийное обслуживание оборудования',
        icon: 'Tools',
        duration: '32 часа',
        participants: 38
      },
      {
        id: 3,
        title: 'Безопасность на объектах',
        description: 'Промышленная безопасность и охрана труда',
        icon: 'Shield',
        duration: '24 часа',
        participants: 52
      },
      {
        id: 4,
        title: 'Системы автоматизации',
        description: 'Работа с системами контроля и управления',
        icon: 'Monitor',
        duration: '28 часов',
        participants: 31
      }
    ])

    return {
      stations,
      trainingPrograms
    }
  }
}
</script>
