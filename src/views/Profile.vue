<template>
  <AppLayout>
    <div class="section-padding bg-gray-50 min-h-screen">
      <div class="page-container">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">Профиль</h1>
          <p class="text-gray-600">Управляйте информацией о вашем аккаунте</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Profile Info -->
          <div class="lg:col-span-1">
            <div class="card p-6">
              <div class="text-center">
                <el-avatar :size="120" :src="user.avatar" class="mb-4">
                  <el-icon :size="60"><User /></el-icon>
                </el-avatar>
                <h2 class="text-xl font-semibold text-gray-900 mb-2">{{ user.name }}</h2>
                <p class="text-gray-600 mb-4">{{ user.email }}</p>
                <el-button @click="showEditProfile = true" type="primary" plain>
                  Редактировать профиль
                </el-button>
              </div>

              <div class="mt-8 space-y-4">
                <div class="flex items-center gap-3">
                  <el-icon class="text-primary-600"><Calendar /></el-icon>
                  <span class="text-gray-600">Дата регистрации:</span>
                  <span class="font-medium">{{ user.joinDate }}</span>
                </div>
                <div class="flex items-center gap-3">
                  <el-icon class="text-primary-600"><Trophy /></el-icon>
                  <span class="text-gray-600">Курсов завершено:</span>
                  <span class="font-medium">{{ userStats.completedCourses }}</span>
                </div>
                <div class="flex items-center gap-3">
                  <el-icon class="text-primary-600"><Clock /></el-icon>
                  <span class="text-gray-600">Часов изучено:</span>
                  <span class="font-medium">{{ userStats.hoursStudied }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Content -->
          <div class="lg:col-span-2">
            <!-- Tabs -->
            <el-tabs v-model="activeTab" class="mb-8">
              <el-tab-pane label="Мои курсы" name="courses">
                <div class="space-y-6">
                  <div 
                    v-for="course in userCourses" 
                    :key="course.id"
                    class="card p-6"
                  >
                    <div class="flex items-center gap-4">
                      <div class="w-20 h-16 bg-gradient-to-br from-primary-100 to-orange-100 rounded-lg flex items-center justify-center">
                        <el-icon :size="32" class="text-primary-600">
                          <component :is="course.icon" />
                        </el-icon>
                      </div>
                      
                      <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ course.title }}</h3>
                        <p class="text-gray-600 mb-3">{{ course.description }}</p>
                        
                        <div class="flex items-center gap-6 mb-3">
                          <div class="flex items-center gap-2">
                            <el-icon class="text-gray-500"><Clock /></el-icon>
                            <span class="text-sm text-gray-600">{{ course.duration }}</span>
                          </div>
                          <div class="flex items-center gap-2">
                            <el-icon class="text-gray-500"><Calendar /></el-icon>
                            <span class="text-sm text-gray-600">Начат {{ course.startDate }}</span>
                          </div>
                          <div class="flex items-center gap-2">
                            <el-icon class="text-gray-500"><Trophy /></el-icon>
                            <span class="text-sm text-gray-600">{{ course.progress }}% завершено</span>
                          </div>
                        </div>
                        
                        <el-progress 
                          :percentage="course.progress" 
                          :show-text="false"
                          :stroke-width="8"
                        />
                      </div>
                      
                      <div class="text-right">
                        <el-button 
                          @click="$router.push(`/course/${course.id}`)"
                          type="primary"
                        >
                          {{ course.progress === 100 ? 'Повторить' : 'Продолжить' }}
                        </el-button>
                        <div v-if="course.certificate" class="mt-2">
                          <el-button size="small" type="success" plain>
                            <el-icon><Certificate /></el-icon>
                            Сертификат
                          </el-button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="Сертификаты" name="certificates">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div 
                    v-for="certificate in certificates" 
                    :key="certificate.id"
                    class="card p-6 text-center"
                  >
                    <div class="w-20 h-20 bg-gradient-to-br from-orange-100 to-orange-200 rounded-full flex items-center justify-center mx-auto mb-4">
                      <el-icon :size="40" class="text-orange-600"><Certificate /></el-icon>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ certificate.title }}</h3>
                    <p class="text-gray-600 mb-4">{{ certificate.course }}</p>
                    <p class="text-sm text-gray-500 mb-4">Выдан {{ certificate.date }}</p>
                    <el-button type="primary" plain>Скачать PDF</el-button>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="Настройки" name="settings">
                <div class="card p-6">
                  <h3 class="text-lg font-semibold text-gray-900 mb-6">Настройки аккаунта</h3>
                  
                  <el-form :model="settingsForm" label-width="150px" class="max-w-2xl">
                    <el-form-item label="Email уведомления">
                      <el-switch v-model="settingsForm.emailNotifications" />
                    </el-form-item>
                    
                    <el-form-item label="Push уведомления">
                      <el-switch v-model="settingsForm.pushNotifications" />
                    </el-form-item>
                    
                    <el-form-item label="Еженедельный отчет">
                      <el-switch v-model="settingsForm.weeklyReport" />
                    </el-form-item>
                    
                    <el-form-item label="Язык интерфейса">
                      <el-select v-model="settingsForm.language" class="w-48">
                        <el-option label="Русский" value="ru" />
                        <el-option label="English" value="en" />
                        <el-option label="Узбекский" value="uz" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button type="primary" @click="saveSettings">Сохранить настройки</el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Dialog -->
    <el-dialog v-model="showEditProfile" title="Редактировать профиль" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="Имя">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="editForm.email" type="email" />
        </el-form-item>
        <el-form-item label="О себе">
          <el-input v-model="editForm.bio" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditProfile = false">Отмена</el-button>
        <el-button type="primary" @click="saveProfile">Сохранить</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>

