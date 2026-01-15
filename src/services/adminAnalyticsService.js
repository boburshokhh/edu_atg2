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
    ...options.headers
  }

  if (token) {
    headers.Authorization = token
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers
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

class AdminAnalyticsService {
  async getCourseAnalytics(stationId) {
    try {
      const data = await apiRequest(`/courses/admin/course-analytics?station_id=${stationId}`)
      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error loading course analytics:', error)
      return { success: false, error: error.message }
    }
  }
}

export default new AdminAnalyticsService()
