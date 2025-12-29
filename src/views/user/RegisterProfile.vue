<template>
  <div class="min-h-screen flex relative overflow-hidden">
    <!-- Кнопка "Назад" -->
    <button 
      class="back-button absolute top-6 left-6 z-50 inline-flex items-center bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-all duration-300 group px-4 py-2 rounded-lg border border-white/30 hover:border-white/50 shadow-lg hover:shadow-xl"
      @click="handleCancel"
    >
      <svg
        class="w-5 h-5 mr-2 transition-transform group-hover:-translate-x-1"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 19l-7-7 7-7"
        />
      </svg>
      <span class="text-sm font-semibold">Назад</span>
    </button>

    <!-- Левая часть - синий фон с 3D моделью турбины -->
    <div class="hidden lg:flex lg:w-1/2 xl:w-[55%] bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 relative overflow-hidden">
      <!-- Декоративная диагональная граница -->
      <div class="absolute right-0 top-0 bottom-0 w-40 bg-white/5 transform skew-x-[-12deg] translate-x-20" />
      
      <!-- 3D модель турбины -->
      <div class="flex items-center justify-center w-full relative z-10 px-8 py-12">
        <div class="w-full max-w-3xl relative">
          <img 
            src="/login/turbine.png" 
            alt="Gas Turbine Engine" 
            class="w-full h-auto object-contain drop-shadow-2xl transform hover:scale-105 transition-all duration-700 ease-out"
          >
        </div>
      </div>
      
      <!-- Декоративные элементы -->
      <div class="absolute top-10 left-10 w-24 h-24 bg-white/10 rounded-full blur-xl" />
      <div class="absolute bottom-20 left-1/4 w-40 h-40 bg-white/5 rounded-full blur-2xl" />
      <div class="absolute top-1/3 right-24 w-20 h-20 bg-white/10 rounded-full blur-lg" />
      <div class="absolute bottom-1/4 right-1/3 w-32 h-32 bg-white/5 rounded-full blur-xl" />
    </div>

    <!-- Правая часть - форма регистрации -->
    <div class="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center bg-white px-6 sm:px-12 lg:px-16 xl:px-20 relative">
      <!-- Декоративный градиент фон -->
      <div class="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50/30" />
      
      <div class="w-full max-w-md relative z-10">
        <!-- Логотип и заголовок -->
        <div class="text-center mb-12 space-y-6">
          <div class="flex justify-center mb-8 animate-fade-in">
            <div class="relative">
              <img 
                src="/login/logo 1.svg" 
                alt="ATG Logo" 
                class="h-20 w-auto sm:h-24 drop-shadow-lg"
              >
            </div>
          </div>
          <div class="space-y-2 animate-slide-up">
            <h1 class="text-3xl sm:text-4xl lg:text-[2.75rem] font-bold text-gray-900 tracking-tight leading-tight">
              Завершение регистрации
            </h1>
            <p class="text-gray-500 text-sm sm:text-base">
              Пожалуйста, заполните ваши данные для завершения регистрации
            </p>
          </div>
        </div>

        <!-- Форма регистрации -->
        <div class="space-y-6 animate-fade-in-delay">
          <el-form 
            ref="registerForm" 
            :model="form" 
            :rules="rules" 
            class="space-y-5"
            @submit.prevent="handleSubmit"
          >
            <!-- ФИО -->
            <el-form-item
              prop="full_name"
              class="mb-5"
            >
              <el-input
                v-model="form.full_name"
                placeholder="ФИО"
                size="large"
                class="login-input"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <el-icon class="input-icon">
                    <User />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Номер телефона -->
            <el-form-item
              prop="phone"
              class="mb-5"
            >
              <el-input
                v-model="form.phone"
                placeholder="Номер телефона"
                size="large"
                class="login-input"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <el-icon class="input-icon">
                    <Phone />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Название станции -->
            <el-form-item
              prop="station_id"
              class="mb-5"
            >
              <el-select
                v-model="form.station_id"
                placeholder="Выберите станцию (необязательно)"
                size="large"
                class="login-input w-full"
                :loading="loadingStations"
                filterable
                clearable
              >
                <el-option
                  v-for="station in stations"
                  :key="station.id"
                  :label="station.name"
                  :value="station.id"
                />
              </el-select>
            </el-form-item>

            <!-- Должность -->
            <el-form-item
              prop="position"
              class="mb-5"
            >
              <el-input
                v-model="form.position"
                placeholder="Должность"
                size="large"
                class="login-input"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <el-icon class="input-icon">
                    <Briefcase />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Департамент -->
            <el-form-item
              prop="department"
              class="mb-6"
            >
              <el-input
                v-model="form.department"
                placeholder="Департамент"
                size="large"
                class="login-input"
                @keyup.enter="handleSubmit"
              >
                <template #prefix>
                  <el-icon class="input-icon">
                    <OfficeBuilding />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Submit Button -->
            <el-button 
              type="primary" 
              size="large" 
              class="w-full login-button"
              :loading="loading"
              @click="handleSubmit"
            >
              <span class="flex items-center justify-center gap-2">
                <span>Сохранить и продолжить</span>
                <svg
                  v-if="!loading"
                  class="w-4 h-4 transition-transform group-hover:translate-x-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </span>
            </el-button>
          </el-form>
        </div>

        <!-- Footer -->
        <div class="mt-12 text-center text-xs text-gray-400">
          <p>Поля ФИО, телефон и должность обязательны для заполнения</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { User, Phone, OfficeBuilding, Briefcase } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import authService from '@/services/auth'
