<template>
  <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Course Header -->
        <div class="card p-8 mb-8">
          <div class="flex flex-col lg:flex-row gap-8">
            <div class="lg:w-2/3">
              <div class="flex items-center gap-2 mb-4">
                <el-tag
                  type="primary"
                  size="small"
                >
                  {{ course.category }}
                </el-tag>
                <el-tag
                  type="success"
                  size="small"
                >
                  {{ course.level }}
                </el-tag>
              </div>
              <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                {{ course.title }}
              </h1>
              <p class="text-xl text-gray-600 mb-6">
                {{ course.description }}
              </p>
              
              <div class="flex items-center gap-6 mb-6">
                <div class="flex items-center gap-2">
                  <el-rate
                    v-model="course.rating"
                    disabled
                    show-score
                    text-color="#ff9900"
                  />
                  <span class="text-gray-600">({{ course.reviews }} {{ $t('courseDetail.reviews') }})</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                    />
                  </svg>
                  <span class="text-gray-600">{{ course.students }} {{ $t('courseDetail.students') }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg
                    class="w-5 h-5 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
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
                  <svg
                    class="w-16 h-16 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <el-button
                  type="primary"
                  size="large"
                  class="w-full mb-4"
                >
                  {{ $t('courseDetail.enroll') }}
                </el-button>
                <el-button
                  size="large"
                  class="w-full mb-4"
                >
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
            <!-- Lessons Sidebar -->
            <div class="card p-4 mb-6">
              <h3 class="text-lg font-semibold mb-4">
                {{ $t('courseDetail.lessons') || 'Уроки курса' }}
              </h3>
              <div class="space-y-2 max-h-96 overflow-y-auto">
                <div
                  v-for="(lesson, index) in allLessons"
                  :key="lesson.id"
                  class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-blue-50 border"
                  :class="{
                    'bg-blue-50 border-blue-200': currentLessonIndex === index,
                    'border-gray-200': currentLessonIndex !== index
                  }"
                  @click="playLesson(index)"
                >
                  <div
                    class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                    :class="lesson.completed ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'"
                  >
                    <svg
                      v-if="lesson.completed"
                      class="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                    <span
                      v-else
                      class="text-xs font-semibold"
                    >{{ index + 1 }}</span>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ lesson.title }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ lesson.duration }}
                    </p>
                  </div>
                  <svg
                    class="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
            </div>

            <!-- Lesson Materials -->
            <div
              v-if="currentLesson && lessonMaterials[currentLesson.id]?.length > 0"
              class="card p-6 mb-6"
            >
              <h3 class="text-lg font-semibold mb-4">
                Материалы урока
              </h3>
              <div class="space-y-2">
                <div 
                  v-for="file in lessonMaterials[currentLesson.id]" 
                  :key="file.objectName"
                  class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors cursor-pointer"
                  @click="downloadMaterial(file)"
                >
                  <el-icon
                    :size="24"
                    class="text-blue-600"
                  >
                    <Document />
                  </el-icon>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ file.original_name || file.originalName }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ file.sizeFormatted }}
                    </p>
                  </div>
                  <el-icon class="text-blue-600">
                    <Download />
                  </el-icon>
                </div>
              </div>
            </div>

            <!-- Tabs -->
            <el-tabs
              v-model="activeTab"
              class="mb-8"
            >
              <el-tab-pane
                :label="$t('courseDetail.tabs.description')"
                name="description"
              >
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">
                    {{ $t('courseDetail.aboutCourse') }}
                  </h3>
                  <div class="prose max-w-none">
                    <p class="text-gray-600 mb-4">
                      {{ course.fullDescription }}
                    </p>
                    <h4 class="text-lg font-semibold mb-3">
                      {{ $t('courseDetail.whatYouLearn') }}
                    </h4>
                    <ul class="list-disc list-inside text-gray-600 space-y-2">
                      <li
                        v-for="item in course.whatYouLearn"
                        :key="item"
                      >
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>
              </el-tab-pane>
              
              <el-tab-pane
                :label="$t('courseDetail.tabs.curriculum')"
                name="curriculum"
              >
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">
                    {{ $t('courseDetail.curriculum') }}
                  </h3>
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
                            <svg
                              v-if="lesson.type === 'video'"
                              class="w-5 h-5 text-blue-600"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                              />
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                            <svg
                              v-else
                              class="w-5 h-5 text-blue-600"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                              />
                            </svg>
                            <span>{{ lesson.title }}</span>
                          </div>
                          <span class="text-gray-500">{{ lesson.duration }}</span>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              
              <el-tab-pane
                :label="$t('courseDetail.tabs.reviews')"
                name="reviews"
              >
                <div class="card p-6">
                  <h3 class="text-xl font-semibold mb-4">
                    {{ $t('courseDetail.studentReviews') }}
                  </h3>
                  <div class="space-y-6">
                    <div 
                      v-for="review in course.reviews" 
                      :key="review.id"
                      class="border-b border-gray-200 pb-6 last:border-b-0"
                    >
                      <div class="flex items-center gap-4 mb-3">
                        <el-avatar :src="review.avatar" />
                        <div>
                          <h4 class="font-semibold">
                            {{ review.name }}
                          </h4>
                          <el-rate
                            v-model="review.rating"
                            disabled
                            size="small"
                          />
                        </div>
                      </div>
                      <p class="text-gray-600">
                        {{ review.text }}
                      </p>
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
              <h3 class="text-lg font-semibold mb-4">
                {{ $t('courseDetail.instructor') }}
              </h3>
              <div class="flex items-center gap-4 mb-4">
                <el-avatar
                  :size="60"
                  :src="course.instructor.avatar"
                />
                <div>
                  <h4 class="font-semibold">
                    {{ course.instructor.name }}
                  </h4>
                  <p class="text-gray-600 text-sm">
                    {{ course.instructor.title }}
                  </p>
                </div>
              </div>
              <p class="text-gray-600 text-sm mb-4">
                {{ course.instructor.bio }}
              </p>
              <el-button
                size="small"
                class="w-full"
              >
                {{ $t('courseDetail.sendMessage') }}
              </el-button>
            </div>

            <!-- Similar Courses -->
            <div class="card p-6">
              <h3 class="text-lg font-semibold mb-4">
                {{ $t('courseDetail.similarCourses') }}
              </h3>
              <div class="space-y-4">
                <div 
                  v-for="similarCourse in similarCourses" 
                  :key="similarCourse.id"
                  class="flex gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg"
                  @click="$router.push(`/course/${similarCourse.id}`)"
                >
                  <div class="w-16 h-12 bg-gradient-to-br from-blue-100 to-orange-100 rounded flex items-center justify-center">
                    <svg
                      class="w-8 h-8 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                      />
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                      />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h4 class="font-medium text-sm">
                      {{ similarCourse.title }}
                    </h4>
                    <div class="flex items-center gap-2 mt-1">
                      <el-rate
                        v-model="similarCourse.rating"
                        disabled
                        size="small"
                      />
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

    <!-- Video Player -->
    <el-dialog
      v-model="showVideoPlayer"
      :title="currentLesson?.title || 'Видеоурок'"
      width="90%"
      :before-close="handleVideoClose"
      @close="handleVideoClose"
    >
      <EducationalVideoPlayer
        v-if="currentLesson?.videoUrl"
        :source="currentLesson.videoUrl"
        :require-auth="false"
        :save-progress="true"
        :progress-key="`lesson_${currentLesson.id}`"
        @ended="handleVideoEnd"
      />
      <template #footer>
        <div class="flex items-center justify-between w-full">
          <el-button
            :disabled="currentLessonIndex === 0"
            @click="playPrevious"
          >
            <el-icon class="mr-2">
              <ArrowLeft />
            </el-icon>
            Предыдущий урок
          </el-button>
          <el-button
            type="primary"
            :disabled="currentLessonIndex >= allLessons.length - 1"
            @click="playNext"
          >
            Следующий урок
            <el-icon class="ml-2">
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </template>
    </el-dialog>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Document, Download } from '@element-plus/icons-vue'
