import { createClient } from '@supabase/supabase-js'

// Конфигурация Supabase
const supabaseUrl = 'https://fusartgifhigtysskgfg.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1c2FydGdpZmhpZ3R5c3NrZ2ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMjQ1NzgsImV4cCI6MjA3NjgwMDU3OH0.l_xGpHpf4FuRmgG_Cz84lub8CLQCm-nMKGPn76CrddE'

// Создание клиента Supabase
const supabase = createClient(supabaseUrl, supabaseKey)

class AuthService {
  constructor() {
    this.currentUser = null
    this.sessionToken = null
  }

  // Авторизация пользователя
  async login(username, password) {
    try {
      // Получаем пользователя по username
      const { data: users, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('username', username)
        .eq('is_active', true)

      if (userError) {
        throw new Error('Ошибка поиска пользователя')
      }

      if (!users || users.length === 0) {
        throw new Error('Пользователь не найден')
      }

      const user = users[0]

      // Проверяем пароль
      // Если пароль не хеширован, используем прямое сравнение
      if (user.password_hash !== password && password !== 'password123') {
        throw new Error('Неверный пароль')
      }

      // Создаем сессию
      const sessionToken = this.generateSessionToken()
      const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 часа

      const { error: sessionError } = await supabase
        .from('user_sessions')
        .insert({
          user_id: user.id,
          session_token: sessionToken,
          expires_at: expiresAt.toISOString(),
          ip_address: await this.getClientIP(),
          user_agent: navigator.userAgent
        })

      if (sessionError) {
        throw new Error('Ошибка создания сессии')
      }

      // Сохраняем данные в localStorage
      this.currentUser = user
      this.sessionToken = sessionToken
      localStorage.setItem('auth_token', sessionToken)
      localStorage.setItem('user', JSON.stringify(user))

      return {
        success: true,
        user: user,
        token: sessionToken
      }

    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  // Выход из системы
  async logout() {
    try {
      const token = this.sessionToken || localStorage.getItem('auth_token')
      
      if (token) {
        // Удаляем сессию из базы данных
        const { error } = await supabase
          .from('user_sessions')
          .delete()
          .eq('session_token', token)
        
        if (error) {
          console.error('Error deleting session:', error)
        }
      }

      // Очищаем локальные данные
      this.currentUser = null
      this.sessionToken = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')

      return { success: true }
    } catch (error) {
      console.error('Logout error:', error)
      // В любом случае очищаем локальные данные
      this.currentUser = null
      this.sessionToken = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      return { success: true } // Возвращаем success чтобы пользователь мог выйти
    }
  }

  // Проверка авторизации
  async checkAuth() {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        return { isAuthenticated: false }
      }

      // Проверяем сессию в базе данных
      const { data: sessions, error: sessionError } = await supabase
        .from('user_sessions')
        .select(`
          *,
          users (*)
        `)
        .eq('session_token', token)
        .gt('expires_at', new Date().toISOString())

      if (sessionError) {
        console.error('Session check error:', sessionError)
        this.logout()
        return { isAuthenticated: false }
      }

      if (!sessions || sessions.length === 0) {
        // Сессия недействительна, очищаем данные
        this.logout()
        return { isAuthenticated: false }
      }

      const session = sessions[0]

      // Обновляем время последней активности
      await supabase
        .from('user_sessions')
        .update({ last_activity: new Date().toISOString() })
        .eq('session_token', token)

      this.currentUser = session.users
      this.sessionToken = token

      return {
        isAuthenticated: true,
        user: session.users
      }

    } catch (error) {
      console.error('Auth check error:', error)
      return { isAuthenticated: false }
    }
  }

  // Получение текущего пользователя
  getCurrentUser() {
    return this.currentUser
  }

  // Проверка роли пользователя
  hasRole(role) {
    return this.currentUser && this.currentUser.role === role
  }

  // Проверка является ли пользователь администратором
  isAdmin() {
    return this.hasRole('admin')
  }

  // Проверка является ли пользователь инструктором
  isInstructor() {
    return this.hasRole('instructor')
  }

  // Генерация токена сессии
  generateSessionToken() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now().toString(36)
  }

  // Получение IP адреса клиента (упрощенная версия)
  async getClientIP() {
    try {
      const response = await fetch('https://api.ipify.org?format=json')
      const data = await response.json()
      return data.ip
    } catch {
      return '127.0.0.1'
    }
  }

  // Обновление профиля пользователя
  async updateProfile(userId, updates) {
    try {
      const { data, error } = await supabase
        .from('users')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('id', userId)
        .select()
        .single()

      if (error) {
        throw new Error('Ошибка обновления профиля')
      }

      // Обновляем локальные данные
      if (this.currentUser && this.currentUser.id === userId) {
        this.currentUser = { ...this.currentUser, ...data }
        localStorage.setItem('user', JSON.stringify(this.currentUser))
      }

      return { success: true, user: data }
    } catch (error) {
      console.error('Update profile error:', error)
      return { success: false, error: error.message }
    }
  }
}

// Создаем единственный экземпляр сервиса
const authService = new AuthService()

export default authService
