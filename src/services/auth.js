// Authentication service with LDAP support via Django API

// API base URL - always use /api proxy (works in both dev and prod)
// In dev mode: Vite proxy handles /api -> http://localhost:8000
// In prod: nginx proxy handles /api -> http://backend:8000 (or backend service name)
const API_BASE_URL = '/api'

// Default was 8s which is often too short for LDAP in real networks.
// Can be overridden via VITE_LOGIN_TIMEOUT_MS (milliseconds).
const LOGIN_TIMEOUT_MS = Number(import.meta.env.VITE_LOGIN_TIMEOUT_MS || 25000)

console.log('[Auth] Environment:', {
  MODE: import.meta.env.MODE,
  API_BASE_URL,
  LOGIN_TIMEOUT_MS,
})

class AuthService {
  constructor() {
    this.currentUser = null
    this.sessionToken = null
    this.accessToken = null
    this.refreshToken = null
  }

  // Авторизация пользователя через Django API (с поддержкой LDAP)
  async login(username, password) {
    try {
      const isLdapEnabled = import.meta.env.VITE_LDAP_ENABLED === 'true' || 
                            import.meta.env.VITE_LDAP_ENABLED === true
      
      if (isLdapEnabled) {
        console.log('[Auth] Attempting LDAP authentication for user:', username)
      }

      const loginUrl = `${API_BASE_URL}/auth/login`
      console.log('[Auth] Sending login request to:', loginUrl)
      console.log('[Auth] API_BASE_URL:', API_BASE_URL)

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), LOGIN_TIMEOUT_MS)

      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          password,
        }),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      
      console.log('[Auth] Response status:', response.status, response.statusText)

      if (!response.ok) {
        let errorMessage = 'Invalid credentials'
        
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorData.detail || errorData.message || 'Invalid credentials'
          
          // Логируем ошибку для отладки
          if (isLdapEnabled) {
            console.error('[Auth] LDAP authentication failed:', errorMessage)
          } else {
            console.error('[Auth] Database authentication failed:', errorMessage)
          }
        } catch (parseError) {
          // Если не удалось распарсить JSON, используем статус код
          if (response.status === 401) {
            errorMessage = isLdapEnabled 
              ? 'Неверное имя пользователя или пароль LDAP'
              : 'Неверное имя пользователя или пароль'
          } else if (response.status === 500) {
            errorMessage = isLdapEnabled
              ? 'Ошибка подключения к LDAP серверу'
              : 'Ошибка сервера при аутентификации'
          } else {
            errorMessage = `Ошибка аутентификации (${response.status})`
          }
        }
        
        return {
          success: false,
          error: errorMessage
        }
      }

      const data = await response.json()
      
      if (isLdapEnabled) {
        console.log('[Auth] LDAP authentication successful for user:', username)
      }
      
      // Сохраняем токены
      this.accessToken = data.token
      this.refreshToken = data.refreshToken
      this.sessionToken = data.refreshToken // Для совместимости
      
      // Проверяем, является ли это pending registration (пользователь еще не создан)
      const isPendingRegistration = data.pending_registration || false
      
      // Формируем объект пользователя
      const user = {
        id: data.user.id || null,  // Может быть null для pending registration
        username: data.user.username,
        role: data.user.role,
        full_name: data.user.full_name || data.user.username,
        email: data.user.email || `${data.user.username}@example.com`,
        is_active: true,
        pending_registration: isPendingRegistration
      }

      // Сохраняем данные в localStorage
      this.currentUser = user
      localStorage.setItem('auth_token', this.accessToken)
      localStorage.setItem('refresh_token', this.refreshToken)
      localStorage.setItem('user', JSON.stringify(user))

      return {
        success: true,
        user: user,
        token: this.accessToken,
        refreshToken: this.refreshToken,
        requires_registration: data.requires_registration || false,  // Флаг необходимости регистрации
        pending_registration: isPendingRegistration  // Флаг pending registration
      }

    } catch (error) {
      console.error('[Auth] Login error:', error)
      
      const isLdapEnabled = import.meta.env.VITE_LDAP_ENABLED === 'true' || 
                            import.meta.env.VITE_LDAP_ENABLED === true
      
      let errorMessage = 'Connection error'

      if (error && (error.name === 'AbortError' || String(error.message || '').toLowerCase().includes('aborted'))) {
        errorMessage = isLdapEnabled
          ? 'LDAP отвечает слишком долго. Попробуйте позже или обратитесь к администратору.'
          : 'Сервер отвечает слишком долго. Попробуйте позже.'
      } else
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = isLdapEnabled
          ? 'Не удалось подключиться к серверу. Проверьте подключение к сети.'
          : 'Не удалось подключиться к серверу'
      } else {
        errorMessage = error.message || 'Неизвестная ошибка при входе'
      }
      
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  // Выход из системы
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      
      // Отправляем запрос на сервер для удаления сессии
      if (refreshToken) {
        try {
          await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refreshToken: refreshToken
            }),
          })
        } catch (error) {
          console.warn('Logout request failed:', error)
        }
      }

      // Очищаем локальные данные
      this.currentUser = null
      this.sessionToken = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      return { success: true }
    } catch (error) {
      console.error('Logout error:', error)
      // В любом случае очищаем локальные данные
      this.currentUser = null
      this.sessionToken = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      return { success: true }
    }
  }

  // Проверка авторизации
  async checkAuth() {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        return { isAuthenticated: false }
      }

      // Проверяем токен на сервере
      try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })

        if (!response.ok) {
          // Токен недействителен, пытаемся обновить
          const refreshed = await this.refreshAccessToken()
          if (!refreshed) {
            this.logout()
            return { isAuthenticated: false }
          }
          // Повторяем запрос с новым токеном
          const retryResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${this.accessToken}`,
              'Content-Type': 'application/json',
            },
          })
          if (!retryResponse.ok) {
            this.logout()
            return { isAuthenticated: false }
          }
        }

        const data = await response.json()
        const user = data.user

        // Обновляем данные пользователя
        this.currentUser = {
          id: user.sub || user.id,
          username: user.username,
          role: user.role,
          full_name: user.full_name || user.username,
          email: user.email || `${user.username}@example.com`,
          is_active: true
        }
        this.sessionToken = token
        this.accessToken = token

        // Сохраняем обновленные данные
        localStorage.setItem('user', JSON.stringify(this.currentUser))
        localStorage.setItem('auth_token', token)

        return {
          isAuthenticated: true,
          user: this.currentUser
        }
      } catch (apiError) {
        console.error('Auth check API error:', apiError)
        // Fallback: проверяем localStorage
        const userStr = localStorage.getItem('user')
        if (userStr) {
          try {
            const user = JSON.parse(userStr)
            this.currentUser = user
            this.sessionToken = token
            return {
              isAuthenticated: true,
              user: user
            }
          } catch (parseError) {
            this.logout()
            return { isAuthenticated: false }
          }
        }
        this.logout()
        return { isAuthenticated: false }
      }

    } catch (error) {
      console.error('Auth check error:', error)
      return { isAuthenticated: false }
    }
  }

  // Обновление access token
  async refreshAccessToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        return false
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refreshToken: refreshToken
        }),
      })

      if (!response.ok) {
        return false
      }

      const data = await response.json()
      this.accessToken = data.token
      localStorage.setItem('auth_token', data.token)

      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      return false
    }
  }

  // Получение текущего пользователя
  getCurrentUser() {
    // Если currentUser не установлен, пытаемся загрузить из localStorage
    if (!this.currentUser) {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          this.currentUser = JSON.parse(userStr)
        }
      } catch (error) {
        console.error('Error parsing user from localStorage:', error)
      }
    }
    
    // Синхронизируем с localStorage для актуальности данных
    // (на случай если данные были обновлены в другом месте, например в Profile)
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const userFromStorage = JSON.parse(userStr)
        // Если есть данные в localStorage и они отличаются, обновляем currentUser
        if (userFromStorage && userFromStorage.id) {
          // Сравниваем ключевые поля для определения изменений
          if (!this.currentUser || 
              this.currentUser.full_name !== userFromStorage.full_name ||
              this.currentUser.avatar_url !== userFromStorage.avatar_url ||
              this.currentUser.avatar !== userFromStorage.avatar ||
              this.currentUser.station !== userFromStorage.station ||
              this.currentUser.position !== userFromStorage.position) {
            // Создаем новый объект для реактивности Vue
            this.currentUser = { ...userFromStorage }
          }
        }
      }
    } catch (error) {
      console.error('Error syncing user from localStorage:', error)
    }
    
    return this.currentUser
  }
  
  // Метод для принудительного обновления пользователя из localStorage
  refreshUser() {
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        this.currentUser = JSON.parse(userStr)
      }
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
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
      // Supabase removed - using localStorage only
      if (this.currentUser && this.currentUser.id === userId) {
        this.currentUser = { ...this.currentUser, ...updates }
        localStorage.setItem('user', JSON.stringify(this.currentUser))
      }

      return { success: true, user: this.currentUser }
    } catch (error) {
      console.error('Update profile error:', error)
      return { success: false, error: error.message }
    }
  }
}

// Создаем единственный экземпляр сервиса
const authService = new AuthService()

export default authService
