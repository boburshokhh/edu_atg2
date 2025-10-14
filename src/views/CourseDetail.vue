<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Course Header -->
        <div class="card p-8 mb-8">
          <div class="flex flex-col lg:flex-row gap-8">
            <div class="lg:w-2/3">
              <div class="flex items-center gap-2 mb-4">
                <el-tag type="primary" size="small">{{ course.category }}</el-tag>
                <el-tag type="success" size="small">{{ course.level }}</el-tag>
              </div>
              <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                {{ course.title }}
              </h1>
              <p class="text-xl text-gray-600 mb-6">
                {{ course.description }}
              </p>
              
              <div class="flex items-center gap-6 mb-6">
                <div class="flex items-center gap-2">
                  <el-rate v-model="course.rating" disabled show-score text-color="#ff9900" />
                  <span class="text-gray-600">({{ course.reviews }} {{ $t('courseDetail.reviews') }})</span>
                </div>
                <div class="flex items-center gap-2">
                  <el-icon><User /></el-icon>
                  <span class="text-gray-600">{{ course.students }} {{ $t('courseDetail.students') }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <el-icon><Clock /></el-icon>
                  <span class="text-gray-600">{{ course.duration }}</span>
                </div>
              </div>
              
              <div class="flex items-center gap-4">
                <span class="text-3xl font-bold text-blue-600">{{ $t('courseDetail.free') }}</span>
              </div>
            </div>
            
            <div class="lg:w-1/3">
              <div class="card p-6">
                <div class="aspect-video bg-gradient-to-br from-blue-100 to-orange-100 rounded-lg flex items-center justify-center mb-4">
                  <el-icon :size="64" class="text-blue-600">
                    <component :is="course.icon" />
                  </el-icon>
                </div>
                <el-button type="primary" size="large" class="w-full mb-4">
                  {{ $t('courseDetail.enroll') }}
                </el-button>
                <el-button size="large" class="w-full mb-4">
                  {{ $t('courseDetail.addToFavorites') }}
                </el-button>
                <div class="text-center text-gray-600">
                  <p>{{ $t('courseDetail.guarantee') }}</p>
                  <p>{{ $t('courseDetail.lifetimeAccess') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Course Content -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content -->
          <div class="lg:col-span-2">
            <!-- Tabs -->
            <el-tabs v-model="activeTab" class="mb-8">
              <el-tab-pane :label="$t('courseDetail.tabs.description')" name="description">
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">{{ $t('courseDetail.aboutCourse') }}</h3>
                  <div class="prose max-w-none">
                    <p class="text-gray-600 mb-4">
                      {{ course.fullDescription }}
                    </p>
                    <h4 class="text-lg font-semibold mb-3">{{ $t('courseDetail.whatYouLearn') }}</h4>
                    <ul class="list-disc list-inside text-gray-600 space-y-2">
                      <li v-for="item in course.whatYouLearn" :key="item">{{ item }}</li>
                    </ul>
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane :label="$t('courseDetail.tabs.curriculum')" name="curriculum">
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">{{ $t('courseDetail.curriculum') }}</h3>
                  <el-collapse v-model="activeCollapse">
                    <el-collapse-item 
                      v-for="(section, index) in course.curriculum" 
                      :key="index"
                      :title="section.title"
                      :name="index"
                    >
                      <div class="space-y-3">
                        <div 
                          v-for="lesson in section.lessons" 
                          :key="lesson.id"
                          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div class="flex items-center gap-3">
                            <el-icon class="text-blue-600">
                              <component :is="lesson.type === 'video' ? 'VideoPlay' : 'Document'" />
                            </el-icon>
                            <span>{{ lesson.title }}</span>
                          </div>
                          <span class="text-gray-500">{{ lesson.duration }}</span>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              
              <el-tab-pane :label="$t('courseDetail.tabs.reviews')" name="reviews">
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">{{ $t('courseDetail.studentReviews') }}</h3>
                  <div class="space-y-6">
                    <div 
                      v-for="review in course.reviews" 
                      :key="review.id"
                      class="border-b border-gray-200 pb-6 last:border-b-0"
                    >
                      <div class="flex items-center gap-4 mb-3">
                        <el-avatar :src="review.avatar" />
                        <div>
                          <h4 class="font-semibold">{{ review.name }}</h4>
                          <el-rate v-model="review.rating" disabled size="small" />
                        </div>
                      </div>
                      <p class="text-gray-600">{{ review.text }}</p>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- Sidebar -->
          <div class="lg:col-span-1">
            <!-- Instructor -->
            <div class="card p-6 mb-6">
              <h3 class="text-lg font-semibold mb-4">{{ $t('courseDetail.instructor') }}</h3>
              <div class="flex items-center gap-4 mb-4">
                <el-avatar :size="60" :src="course.instructor.avatar" />
                <div>
                  <h4 class="font-semibold">{{ course.instructor.name }}</h4>
                  <p class="text-gray-600 text-sm">{{ course.instructor.title }}</p>
                </div>
              </div>
              <p class="text-gray-600 text-sm mb-4">{{ course.instructor.bio }}</p>
              <el-button size="small" class="w-full">{{ $t('courseDetail.sendMessage') }}</el-button>
            </div>

            <!-- Similar Courses -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold mb-4">{{ $t('courseDetail.similarCourses') }}</h3>
              <div class="space-y-4">
                <div 
                  v-for="similarCourse in similarCourses" 
                  :key="similarCourse.id"
                  class="flex gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg"
                  @click="$router.push(`/course/${similarCourse.id}`)"
                >
                  <div class="w-16 h-12 bg-gradient-to-br from-blue-100 to-orange-100 rounded flex items-center justify-center">
                    <el-icon class="text-blue-600">
                      <component :is="similarCourse.icon" />
                    </el-icon>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-sm">{{ similarCourse.title }}</h4>
                    <div class="flex items-center gap-2 mt-1">
                      <el-rate v-model="similarCourse.rating" disabled size="small" />
                      <span class="text-xs text-gray-500">{{ $t('courseDetail.free') }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppLayout from '@/components/AppLayout.vue'
import { 
  User, 
  Clock, 
  VideoPlay, 
  Document, 
  Setting, 
  Lock, 
  Tools, 
  Monitor, 
  Star 
} from '@element-plus/icons-vue'

export default {
  name: 'CourseDetail',
  components: {
    AppLayout,
    User,
    Clock,
    VideoPlay,
    Document,
    Setting,
    Lock,
    Tools,
    Monitor,
    Star
  },
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const { t } = useI18n()
    const activeTab = ref('description')
    const activeCollapse = ref([0])
    
    const course = ref({
      id: 1,
      title: 'Компрессорная станция WKC1',
      description: 'Изучите основы эксплуатации компрессорной станции WKC1. От технических характеристик до процедур безопасности.',
      fullDescription: 'Этот курс предназначен для операторов и технических специалистов, работающих с компрессорными станциями. Вы изучите все аспекты эксплуатации станции WKC1, включая технические характеристики, процедуры запуска и остановки, мониторинг параметров и обеспечение безопасности.',
      icon: 'Setting',
      category: 'Техническое обучение',
      level: 'Средний',
      rating: 4.8,
      reviews: 1250,
      students: 5000,
      duration: '40 часов',
      whatYouLearn: [
        'Технические характеристики КС WKC1',
        'Процедуры запуска и остановки',
        'Мониторинг параметров работы',
        'Процедуры безопасности',
        'Техническое обслуживание',
        'Устранение неисправностей'
      ],
      curriculum: [
        {
          title: 'Введение в КС WKC1',
          lessons: [
            { id: 1, title: 'Обзор станции и оборудования', type: 'video', duration: '15 мин' },
            { id: 2, title: 'Технические характеристики', type: 'video', duration: '20 мин' },
            { id: 3, title: 'Системы безопасности', type: 'video', duration: '25 мин' },
            { id: 4, title: 'Практическое задание', type: 'document', duration: '30 мин' }
          ]
        },
        {
          title: 'Эксплуатация станции',
          lessons: [
            { id: 5, title: 'Процедуры запуска', type: 'video', duration: '20 мин' },
            { id: 6, title: 'Мониторинг параметров', type: 'video', duration: '25 мин' },
            { id: 7, title: 'Процедуры остановки', type: 'video', duration: '30 мин' }
          ]
        }
      ],
      reviews: [
        {
          id: 1,
          name: 'Анна Петрова',
          avatar: '',
          rating: 5,
          text: 'Отличный курс для операторов! Все объясняется очень понятно и доступно.'
        },
        {
          id: 2,
          name: 'Михаил Иванов',
          avatar: '',
          rating: 4,
          text: 'Хорошая структура курса, много практических заданий. Рекомендую!'
        }
      ],
      instructor: {
        name: 'Дмитрий Смирнов',
        title: 'Главный инженер КС WKC1',
        avatar: '',
        bio: 'Опытный инженер с 15-летним стажем работы с компрессорными станциями. Специализируется на эксплуатации и техническом обслуживании газотранспортного оборудования.'
      }
    })
    
    const similarCourses = ref([
      {
        id: 2,
        title: 'Промышленная безопасность',
        icon: 'Lock',
        rating: 4.8
      },
      {
        id: 3,
        title: 'Техническое обслуживание',
        icon: 'Tools',
        rating: 4.7
      },
      {
        id: 4,
        title: 'Системы автоматизации',
        icon: 'Monitor',
        rating: 4.9
      }
    ])
    
    onMounted(() => {
      // Здесь можно загрузить данные курса по ID
      console.log('Course ID:', props.id || route.params.id)
    })
    
    return {
      activeTab,
      activeCollapse,
      course,
      similarCourses
    }
  }
}
</script>
