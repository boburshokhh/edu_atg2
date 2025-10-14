<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-orange-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="flex justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-primary-600 to-orange-600 rounded-xl flex items-center justify-center">
            <span class="text-white font-bold text-xl">ATG</span>
          </div>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Создать аккаунт</h2>
        <p class="mt-2 text-gray-600">
          Или
          <router-link to="/login" class="text-primary-600 hover:text-primary-500 font-medium">
            войдите в существующий
          </router-link>
        </p>
      </div>

      <!-- Form -->
      <div class="card p-8">
        <el-form 
          ref="registerForm" 
          :model="form" 
          :rules="rules" 
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="name">
            <el-input
              v-model="form.name"
              placeholder="Полное имя"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="Email"
              :prefix-icon="Message"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Пароль"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="Подтвердите пароль"
              :prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>

          <el-form-item prop="agreement">
            <el-checkbox v-model="form.agreement">
              Я согласен с
              <a href="#" class="text-primary-600 hover:text-primary-500">условиями использования</a>
              и
              <a href="#" class="text-primary-600 hover:text-primary-500">политикой конфиденциальности</a>
            </el-checkbox>
          </el-form-item>

          <el-button 
            type="primary" 
            size="large" 
            class="w-full mb-4"
            :loading="loading"
            @click="handleRegister"
          >
            Создать аккаунт
          </el-button>

          <div class="text-center">
            <span class="text-gray-500 text-sm">Или зарегистрируйтесь через</span>
          </div>

          <div class="flex gap-4 mt-4">
            <el-button size="large" class="flex-1">
              <el-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg></el-icon>
              Google
            </el-button>
            <el-button size="large" class="flex-1">
              <el-icon><svg viewBox="0 0 24 24"><path fill="currentColor" d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.746-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-11.988C24.007 5.367 18.641.001 12.017.001z"/></svg></el-icon>
              Facebook
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Message, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const registerForm = ref(null)
    const loading = ref(false)
    
    const form = reactive({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreement: false
    })
    
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== form.password) {
        callback(new Error('Пароли не совпадают'))
      } else {
        callback()
      }
    }
    
    const rules = {
      name: [
        { required: true, message: 'Пожалуйста, введите имя', trigger: 'blur' },
        { min: 2, message: 'Имя должно содержать минимум 2 символа', trigger: 'blur' }
      ],
      email: [
        { required: true, message: 'Пожалуйста, введите email', trigger: 'blur' },
        { type: 'email', message: 'Пожалуйста, введите корректный email', trigger: 'blur' }
      ],
      password: [
        { required: true, message: 'Пожалуйста, введите пароль', trigger: 'blur' },
        { min: 6, message: 'Пароль должен содержать минимум 6 символов', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: 'Пожалуйста, подтвердите пароль', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ],
      agreement: [
        { 
          validator: (rule, value, callback) => {
            if (!value) {
              callback(new Error('Необходимо согласиться с условиями'))
            } else {
              callback()
            }
          }, 
          trigger: 'change' 
        }
      ]
    }
    
    const handleRegister = async () => {
      if (!registerForm.value) return
      
      try {
        await registerForm.value.validate()
        loading.value = true
        
        // Имитация API запроса
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Сохраняем данные пользователя
        const userData = {
          id: 1,
          name: form.name,
          email: form.email,
          avatar: ''
        }
        
        localStorage.setItem('auth_token', 'mock_token_123')
        localStorage.setItem('user', JSON.stringify(userData))
        
        ElMessage.success('Аккаунт успешно создан!')
        router.push('/dashboard')
        
      } catch (error) {
        console.error('Validation failed:', error)
      } finally {
        loading.value = false
      }
    }
    
    return {
      registerForm,
      form,
      rules,
      loading,
      handleRegister,
      User,
      Message,
      Lock
    }
  }
}
</script>
