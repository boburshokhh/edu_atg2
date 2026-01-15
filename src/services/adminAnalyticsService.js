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
    const message = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(message)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

class AdminAnalyticsService {
  async getOverviewStats() {
    const data = await apiRequest('/courses/admin/analytics/overview')
    return data.data
  }

  async getCoursesAnalytics() {
    const data = await apiRequest('/courses/admin/analytics/courses')
    return data.data || []
  }

  async getCourseDetail(courseProgramId) {
    const data = await apiRequest(`/courses/admin/analytics/courses/${courseProgramId}`)
    return data.data
  }

  async getCourseParticipants(courseProgramId) {
    const data = await apiRequest(`/courses/admin/analytics/courses/${courseProgramId}/participants`)
    return data.data || []
  }

  async getUsersAnalytics() {
    const data = await apiRequest('/courses/admin/analytics/users')
    return data.data || []
  }

  async getUserDetail(userId) {
    const data = await apiRequest(`/courses/admin/analytics/users/${userId}`)
    return data.data
  }

  async getMaterialsAnalytics() {
    const data = await apiRequest('/courses/admin/analytics/materials')
    return data.data
  }
}

export default new AdminAnalyticsService()
