const API_BASE_URL = '/api'

function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (token) {
    return `Bearer ${token.trim()}`
  }
  return null
}

async function apiRequest(url, options = {}) {
  const token = getAuthToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers.Authorization = token
  }

  const fullUrl = `${API_BASE_URL}${url}`
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
    const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(errorMessage)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

class CourseService {
  async enrollInCourseProgram(courseProgramId) {
    try {
      const data = await apiRequest(`/courses/programs/${courseProgramId}/enroll`, {
        method: 'POST',
      })
      return { success: true, data }
    } catch (error) {
      console.error('Error enrolling in course program:', error)
      return { success: false, error: error.message }
    }
  }

  async getCourseProgramProgress(courseProgramId) {
    try {
      const data = await apiRequest(`/courses/programs/${courseProgramId}/progress`)
      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error loading course program progress:', error)
      return { success: false, error: error.message }
    }
  }

  async markMaterialComplete(courseProgramId, materialType, materialKey) {
    try {
      const data = await apiRequest(`/courses/programs/${courseProgramId}/materials/complete`, {
        method: 'POST',
        body: JSON.stringify({
          material_type: materialType,
          material_key: materialKey,
        }),
      })
      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error marking material complete:', error)
      return { success: false, error: error.message }
    }
  }

  async getUserCoursePrograms() {
    try {
      const data = await apiRequest('/courses/me/programs')
      return { success: true, data: data.data || [] }
    } catch (error) {
      console.error('Error loading user course programs:', error)
      return { success: false, error: error.message }
    }
  }

  async getUserCourseStats() {
    try {
      const data = await apiRequest('/courses/me/stats')
      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error loading user course stats:', error)
      return { success: false, error: error.message }
    }
  }
}

export default new CourseService()
