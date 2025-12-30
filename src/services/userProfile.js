// User Profile Service for Django API

// API base URL - always use /api proxy (works in both dev and prod)
const API_BASE_URL = '/api'

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (token) {
    return `Bearer ${token.trim()}`
  }
  return null
}

/**
 * Make API request with authentication
 */
async function apiRequest(url, options = {}) {
  const token = getAuthToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = token
  }

  const fullUrl = `${API_BASE_URL}${url}`
  console.log('[userProfileService] Request:', options.method || 'GET', fullUrl)

  const response = await fetch(fullUrl, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
    }
    console.error('[userProfileService] Error response:', response.status, errorData)
    const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(errorMessage)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

class UserProfileService {
  // Получение профиля пользователя
  async getProfile(userId) {
    try {
      const data = await apiRequest('/users/me')
      
      if (data.data) {
        // Маппинг данных из Django API
        return {
          success: true,
          data: {
            id: data.data.id,
            username: data.data.username,
            role: data.data.role,
            full_name: data.data.full_name,
            email: data.data.email,
            avatar_url: data.data.avatar_url,
            company: data.data.company, // Station name
            position: data.data.position,
            phone: data.data.phone,
            bio: data.data.bio,
            language: data.data.language || 'ru',
            email_notifications: data.data.email_notifications !== false,
            push_notifications: data.data.push_notifications !== false,
            weekly_report: data.data.weekly_report || false,
            // Для совместимости с фронтендом
            station: data.data.company, // Маппинг company -> station
            avatar: data.data.avatar_url,
            name: data.data.full_name
          }
        }
      }
      
      return { success: false, error: 'Profile data not found' }
    } catch (error) {
      console.error('Error getting profile:', error)
      return { success: false, error: error.message }
    }
  }

  // Сохранение профиля
  async saveProfile(userId, profileData) {
    try {
      // Маппинг данных для Django API
      const updateData = {
        full_name: profileData.full_name || profileData.name,
        email: profileData.email,
        company: profileData.company || profileData.station, // Маппинг station -> company
        position: profileData.position,
        phone: profileData.phone,
        bio: profileData.bio,
        language: profileData.language,
        email_notifications: profileData.email_notifications,
        push_notifications: profileData.push_notifications,
        weekly_report: profileData.weekly_report
      }
      
      // Удаляем undefined значения
      Object.keys(updateData).forEach(key => {
        if (updateData[key] === undefined) {
          delete updateData[key]
        }
      })
      
      const data = await apiRequest('/users/me', {
        method: 'PUT',
        body: JSON.stringify(updateData)
      })
      
      if (data.success) {
        return { success: true, data: updateData }
      }
      
      return { success: false, error: 'Failed to save profile' }
    } catch (error) {
      console.error('Error saving profile:', error)
      return { success: false, error: error.message }
    }
  }

  // Загрузка аватара
  async uploadAvatar(userId, file) {
    try {
      if (!file) {
        return { success: false, error: 'No file provided' }
      }

      // Validate file type
      if (!file.type || !file.type.startsWith('image/')) {
        return { success: false, error: 'Only image files are allowed' }
      }

      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024 // 5MB
      if (file.size > maxSize) {
        return { success: false, error: 'File is too large (max 5MB)' }
      }

      // Create FormData for multipart upload
      const formData = new FormData()
      formData.append('file', file)

      // Get auth token
      const token = getAuthToken()
      if (!token) {
        return { success: false, error: 'Authentication required' }
      }

      // Upload avatar
      const fullUrl = `${API_BASE_URL}/users/me/avatar`
      console.log('[userProfileService] Uploading avatar to:', fullUrl)

      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Authorization': token
          // Don't set Content-Type - browser will set it with boundary for FormData
        },
        body: formData
      })

      if (!response.ok) {
        let errorData
        try {
          errorData = await response.json()
        } catch {
          errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
        }
        console.error('[userProfileService] Avatar upload error:', response.status, errorData)
        const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      if (data.success && data.url) {
        console.log('[userProfileService] Avatar uploaded successfully:', data.key)
        return {
          success: true,
          url: data.url,
          key: data.key
        }
      }

      return { success: false, error: 'Upload failed' }
    } catch (error) {
      console.error('Error uploading avatar:', error)
      return { success: false, error: error.message }
    }
  }

  // Сохранение аватара как base64 (пока не реализовано)
  async saveAvatarAsBase64(userId, file) {
    return new Promise((resolve) => {
      resolve({ success: false, error: 'Avatar upload not yet implemented' })
    })
  }

  // Получение курсов пользователя
  async getUserCourses(userId) {
    try {
      const data = await apiRequest('/courses/me/enrollments')
      
      if (data.data) {
        // Маппинг данных для совместимости с фронтендом
        return {
          success: true,
          data: data.data.map(course => ({
            id: course.course_id,
            course_id: course.course_id,
            title: course.title,
            description: course.description,
            progress_percent: course.progress_percent || 0,
            status: course.progress_percent === 100 ? 'completed' : 
                   course.progress_percent > 0 ? 'in_progress' : 'not_started',
            station_id: course.station_id,
            course: {
              id: course.course_id,
              title: course.title,
              description: course.description,
              icon: 'Monitor' // По умолчанию
            }
          }))
        }
      }
      
      return { success: true, data: [] }
    } catch (error) {
      console.error('Error getting user courses:', error)
      return { success: false, error: error.message, data: [] }
    }
  }

  // Добавление курса пользователю
  async enrollInCourse(userId, courseId) {
    try {
      const data = await apiRequest(`/courses/${courseId}/enroll`, {
        method: 'POST'
      })
      
      if (data.success) {
        return { success: true }
      }
      
      return { success: false, error: 'Failed to enroll in course' }
    } catch (error) {
      console.error('Error enrolling in course:', error)
      return { success: false, error: error.message }
    }
  }

  // Обновление прогресса курса (пока не реализовано на бэкенде)
  async updateCourseProgress(userId, courseId, progress) {
    try {
      // TODO: Реализовать обновление прогресса через Django API
      return { success: false, error: 'Progress update not yet implemented' }
    } catch (error) {
      console.error('Error updating course progress:', error)
      return { success: false, error: error.message }
    }
  }

  // Получение статистики пользователя
  async getUserStats(userId) {
    try {
      const data = await apiRequest('/users/me/stats')
      
      if (data.stats) {
        return {
          success: true,
          data: {
            completed_courses: data.stats.completed_courses || 0,
            active_courses: data.stats.active_courses || 0,
            total_progress: data.stats.total_progress || 0,
            total_hours_studied: 0, // Пока не реализовано на бэкенде
            certificates: data.certificates || []
          }
        }
      }
      
      return { success: true, data: {} }
    } catch (error) {
      console.error('Error getting user stats:', error)
      return { success: false, error: error.message, data: {} }
    }
  }

  // Обновление статистики пользователя (не требуется, статистика вычисляется автоматически)
  async updateUserStats(userId) {
    return { success: true }
  }

  // Получение сертификатов
  async getCertificates(userId) {
    try {
      const data = await apiRequest('/users/me/stats')
      
      if (data.certificates) {
        return {
          success: true,
          data: data.certificates.map(cert => ({
            id: cert.id,
            title: cert.title,
            issued_at: cert.issued_at
          }))
        }
      }
      
      return { success: true, data: [] }
    } catch (error) {
      console.error('Error getting certificates:', error)
      return { success: false, error: error.message, data: [] }
    }
  }
}

const userProfileService = new UserProfileService()
export default userProfileService