<script>
import { ref, reactive } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Profile',
  components: {
    AppLayout
  },
  setup() {
    const activeTab = ref('courses')
    const showEditProfile = ref(false)
    
    const user = ref({
      name: 'Иван Иванов',
      email: 'ivan@example.com',
      avatar: '',
      joinDate: '15 января 2024'
    })
    
    const userStats = ref({
      completedCourses: 5,
      hoursStudied: 120
    })
    
    const userCourses = ref([
      {
        id: 1,
        title: 'Основы программирования на Python',
        description: 'Изучите основы программирования с помощью языка Python',
        icon: 'Code',
        duration: '40 часов',
        startDate: '15 января 2024',
        progress: 100,
        certificate: true
      },
      {
        id: 2,
        title: 'Веб-дизайн с Figma',
        description: 'Создавайте красивые и функциональные интерфейсы',
        icon: 'Monitor',
        duration: '30 часов',
        startDate: '1 февраля 2024',
        progress: 65,
        certificate: false
      },
      {
        id: 3,
        title: 'SMM и контент-маркетинг',
        description: 'Эффективное продвижение в социальных сетях',
        icon: 'Share',
        duration: '25 часов',
        startDate: '10 марта 2024',
        progress: 30,
        certificate: false
      }
    ])
    
    const certificates = ref([
      {
        id: 1,
        title: 'Сертификат Python',
        course: 'Основы программирования на Python',
        date: '20 февраля 2024'
      },
      {
        id: 2,
        title: 'Сертификат веб-дизайна',
        course: 'Веб-дизайн с Figma',
        date: '15 марта 2024'
      }
    ])
    
    const settingsForm = reactive({
      emailNotifications: true,
      pushNotifications: false,
      weeklyReport: true,
      language: 'ru'
    })
    
    const editForm = reactive({
      name: user.value.name,
      email: user.value.email,
      bio: 'Люблю изучать новые технологии и делиться знаниями с другими.'
    })
    
    const saveSettings = () => {
      ElMessage.success('Настройки сохранены!')
    }
    
    const saveProfile = () => {
      user.value.name = editForm.name
      user.value.email = editForm.email
      showEditProfile.value = false
      ElMessage.success('Профиль обновлен!')
    }
    
    return {
      activeTab,
      showEditProfile,
      user,
      userStats,
      userCourses,
      certificates,
      settingsForm,
      editForm,
      saveSettings,
      saveProfile
    }
  }
}
</script>
