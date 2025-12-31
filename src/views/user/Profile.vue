<template>
  <AppLayout>
    <div class="bg-gray-50 min-h-screen pt-24 sm:pt-28 lg:pt-32 pb-8 sm:pb-12 lg:pb-20">
      <div class="page-container">
        <!-- Header -->
        <div class="mb-6 sm:mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-[clamp(1.5rem,4.5vw,1.875rem)] sm:text-3xl font-bold text-gray-900 mb-1.5 sm:mb-2 leading-tight">
              Профиль сотрудника
            </h1>
            <p class="text-gray-600 text-sm sm:text-base">
              Персональная информация и настройки
            </p>
          </div>
          <el-button
            type="primary"
            :icon="Edit"
            :disabled="loading"
            class="w-full md:w-auto justify-center"
            @click="openEditModal"
          >
            Редактировать
          </el-button>
        </div>

        <!-- Loading State -->
        <div
          v-if="loading"
          class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6 lg:gap-8"
        >
          <div class="lg:col-span-1">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item
                  variant="image"
                  style="width: 100%; height: 400px; border-radius: 16px;"
                />
              </template>
            </el-skeleton>
          </div>
          <div class="lg:col-span-2">
            <el-skeleton
              animated
              :rows="10"
            />
          </div>
        </div>

        <!-- Content -->
        <div
          v-else
          class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6 lg:gap-8"
        >
          <!-- Карточка профиля (Левая колонка) -->
          <div class="lg:col-span-1">
            <div class="card bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <!-- Верхняя часть с фоном -->
              <div class="h-32 bg-gradient-to-r from-blue-600 to-blue-800 relative overflow-hidden">
                <div class="absolute inset-0 opacity-20 pattern-dots" />
              </div>
              
              <!-- Аватар и основная инфо -->
              <div class="px-4 sm:px-6 pb-5 sm:pb-6 relative">
                <div class="relative -mt-16 mb-4 flex justify-center">
                  <div class="relative group">
                    <el-avatar 
                      :size="avatarSize" 
                      :src="user.avatar" 
                      class="border-4 border-white shadow-lg bg-white text-4xl font-bold text-gray-400 flex items-center justify-center"
                    >
                      <img
                        v-if="user.avatar"
                        :src="user.avatar"
                        class="w-full h-full object-cover"
                      >
                      <span v-else>{{ user.name ? user.name.charAt(0).toUpperCase() : 'U' }}</span>
                    </el-avatar>
                    
                    <!-- Кнопка загрузки поверх аватара -->
                    <div class="absolute inset-0 rounded-full overflow-hidden">
                      <el-upload
                        class="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-300 cursor-pointer"
                        action="#"
                        :auto-upload="false"
                        :on-change="handleAvatarChange"
                        :show-file-list="false"
                        accept="image/jpeg,image/png,image/webp"
                      >
                        <div class="text-center">
                          <el-icon class="text-white text-2xl mb-1">
                            <Camera />
                          </el-icon>
                          <p class="text-white text-xs font-medium">
                            Изменить
                          </p>
                        </div>
                      </el-upload>
                    </div>
                    
                    <!-- Индикатор загрузки -->
                    <div
                      v-if="uploading"
                      class="absolute inset-0 flex items-center justify-center bg-white/80 rounded-full z-10"
                    >
                      <el-icon class="is-loading text-blue-600 text-2xl">
                        <Loading />
                      </el-icon>
                    </div>
                  </div>
                </div>

                <div class="text-center mb-5 sm:mb-6">
                  <h2 class="text-xl sm:text-2xl font-bold text-gray-900 mb-1 break-words leading-tight">
                    {{ user.name || 'Пользователь' }}
                  </h2>
                  <p class="text-blue-600 font-medium mb-1 text-sm sm:text-base">
                    {{ user.position || 'Должность не указана' }}
                  </p>
                </div>

                <el-divider class="!my-6" />

                <!-- Детальная информация -->
                <div class="space-y-4 sm:space-y-5">
                  <div class="flex items-center gap-3 sm:gap-4 group">
                    <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors shrink-0">
                      <el-icon><Message /></el-icon>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-0.5">
                        Email
                      </p>
                      <p class="text-gray-900 font-medium truncate" :title="user.email">
                        {{ user.email || 'Не указан' }}
                      </p>
                    </div>
                  </div>

                  <!-- Отдел (показываем только если станция не выбрана) -->
                  <div 
                    v-if="!user.station && user.department"
                    class="flex items-center gap-3 sm:gap-4 group"
                  >
                    <div class="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-600 group-hover:bg-orange-100 transition-colors shrink-0">
                      <el-icon><OfficeBuilding /></el-icon>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-0.5">
                        Отдел
                      </p>
                      <p class="text-gray-900 font-medium truncate">
                        {{ user.department }}
                      </p>
                    </div>
                  </div>

                  <div class="flex items-center gap-3 sm:gap-4 group">
                    <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-green-600 group-hover:bg-green-100 transition-colors shrink-0">
                      <el-icon><Suitcase /></el-icon>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-gray-500 text-xs uppercase tracking-wider font-semibold mb-0.5">
                        Должность
                      </p>
                      <p class="text-gray-900 font-medium truncate">
                        {{ user.position || 'Не указана' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Краткая статистика -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
              <div class="card bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-gray-100 text-center hover:shadow-md transition-shadow">
                <p class="text-2xl sm:text-3xl font-bold text-blue-600 mb-1 leading-tight">
                  {{ userStats.completedCourses }}
                </p>
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">
                  Курсов пройдено
                </p>
              </div>
              <div class="card bg-white p-4 sm:p-5 rounded-xl shadow-sm border border-gray-100 text-center hover:shadow-md transition-shadow">
                <p class="text-2xl sm:text-3xl font-bold text-orange-600 mb-1 leading-tight">
                  {{ userStats.hoursStudied }}
                </p>
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">
                  Часов обучения
                </p>
              </div>
            </div>
          </div>

          <!-- Контент (Правая колонка) -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[600px] flex flex-col overflow-hidden">
              <el-tabs
                v-model="activeTab"
                class="profile-tabs flex-1"
              >
                <el-tab-pane
                  label="Мои курсы"
                  name="courses"
                >
                  <div class="p-4 sm:p-6">
                    <div
                      v-if="userCourses.length"
                      class="space-y-3 sm:space-y-4"
                    >
                      <div 
                        v-for="course in userCourses" 
                        :key="course.id"
                        class="group flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 p-4 sm:p-5 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all cursor-pointer"
                        @click="$router.push(`/course/${course.course_id || course.id}`)"
                      >
                        <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600 shrink-0 group-hover:scale-110 transition-transform">
                          <el-icon :size="isMobile ? 24 : 28">
                            <component :is="course.course?.icon || 'Monitor'" />
                          </el-icon>
                        </div>
                        <div class="flex-1 min-w-0 w-full">
                          <div class="flex flex-wrap justify-between items-start gap-2 mb-2">
                            <h3 class="font-bold text-gray-900 text-base sm:text-lg leading-tight group-hover:text-blue-600 transition-colors">
                              {{ course.course?.title || course.title }}
                            </h3>
                            <span 
                              class="px-2.5 py-1 rounded-full text-xs font-medium shrink-0"
                              :class="getStatusClass(course.status)"
                            >
                              {{ getStatusLabel(course.status) }}
                            </span>
                          </div>
                          
                          <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 mt-3">
                            <div class="flex-1 w-full">
                              <div class="flex justify-between text-xs text-gray-500 mb-1.5">
                                <span>Прогресс</span>
                                <span class="font-medium text-gray-700">{{ course.progress_percent || 0 }}%</span>
                              </div>
                              <el-progress 
                                :percentage="course.progress_percent || 0" 
                                :stroke-width="8" 
                                :show-text="false"
                                :color="customColors"
                              />
                            </div>
                            <div class="hidden sm:flex text-xs text-gray-400 shrink-0 items-center gap-1">
                              <el-icon><Clock /></el-icon>
                              <span>Обновлено: {{ formatDate(course.last_activity) }}</span>
                            </div>
                          </div>
                        </div>
                        <div class="hidden sm:flex items-center justify-center w-10 h-10 rounded-full border border-gray-200 text-gray-400 group-hover:border-blue-200 group-hover:text-blue-600 group-hover:bg-white transition-all shrink-0">
                          <el-icon><ArrowRight /></el-icon>
                        </div>
                      </div>
                    </div>
                    
                    <div
                      v-else
                      class="flex flex-col items-center justify-center py-12 text-center"
                    >
                      <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                        <el-icon class="text-gray-300 text-4xl">
                          <Collection />
                        </el-icon>
                      </div>
                      <h3 class="text-lg font-medium text-gray-900 mb-2">
                        Нет активных курсов
                      </h3>
                      <p class="text-gray-500 max-w-xs mx-auto mb-6">
                        Вы пока не записаны ни на один курс. Перейдите в каталог, чтобы начать обучение.
                      </p>
                      <el-button
                        type="primary"
                        @click="$router.push('/stations')"
                      >
                        Перейти к курсам
                      </el-button>
                    </div>
                  </div>
                </el-tab-pane>

                <!-- Вкладка Статистики -->
                <el-tab-pane
                  label="Детальная статистика"
                  name="stats"
                >
                  <div class="p-4 sm:p-6">
                    <UserStatistics :detailed="true" />
                  </div>
                </el-tab-pane>

                <el-tab-pane
                  label="Настройки"
                  name="settings"
                >
                  <div class="p-6 max-w-2xl">
                    <div class="space-y-8">
                      <!-- Уведомления -->
                      <div>
                        <div class="flex items-center gap-3 mb-6">
                          <div class="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600">
                            <el-icon size="20">
                              <Bell />
                            </el-icon>
                          </div>
                          <div>
                            <h3 class="font-bold text-gray-900">
                              Уведомления
                            </h3>
                            <p class="text-sm text-gray-500">
                              Управление оповещениями
                            </p>
                          </div>
                        </div>
                        
                        <div class="bg-gray-50 rounded-xl p-4 space-y-4 border border-gray-100">
                          <div class="flex items-center justify-between">
                            <div>
                              <p class="font-medium text-gray-900">
                                Email рассылка
                              </p>
                              <p class="text-xs text-gray-500">
                                Получать новости и отчеты на почту
                              </p>
                            </div>
                            <el-switch v-model="settingsForm.emailNotifications" />
                          </div>
                          <el-divider class="!my-2" />
                          <div class="flex items-center justify-between">
                            <div>
                              <p class="font-medium text-gray-900">
                                Push уведомления
                              </p>
                              <p class="text-xs text-gray-500">
                                Уведомления в браузере
                              </p>
                            </div>
                            <el-switch v-model="settingsForm.pushNotifications" />
                          </div>
                        </div>
                      </div>
                  
                      <!-- Интерфейс -->
                      <div>
                        <div class="flex items-center gap-3 mb-6">
                          <div class="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                            <el-icon size="20">
                              <Monitor />
                            </el-icon>
                          </div>
                          <div>
                            <h3 class="font-bold text-gray-900">
                              Интерфейс
                            </h3>
                            <p class="text-sm text-gray-500">
                              Настройки отображения
                            </p>
                          </div>
                        </div>
                        
                        <div class="bg-gray-50 rounded-xl p-4 border border-gray-100">
                          <div class="flex items-center justify-between">
                            <div>
                              <p class="font-medium text-gray-900">
                                Язык системы
                              </p>
                              <p class="text-xs text-gray-500">
                                Выберите предпочтительный язык
                              </p>
                            </div>
                            <el-select
                              v-model="settingsForm.language"
                              size="large"
                              class="w-40"
                            >
                              <el-option
                                label="Русский"
                                value="ru"
                              >
                                <span class="flex items-center gap-2">🇷🇺 Русский</span>
                              </el-option>
                              <el-option
                                label="English"
                                value="en"
                              >
                                <span class="flex items-center gap-2">🇺🇸 English</span>
                              </el-option>
                            </el-select>
                          </div>
                        </div>
                      </div>
                  
                      <div class="pt-4">
                        <el-button
                          type="primary"
                          size="large"
                          class="w-full sm:w-auto px-8"
                          @click="saveSettings"
                        >
                          Сохранить настройки
                        </el-button>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <el-dialog 
      v-model="showEditProfile" 
      title="Редактирование профиля" 
      width="90%" 
      class="max-w-lg rounded-2xl"
      align-center
      destroy-on-close
    >
      <el-form
        :model="editForm"
        label-position="top"
        size="large"
        class="mt-2"
      >
        <el-form-item label="ФИО Сотрудника">
          <el-input
            v-model="editForm.name"
            placeholder="Введите ваше полное имя"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="Корпоративный Email">
          <el-input
            v-model="editForm.email"
            disabled
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
            <template #append>
              <el-tooltip
                content="Email нельзя изменить самостоятельно. Обратитесь к администратору."
                placement="top"
              >
                <el-icon><Lock /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <el-form-item label="Станция (необязательно)">
            <el-select 
              v-model="editForm.station" 
              placeholder="Выберите станцию (необязательно)" 
              class="w-full"
              :loading="loadingStations"
              filterable
              clearable
            >
              <el-option
                v-for="station in stations"
                :key="station.id"
                :label="station.name"
                :value="station.name"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Должность">
            <el-input
              v-model="editForm.position"
              placeholder="Например, Инженер"
              :prefix-icon="Suitcase"
            />
          </el-form-item>
        </div>
      </el-form>
      
      <template #footer>
        <div class="flex justify-end gap-3 pt-2">
          <el-button @click="showEditProfile = false">
            Отмена
          </el-button>
          <el-button
            type="primary"
            :loading="saving"
            @click="saveProfile"
          >
            Сохранить изменения
          </el-button>
        </div>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import UserStatistics from '@/components/user/UserStatistics.vue'
import { ElMessage } from 'element-plus'
import authService from '@/services/auth'
import userProfileService from '@/services/userProfile'
import stationService from '@/services/stationService'
import { 
  Edit, Camera, Message, OfficeBuilding, Suitcase, ArrowRight, Lock,
  Monitor, Bell, Clock, Collection, Loading, User
} from '@element-plus/icons-vue'

export default {
  name: 'Profile',
  components: {
    AppLayout,
    UserStatistics,
    Edit, Camera, Message, OfficeBuilding, Suitcase, ArrowRight, Lock,
    Monitor, Bell, Clock, Collection, Loading, User
  },
  setup() {
    const activeTab = ref('courses')
    const showEditProfile = ref(false)
    const uploading = ref(false)
    const saving = ref(false)
    const loading = ref(true)
    const loadingStations = ref(false)
    const stations = ref([])
    const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
    let resizeHandler = null
    
    const currentUser = authService.getCurrentUser()

    const isMobile = computed(() => viewportWidth.value < 640)
    const avatarSize = computed(() => {
      if (viewportWidth.value < 640) return 96
      if (viewportWidth.value < 1024) return 112
      return 128
    })
    
    const user = ref({
      id: currentUser?.id,
      name: '',
      email: '',
      avatar: '',
      station: '',
      position: '',
      department: '' // Отдел из LDAP (хранится в bio)
    })
    
    const userStats = ref({
      completedCourses: 0,
      hoursStudied: 0
    })
    
    const userCourses = ref([])
    
    const settingsForm = reactive({
      emailNotifications: true,
      pushNotifications: false,
      language: 'ru'
    })
    
    const editForm = reactive({
      name: '',
      email: '',
      station: '',
      position: ''
    })
    
    const customColors = [
      { color: '#f56c6c', percentage: 20 },
      { color: '#e6a23c', percentage: 40 },
      { color: '#5cb87a', percentage: 80 },
      { color: '#1989fa', percentage: 100 },
    ]

    const openEditModal = () => {
      editForm.name = user.value.name
      editForm.email = user.value.email
      editForm.station = user.value.station
      editForm.position = user.value.position
      showEditProfile.value = true
    }

    // Обновление глобального состояния пользователя (для Header/LessonHeader)
    const updateGlobalUserState = (updates) => {
      const current = authService.getCurrentUser()
      if (current) {
        const updatedUser = { ...current, ...updates }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        authService.currentUser = { ...updatedUser }
        authService.refreshUser()
        
        // Обновляем локальный ref, если он не был обновлен
        user.value = { ...user.value, ...updates }
      }
    }
    
    const handleAvatarChange = async (file) => {
      if (!currentUser?.id) return

      uploading.value = true
      try {
        const result = await userProfileService.uploadAvatar(currentUser.id, file.raw)
        
        if (result.success) {
          const newAvatarUrl = result.url
          const avatarKey = result.key // MinIO key
          ElMessage.success('Фото профиля обновлено')
          
          // Обновляем кеш аватарки сразу после загрузки
          if (avatarKey) {
            localStorage.setItem('avatar_key', avatarKey)
            localStorage.setItem('avatar_url_cached', newAvatarUrl)
            // Кеш действителен 6 дней (из 7 дней presigned URL)
            localStorage.setItem('avatar_url_expires', String(Date.now() + (6 * 24 * 60 * 60 * 1000)))
            console.log('[Profile] Avatar cache updated, key:', avatarKey)
          }
          
          // Обновляем везде
          user.value.avatar = newAvatarUrl
          updateGlobalUserState({ avatar_url: newAvatarUrl, avatar: newAvatarUrl })
          
          // Отправляем событие для обновления Header
          await nextTick()
          window.dispatchEvent(new CustomEvent('user-profile-updated'))
        } else {
          ElMessage.error(result.error || 'Ошибка загрузки')
        }
      } catch (error) {
        console.error('Upload error:', error)
        ElMessage.error('Не удалось загрузить фото')
      } finally {
        uploading.value = false
      }
    }
    
    const saveProfile = async () => {
      if (!currentUser?.id) return
      
      saving.value = true
      try {
        // Защита от undefined при trim()
        const fullName = editForm.name ? String(editForm.name).trim() : ''
        const position = editForm.position ? String(editForm.position).trim() : null
        const station = editForm.station || null

        if (!fullName) {
          ElMessage.warning('Пожалуйста, укажите ФИО')
          saving.value = false
          return
        }

        const profileData = {
          full_name: fullName,
          company: station, // Используем company для Django API (маппинг station -> company)
          position: position
        }

        const result = await userProfileService.saveProfile(currentUser.id, profileData)
        
        if (result.success) {
          ElMessage.success('Профиль успешно обновлен')
          
          // Обновляем локальный стейт
          user.value = {
            ...user.value,
            name: fullName,
            station: station, // Используем выбранное значение станции
            position: position
          }
          
          // Обновляем глобальное состояние (сохраняем station для совместимости)
          updateGlobalUserState({
            full_name: fullName,
            station: station, // Используем выбранное значение станции
            company: station, // Также сохраняем как company для БД
            position: position
          })
          
          await nextTick()
          window.dispatchEvent(new CustomEvent('user-profile-updated'))
          
          showEditProfile.value = false
        } else {
          ElMessage.error(result.error || 'Ошибка сохранения профиля')
        }
      } catch (error) {
        console.error('Save error:', error)
        ElMessage.error(error.message || 'Ошибка сохранения профиля')
      } finally {
        saving.value = false
      }
    }

    const saveSettings = () => {
      // В будущем здесь можно сохранить настройки в БД
      ElMessage.success('Настройки сохранены')
    }
    
    const loadUserData = async () => {
      loading.value = true
      
      if (!currentUser?.id) {
        // Fallback для демо режима (без авторизации)
        user.value = {
          name: 'Демо Пользователь',
          email: 'demo@tamex.uz',
          avatar: '',
          station: 'WKC1',
          position: 'Гость',
          department: null
        }
        loading.value = false
        return
      }
      
      try {
        // 1. Загружаем профиль
        const profilePromise = userProfileService.getProfile(currentUser.id)
        
        // 2. Загружаем статистику
        const statsPromise = userProfileService.getUserStats(currentUser.id)
        
        // 3. Загружаем курсы
        const coursesPromise = userProfileService.getUserCourses(currentUser.id)
        
        // Ждем все запросы
        const [profileResult, statsResult, coursesResult] = await Promise.all([
          profilePromise,
          statsPromise,
          coursesPromise
        ])
        
        // Обрабатываем профиль
        if (profileResult.success && profileResult.data) {
          const data = profileResult.data
          user.value = {
            id: data.id,
            name: data.full_name || data.name || currentUser.username || 'Пользователь',
            email: data.email || currentUser.email || '',
            avatar: data.avatar_url || data.avatar || null,
            station: data.station || data.company || null, // Маппинг company -> station
            position: data.position || null,
            department: data.bio || null // Отдел из LDAP (хранится в bio)
          }
          
          // Синхронизируем с глобальным стейтом
          updateGlobalUserState({
            full_name: data.full_name || data.name,
            station: data.station || data.company, // Маппинг company -> station
            position: data.position,
            avatar_url: data.avatar_url || data.avatar,
            email: data.email
          })
        } else {
            // Если профиль не найден, используем данные из auth
            user.value = {
              id: currentUser.id,
              name: currentUser.full_name || currentUser.username,
              email: currentUser.email,
              avatar: currentUser.avatar_url || currentUser.avatar,
              station: currentUser.station || currentUser.company,
              position: currentUser.position,
              department: currentUser.bio || null // Отдел из LDAP (хранится в bio)
            }
        }
        
        // Обрабатываем статистику
        if (statsResult.success && statsResult.data) {
          userStats.value = {
            completedCourses: statsResult.data.completed_courses || 0,
            hoursStudied: Math.round(statsResult.data.total_hours_studied || 0)
          }
        }
        
        // Обрабатываем курсы
        if (coursesResult.success && coursesResult.data) {
          userCourses.value = coursesResult.data
        }
        
      } catch (error) {
        console.error('Error loading profile data:', error)
        ElMessage.error('Ошибка загрузки данных профиля')
      } finally {
        loading.value = false
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'Недавно'
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }).format(date)
    }
    
    const getStatusLabel = (status) => {
      const map = {
        'in_progress': 'В процессе',
        'completed': 'Завершен',
        'not_started': 'Не начат'
      }
      return map[status] || status
    }
    
    const getStatusClass = (status) => {
      const map = {
        'in_progress': 'bg-blue-100 text-blue-700',
        'completed': 'bg-green-100 text-green-700',
        'not_started': 'bg-gray-100 text-gray-700'
      }
      return map[status] || 'bg-gray-100 text-gray-700'
    }

    // Загрузка списка станций
    const loadStations = async () => {
      loadingStations.value = true
      try {
        const data = await stationService.getStations()
        stations.value = data || []
      } catch (error) {
        console.error('Error loading stations:', error)
        ElMessage.error({
          message: 'Не удалось загрузить список станций',
          duration: 3000
        })
      } finally {
        loadingStations.value = false
      }
    }
    
    onMounted(() => {
      loadUserData()
      loadStations()
      resizeHandler = () => {
        viewportWidth.value = window.innerWidth
      }
      window.addEventListener('resize', resizeHandler, { passive: true })
    })

    onBeforeUnmount(() => {
      if (resizeHandler) window.removeEventListener('resize', resizeHandler)
    })
    
    return {
      activeTab,
      showEditProfile,
      uploading,
      saving,
      loading,
      loadingStations,
      stations,
      user,
      userStats,
      userCourses,
      settingsForm,
      editForm,
      customColors,
      isMobile,
      avatarSize,
      Edit, Camera, Message, OfficeBuilding, Suitcase, ArrowRight, Lock, Monitor, Bell, User,
      openEditModal,
      handleAvatarChange,
      saveProfile,
      saveSettings,
      formatDate,
      getStatusLabel,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.card {
  transition: all 0.3s ease;
}

.pattern-dots {
  background-image: radial-gradient(rgba(255, 255, 255, 0.2) 1px, transparent 1px);
  background-size: 20px 20px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #f3f4f6;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  height: 50px;
  line-height: 50px;
  color: #6b7280;
}

:deep(.el-tabs__item.is-active) {
  color: #2563eb;
  font-weight: 600;
}

:deep(.el-tabs__active-bar) {
  background-color: #2563eb;
  height: 3px;
  border-radius: 3px;
}

:deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 10px;
}

@media (max-width: 640px) {
  .profile-tabs :deep(.el-tabs__nav) {
    width: 100%;
    display: flex;
  }
  
  .profile-tabs :deep(.el-tabs__item) {
    flex: 1;
    text-align: center;
    padding: 0 10px;
    font-size: 14px;
  }
}
</style>