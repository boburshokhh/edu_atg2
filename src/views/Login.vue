<template>
  <div class="min-h-screen flex relative overflow-hidden">
    <!-- Кнопка "Назад" -->
    <button 
      @click="$router.go(-1)"
      class="back-button absolute top-6 left-6 z-50 inline-flex items-center bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-all duration-300 group px-4 py-2 rounded-lg border border-white/30 hover:border-white/50 shadow-lg hover:shadow-xl"
    >
      <svg class="w-5 h-5 mr-2 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      <span class="text-sm font-semibold">{{ $t('nav.back') }}</span>
    </button>

    <!-- Левая часть - синий фон с 3D моделью турбины -->
    <div class="hidden lg:flex lg:w-1/2 xl:w-[55%] bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 relative overflow-hidden">
      <!-- Декоративная диагональная граница -->
      <div class="absolute right-0 top-0 bottom-0 w-40 bg-white/5 transform skew-x-[-12deg] translate-x-20"></div>
      
      <!-- 3D модель турбины -->
      <div class="flex items-center justify-center w-full relative z-10 px-8 py-12">
        <div class="w-full max-w-3xl relative">
          <img 
            src="/login/turbine.png" 
            alt="Gas Turbine Engine" 
            class="w-full h-auto object-contain drop-shadow-2xl transform hover:scale-105 transition-all duration-700 ease-out"
          />
        </div>
      </div>
      
      <!-- Декоративные элементы -->
      <div class="absolute top-10 left-10 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
      <div class="absolute bottom-20 left-1/4 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
      <div class="absolute top-1/3 right-24 w-20 h-20 bg-white/10 rounded-full blur-lg"></div>
      <div class="absolute bottom-1/4 right-1/3 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
    </div>

    <!-- Правая часть - форма входа -->
    <div class="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center bg-white px-6 sm:px-12 lg:px-16 xl:px-20 relative">
      <!-- Декоративный градиент фон -->
      <div class="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50/30"></div>
      
      <div class="w-full max-w-md relative z-10">
        <!-- Логотип и заголовок -->
        <div class="text-center mb-12 space-y-6">
          <div class="flex justify-center mb-8 animate-fade-in">
            <div class="relative">
              <img 
                src="/login/logo 1.svg" 
                alt="ATG Logo" 
                class="h-20 w-auto sm:h-24 drop-shadow-lg"
              />
            </div>
          </div>
          <div class="space-y-2 animate-slide-up">
            <h1 class="text-3xl sm:text-4xl lg:text-[2.75rem] font-bold text-gray-900 tracking-tight leading-tight">
              {{ $t('login.title') }}
            </h1>
            <p class="text-gray-500 text-sm sm:text-base">
              {{ $t('login.subtitle') }}
            </p>
          </div>
        </div>

        <!-- Форма входа -->
        <div class="space-y-6 animate-fade-in-delay">
          <el-form 
            ref="loginForm" 
            :model="form" 
            :rules="rules" 
            @submit.prevent="handleLogin"
            class="space-y-5"
          >
            <!-- Username -->
            <el-form-item prop="username" class="mb-5">
              <el-input
                v-model="form.username"
                :placeholder="$t('login.username')"
                size="large"
                class="login-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Password -->
            <el-form-item prop="password" class="mb-6">
              <el-input
                v-model="form.password"
                type="password"
                :placeholder="$t('login.password')"
                size="large"
                show-password
                class="login-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- Login Button -->
            <el-button 
              type="primary" 
              size="large" 
              class="w-full login-button"
              :loading="loading"
              @click="handleLogin"
            >
              <span class="flex items-center justify-center gap-2">
                <span>{{ $t('login.loginButton') }}</span>
                <svg v-if="!loading" class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </el-button>
          </el-form>

          <!-- Разделитель -->
          <div class="relative my-8">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-500">{{ $t('login.divider') }}</span>
            </div>
          </div>

          <!-- Дополнительные ссылки -->
          <div class="text-center space-y-3">
            <div>
              <a href="#" class="text-gray-500 hover:text-gray-700 text-xs transition-colors">
                {{ $t('login.forgotPassword') }}
              </a>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="mt-12 text-center text-xs text-gray-400">
          <p>{{ $t('login.copyright') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import authService from '@/services/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const { t } = useI18n()
    const loginForm = ref(null)
    const loading = ref(false)
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const rules = computed(() => ({
      username: [
        { required: true, message: t('login.validation.usernameRequired'), trigger: 'blur' }
      ],
      password: [
        { required: true, message: t('login.validation.passwordRequired'), trigger: 'blur' },
        { min: 6, message: t('login.validation.passwordMinLength'), trigger: 'blur' }
      ]
    }))
    
    const handleLogin = async () => {
      if (!loginForm.value) return
      
      try {
        await loginForm.value.validate()
        loading.value = true
        
        // Авторизация через Supabase
        const result = await authService.login(form.username, form.password)
        
        if (result.success) {
          ElMessage.success(t('login.messages.loginSuccess'))
          
          // Перенаправляем в зависимости от роли пользователя
          if (result.user.role === 'admin') {
            router.push('/dashboard')
          } else if (result.user.role === 'instructor') {
            router.push('/dashboard')
          } else {
            router.push('/dashboard')
          }
        } else {
          ElMessage.error(result.error || t('login.messages.loginError'))
        }
        
      } catch (error) {
        console.error('Validation failed:', error)
        ElMessage.error(t('login.messages.validationError'))
      } finally {
        loading.value = false
      }
    }
    
    // Проверяем авторизацию при загрузке компонента
    onMounted(async () => {
      const authResult = await authService.checkAuth()
      if (authResult.isAuthenticated) {
        // Пользователь уже авторизован, перенаправляем
        router.push('/dashboard')
      }
    })
    
    return {
      loginForm,
      form,
      rules,
      loading,
      handleLogin,
      User,
      Lock
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

/* Стили для инпутов */
:deep(.login-input .el-input__wrapper) {
  background-color: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 14px;
  padding: 14px 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 56px;
}

:deep(.login-input .el-input__wrapper:hover) {
  background-color: #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

:deep(.login-input .el-input__wrapper.is-focus) {
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

/* Стили для кнопки входа */
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

/* Дополнительные улучшения */
:deep(.el-loading-mask) {
  border-radius: 14px;
}

/* Плавный переход для всех интерактивных элементов */
a, button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