import stationService from '@/services/stationService'

export default {
  name: 'RegisterProfile',
  setup() {
    const router = useRouter()
    const registerForm = ref(null)
    const loading = ref(false)
    const loadingStations = ref(false)
    const stations = ref([])
    
    const form = reactive({
      full_name: '',
      phone: '',
      station_id: null,
      position: '',
      department: ''
    })
    
    const rules = {
      full_name: [
        { required: true, message: 'ФИО обязательно для заполнения', trigger: 'blur' },
        { min: 2, message: 'ФИО должно содержать минимум 2 символа', trigger: 'blur' }
      ],
      phone: [
        { required: true, message: 'Номер телефона обязателен для заполнения', trigger: 'blur' },
        { min: 5, message: 'Номер телефона должен содержать минимум 5 символов', trigger: 'blur' }
      ],
      station_id: [
        // Станция необязательна
      ],
      position: [
        { required: true, message: 'Должность обязательна для заполнения', trigger: 'blur' },
        { min: 2, message: 'Должность должна содержать минимум 2 символа', trigger: 'blur' }
      ],
      department: [
        { required: true, message: 'Департамент обязателен для заполнения', trigger: 'blur' },
        { min: 2, message: 'Департамент должен содержать минимум 2 символа', trigger: 'blur' }
      ]
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
          duration: 5000,
          showClose: true
        })
      } finally {
        loadingStations.value = false
      }
    }
    
    // Загрузка данных профиля из БД
    const loadProfileData = async () => {
      try {
        // Always use /api proxy (works in both dev and prod)
        // In dev: Vite proxy handles /api -> http://localhost:8000
        // In prod: nginx proxy handles /api -> http://backend:8000
        const API_BASE_URL = '/api'
        
        // Получаем токен
        const token = authService.accessToken || localStorage.getItem('auth_token')
        if (!token) {
          console.warn('[RegisterProfile] No auth token found, skipping profile load')
          return
        }
        
        console.log('[RegisterProfile] Loading profile data from:', `${API_BASE_URL}/auth/register-profile`)
        
        const response = await fetch(`${API_BASE_URL}/auth/register-profile`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        })
        
        console.log('[RegisterProfile] Response status:', response.status, response.statusText)
        
        if (response.ok) {
          const result = await response.json()
          console.log('[RegisterProfile] Profile data received:', result)
          
          if (result.data) {
            // Заполняем форму данными из БД (реактивно)
            if (result.data.full_name) {
              form.full_name = result.data.full_name
              console.log('[RegisterProfile] Set full_name:', result.data.full_name)
            }
            if (result.data.phone) {
              form.phone = result.data.phone
              console.log('[RegisterProfile] Set phone:', result.data.phone)
            }
            if (result.data.station_id) {
              // Убеждаемся, что станции уже загружены
              if (stations.value.length > 0) {
                form.station_id = result.data.station_id
                console.log('[RegisterProfile] Set station_id:', result.data.station_id)
              } else {
                // Если станции еще не загружены, сохраняем ID и установим позже
                console.log('[RegisterProfile] Stations not loaded yet, will set station_id after load')
                setTimeout(() => {
                  form.station_id = result.data.station_id
                  console.log('[RegisterProfile] Set station_id (delayed):', result.data.station_id)
                }, 500)
              }
            }
            if (result.data.position) {
              form.position = result.data.position
              console.log('[RegisterProfile] Set position:', result.data.position)
            }
            if (result.data.department) {
              form.department = result.data.department
              console.log('[RegisterProfile] Set department:', result.data.department)
            }
            
            console.log('[RegisterProfile] Form data after load:', {
              full_name: form.full_name,
              phone: form.phone,
              station_id: form.station_id,
              position: form.position,
              department: form.department
            })
            
            // Принудительно обновляем форму Element Plus
            await nextTick()
            if (registerForm.value) {
              registerForm.value.clearValidate()
              console.log('[RegisterProfile] Form cleared and validated')
            }
          } else {
            console.log('[RegisterProfile] No data in response')
          }
        } else {
          const errorText = await response.text()
          console.warn('[RegisterProfile] Failed to load profile:', response.status, errorText)
          // Не показываем ошибку, так как это нормально, если профиля еще нет
        }
      } catch (error) {
        console.error('[RegisterProfile] Error loading profile data:', error)
        // Не показываем ошибку, так как это нормально, если профиля еще нет
      }
    }
    
    const handleSubmit = async () => {
      if (!registerForm.value) return
      
      try {
        await registerForm.value.validate()
        loading.value = true
        
        // Always use /api proxy (works in both dev and prod)
        // In dev: Vite proxy handles /api -> http://localhost:8000
        // In prod: nginx proxy handles /api -> http://backend:8000
        const API_BASE_URL = '/api'
        
        const response = await fetch(`${API_BASE_URL}/auth/register-profile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authService.accessToken || localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({
            full_name: form.full_name.trim(),
            phone: form.phone.trim(),
            station_id: form.station_id,
            position: form.position.trim(),
            department: form.department.trim()
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || errorData.detail || 'Ошибка при сохранении профиля')
        }
        
        const data = await response.json()

        // If backend returns fresh tokens (temp LDAP -> real user), update local auth state
        if (data && data.token && data.refreshToken && data.user) {
          authService.accessToken = data.token
          authService.refreshToken = data.refreshToken
          authService.sessionToken = data.refreshToken
          authService.currentUser = data.user
          localStorage.setItem('auth_token', data.token)
          localStorage.setItem('refresh_token', data.refreshToken)
          localStorage.setItem('user', JSON.stringify(data.user))
        }
        
        ElMessage.success({
          message: 'Профиль успешно сохранен!',
          duration: 3000,
          showClose: true
        })
        
        // Перенаправляем в зависимости от роли пользователя
        const user = authService.getCurrentUser()
        if (user && user.role === 'instructor') {
          router.push('/dashboard')
        } else {
          // Админы и обычные пользователи попадают в личный кабинет
          router.push('/profile')
        }
        
      } catch (error) {
        console.error('Registration error:', error)
        ElMessage.error({
          message: error.message || 'Ошибка при сохранении профиля',
          duration: 5000,
          showClose: true
        })
      } finally {
        loading.value = false
      }
    }
    
    const handleCancel = () => {
      // При отмене выходим из системы
      authService.logout()
      router.push('/login')
    }
    
    // Загружаем станции и данные профиля при монтировании компонента
    onMounted(async () => {
      console.log('[RegisterProfile] Component mounted, loading data...')
      // Сначала загружаем станции, потом профиль (чтобы station_id мог найтись)
      await loadStations()
      console.log('[RegisterProfile] Stations loaded:', stations.value.length)
      // Небольшая задержка, чтобы убедиться, что станции отрендерились
      await new Promise(resolve => setTimeout(resolve, 100))
      await loadProfileData()
      console.log('[RegisterProfile] Profile data loaded')
    })
    
    return {
      registerForm,
      form,
      rules,
      loading,
      loadingStations,
      stations,
      handleSubmit,
      handleCancel,
      User,
      Phone,
      OfficeBuilding,
      Briefcase
    }
  }
}
</script>

<style scoped>
/* Анимации */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out 0.2s backwards;
}

.animate-fade-in-delay {
  animation: fadeIn 0.8s ease-out 0.4s backwards;
}

/* Стили для инпутов и селектов */
:deep(.login-input .el-input__wrapper),
:deep(.login-input .el-select__wrapper) {
  background-color: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 14px;
  padding: 14px 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 56px;
}

:deep(.login-input .el-input__wrapper:hover),
:deep(.login-input .el-select__wrapper:hover) {
  background-color: #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

:deep(.login-input .el-input__wrapper.is-focus),
:deep(.login-input .el-select__wrapper.is-focus) {
  background-color: #ffffff;
  border-color: #60a5fa;
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.1), 0 4px 16px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

:deep(.login-input .el-input__inner) {
  color: #1f2937;
  font-size: 15px;
  font-weight: 500;
}

:deep(.login-input .el-input__inner::placeholder) {
  color: #9ca3af;
  font-weight: 400;
}

:deep(.login-input .input-icon) {
  color: #6b7280;
  font-size: 18px;
  transition: color 0.3s ease;
}

:deep(.login-input .el-input__wrapper.is-focus .input-icon) {
  color: #3b82f6;
}

/* Стили для кнопки */
:deep(.login-button) {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
  border: none;
  border-radius: 14px;
  padding: 16px 0;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.25), 0 4px 8px rgba(59, 130, 246, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 56px;
  position: relative;
  overflow: hidden;
}

:deep(.login-button::before) {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

:deep(.login-button:hover::before) {
  left: 100%;
}

:deep(.login-button:hover) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 12px 24px rgba(59, 130, 246, 0.35), 0 6px 12px rgba(59, 130, 246, 0.2);
  transform: translateY(-2px) scale(1.01);
}

:deep(.login-button:active) {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

:deep(.login-button.is-loading) {
  background: linear-gradient(135deg, #93c5fd 0%, #60a5fa 100%);
}

/* Убираем отступы у form-item */
:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-form-item__error) {
  padding-top: 6px;
  font-size: 13px;
  font-weight: 500;
}

/* Адаптивность для мобильных */
@media (max-width: 640px) {
  :deep(.login-input .el-input__wrapper) {
    height: 52px;
    padding: 12px 16px;
    border-radius: 12px;
  }
  
  :deep(.login-button) {
    height: 52px;
    padding: 14px 0;
    border-radius: 12px;
    font-size: 15px;
  }
}

/* Адаптивные стили для кнопки "Назад" */
@media (max-width: 1024px) {
  .back-button {
    background-color: rgba(59, 130, 246, 0.1) !important;
    color: #3b82f6 !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
  }
  
  .back-button:hover {
    background-color: rgba(59, 130, 246, 0.2) !important;
    border-color: rgba(59, 130, 246, 0.5) !important;
  }
}
</style>