import EducationalVideoPlayer from '@/components/video/EducationalVideoPlayer.vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import videoService from '@/services/videoService'
import authService from '@/services/auth'
import minioService from '@/services/minioService'

export default {
  name: 'CourseDetail',
  components: {
    EducationalVideoPlayer,
    Document,
    Download,
    ArrowLeft,
    ArrowRight
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
    const showVideoPlayer = ref(false)
    const currentLessonIndex = ref(0)
    const currentLesson = ref(null)
    const lessonMaterials = ref({}) // { lessonId: [files] }
    const loadingMaterials = ref(false)
    
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

    // Получаем все уроки из курса
    const allLessons = computed(() => {
      const lessons = []
      course.value.curriculum.forEach((section, sectionIndex) => {
        section.lessons.forEach((lesson, lessonIndex) => {
          lessons.push({
            ...lesson,
            sectionIndex,
            sectionTitle: section.title,
            completed: false
          })
        })
      })
      return lessons
    })

    // Играть урок
    const playLesson = async (index) => {
      currentLessonIndex.value = index
      currentLesson.value = allLessons.value[index]
      
      // Для демо используем тестовые видео
      // В продакшене: await videoService.getVideoUrl(currentLesson.value.id)
      currentLesson.value.videoUrl = `https://storage.googleapis.com/gtv-videos-bucket/sample/${['BigBuckBunny', 'ElephantsDream', 'ForBiggerBlazes'][index % 3]}.mp4`
      
      // Загружаем материалы для урока из MinIO
      await loadLessonMaterials(currentLesson.value.title)
      
      // Загружаем прогресс
      const currentUser = authService.getCurrentUser()
      if (currentUser && currentLesson.value.id) {
        const progressResult = await videoService.getLessonProgress(
          currentUser.id, 
          currentLesson.value.id
        )
        if (progressResult.success && progressResult.progress) {
          // Применяем сохраненную позицию к видео
        }
      }
      
      showVideoPlayer.value = true
    }

    // Загрузить материалы урока из MinIO
    const loadLessonMaterials = async (lessonTitle) => {
      if (!lessonTitle) return
      
      try {
        loadingMaterials.value = true
        
        // Создаем folder path из названия урока
        // Экранируем специальные символы для MinIO
        const folderName = lessonTitle.replace(/[<>:"/\\|?*]/g, '_')
        
        // Получаем содержимое папки с этим названием
        const contents = await minioService.getFolderContents(folderName)
        
        // Сохраняем файлы для текущего урока
        if (currentLesson.value) {
          lessonMaterials.value[currentLesson.value.id] = contents.files
        }
      } catch (error) {
        console.error('Ошибка загрузки материалов урока:', error)
        // Не показываем ошибку, если папка не найдена
        if (!error.message.includes('Not Found')) {
          ElMessage.warning(`Не удалось загрузить материалы для урока: ${lessonTitle}`)
        }
      } finally {
        loadingMaterials.value = false
      }
    }

    // Скачать материалы урока
    const downloadMaterial = (file) => {
      if (file.file_url || file.url) {
        const link = document.createElement('a')
        link.href = file.file_url || file.url
        link.download = file.original_name || file.originalName
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }

    // Обработчики видеоплеера
    const handleVideoEnd = async () => {
      // Отмечаем урок как завершенный
      if (allLessons.value[currentLessonIndex.value]) {
        allLessons.value[currentLessonIndex.value].completed = true
        
        // Сохраняем прогресс
        const currentUser = authService.getCurrentUser()
        if (currentUser && currentLesson.value.id) {
          await videoService.completeLesson(currentUser.id, currentLesson.value.id)
          ElMessage.success('Урок завершен!')
        }
      }
    }

    const handleVideoClose = () => {
      showVideoPlayer.value = false
    }

    const playNext = () => {
      if (currentLessonIndex.value < allLessons.value.length - 1) {
        playLesson(currentLessonIndex.value + 1)
      }
    }

    const playPrevious = () => {
      if (currentLessonIndex.value > 0) {
        playLesson(currentLessonIndex.value - 1)
      }
    }
    
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
      similarCourses,
      allLessons,
      showVideoPlayer,
      currentLessonIndex,
      currentLesson,
      lessonMaterials,
      loadingMaterials,
      playLesson,
      loadLessonMaterials,
      downloadMaterial,
      handleVideoEnd,
      handleVideoClose,
      playNext,
      playPrevious
    }
  }
}
</script>
