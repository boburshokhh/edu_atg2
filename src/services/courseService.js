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

  /**
   * Save material progress (video position, PDF page, etc.)
   * @param {Object} progressData - Progress data to save
   * @param {number} progressData.course_program_id - Course program ID
   * @param {string} progressData.material_key - Unique material identifier (objectKey)
   * @param {string} progressData.material_type - Type: 'video', 'pdf', 'document'
   * @param {number} progressData.position_seconds - Current position in seconds (for video)
   * @param {number} progressData.duration_seconds - Total duration in seconds
   * @param {number} progressData.lesson_id - Optional lesson ID
   * @param {number} progressData.topic_id - Optional topic ID
   */
  async saveMaterialProgress(progressData) {
    try {
      const data = await apiRequest('/courses/progress/save', {
        method: 'POST',
        body: JSON.stringify(progressData),
      })
      return { success: true, data: data.data }
    } catch (error) {
      console.error('Error saving material progress:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Get progress for a specific material
   * @param {string} materialKey - Material identifier (objectKey)
   * @param {number} courseProgramId - Optional course program ID for filtering
   */
  async getMaterialProgress(materialKey, courseProgramId = null) {
    try {
      let url = `/courses/progress/${encodeURIComponent(materialKey)}`
      if (courseProgramId) {
        url += `?course_program_id=${courseProgramId}`
      }
      const data = await apiRequest(url)
      return { success: true, data: data.data, found: data.found }
    } catch (error) {
      console.error('Error loading material progress:', error)
      return { success: false, error: error.message, found: false }
    }
  }

  /**
   * Get progress for multiple materials at once (batch request)
   * @param {string[]} materialKeys - Array of material identifiers
   * @param {number} courseProgramId - Optional course program ID for filtering
   */
  async getBatchMaterialProgress(materialKeys, courseProgramId = null) {
    try {
      const body = { material_keys: materialKeys }
      if (courseProgramId) {
        body.course_program_id = courseProgramId
      }
      const data = await apiRequest('/courses/progress/batch', {
        method: 'POST',
        body: JSON.stringify(body),
      })
      return { success: true, data: data.data, found: data.found }
    } catch (error) {
      console.error('Error loading batch material progress:', error)
      return { success: false, error: error.message, data: {} }
    }
  }
}

export default new CourseService()
