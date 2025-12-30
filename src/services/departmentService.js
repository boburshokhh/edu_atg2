// Service for managing departments via Django REST API

// Unified API base - always use /api proxy (works in both dev and prod)
const API_BASE_URL = '/api'

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const token = localStorage.getItem('auth_token')
  // Backend supports both:
  // - JWT (Bearer <jwt>)
  // - session tokens from auth flow (Bearer session_...)
  if (typeof token === 'string' && token.trim()) {
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
    console.log('[departmentService] Using auth token:', token.substring(0, 30) + '...')
  } else {
    console.warn('[departmentService] No auth token found in localStorage')
    console.log('[departmentService] localStorage.auth_token:', localStorage.getItem('auth_token'))
  }

  const fullUrl = `${API_BASE_URL}${url}`
  console.log('[departmentService] Request:', options.method || 'GET', fullUrl)

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
    console.error('[departmentService] Error response:', response.status, errorData)
    const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(errorMessage)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  // For non-JSON responses, return text
  return response.text()
}

class DepartmentService {
  // ==================== Departments ====================

  /**
   * Get all departments
   */
  async getDepartments() {
    const data = await apiRequest('/stations/departments/')
    return data.data || []
  }

  /**
   * Get department by ID
   */
  async getDepartment(id) {
    const data = await apiRequest(`/stations/departments/${id}`)
    return data.data || null
  }

  /**
   * Create a new department
   */
  async createDepartment(departmentData) {
    // Convert camelCase to snake_case for API
    const apiData = {
      name: departmentData.name,
      short_name: departmentData.shortName || departmentData.short_name,
      description: departmentData.description,
      image: departmentData.image,
      status: departmentData.status || 'active',
    }
    const result = await apiRequest('/stations/departments/create/', {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
    return result
  }

  /**
   * Update department
   */
  async updateDepartment(id, departmentData) {
    // Check auth before making request
    const token = getAuthToken()
    if (!token) {
      console.error('[updateDepartment] No auth token! Please login first.')
      throw new Error('Требуется авторизация. Пожалуйста, войдите в систему.')
    }
    
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    console.log('[updateDepartment] User:', user.id, 'Role:', user.role)
    
    if (user.role !== 'admin') {
      console.error('[updateDepartment] User is not admin! Role:', user.role)
      throw new Error('Требуется роль администратора.')
    }
    
    const apiData = {
      name: departmentData.name,
      short_name: departmentData.shortName || departmentData.short_name,
      description: departmentData.description,
      image: departmentData.image,
      status: departmentData.status,
    }
    return await apiRequest(`/stations/departments/${id}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  /**
   * Delete department
   */
  async deleteDepartment(id) {
    return await apiRequest(`/stations/departments/${id}/delete/`, {
      method: 'DELETE',
    })
  }
}

// Create and export singleton instance
const departmentService = new DepartmentService()
export default departmentService

