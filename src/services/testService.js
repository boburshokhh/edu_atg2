// Service for managing tests via Django REST API

// Unified API base - always use /api proxy (works in both dev and prod)
const API_BASE_URL = '/api'

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const token = localStorage.getItem('auth_token')
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
    console.log('[testService] Using auth token:', token.substring(0, 30) + '...')
  } else {
    console.warn('[testService] No auth token found in localStorage')
  }

  const fullUrl = `${API_BASE_URL}${url}`
  console.log('[testService] Request:', options.method || 'GET', fullUrl)

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
    console.error('[testService] Error response:', response.status, errorData)
    const errorMessage = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(errorMessage)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

class TestService {
  // ==================== Tests ====================

  /**
   * Get all tests (optionally filtered by type)
   * @param {string} type - 'lesson', 'final', or null for all
   */
  async getTests(type = null) {
    const url = type ? `/courses/tests?type=${type}` : '/courses/tests'
    const data = await apiRequest(url)
    return data.data || []
  }

  /**
   * Get test by ID with questions
   * @param {number} testId - Test ID
   * @param {string} testType - 'lesson' or 'final'
   */
  async getTest(testId, testType) {
    const data = await apiRequest(`/courses/tests/${testType}/${testId}`)
    return data.test || null
  }

  /**
   * Create a new test
   * @param {Object} testData - Test data
   * @param {string} testData.test_type - 'lesson' or 'final'
   * @param {string} testData.title - Test title
   * @param {string} testData.description - Test description
   * @param {number} testData.lesson_id - Lesson ID (for lesson tests)
   * @param {number} testData.course_program_id - Course program ID (for final tests)
   * @param {number} testData.passing_score - Passing score (default: 70)
   * @param {number} testData.time_limit - Time limit in minutes (default: 30)
   * @param {number} testData.attempts - Max attempts (null for unlimited)
   */
  async createTest(testData) {
    const payload = {
      test_type: testData.test_type,
      title: testData.title,
      description: testData.description || '',
      passing_score: testData.passing_score || 70,
      time_limit: testData.time_limit || 30,
      attempts: testData.attempts || null,
      is_active: testData.is_active !== undefined ? testData.is_active : true,
    }

    if (testData.test_type === 'lesson') {
      payload.lesson_id = testData.lesson_id
    } else {
      payload.course_program_id = testData.course_program_id
    }

    const data = await apiRequest('/courses/tests/create', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    return data.data
  }

  /**
   * Update test
   * @param {number} testId - Test ID
   * @param {string} testType - 'lesson' or 'final'
   * @param {Object} testData - Updated test data
   */
  async updateTest(testId, testType, testData) {
    const payload = {}
    if (testData.title !== undefined) payload.title = testData.title
    if (testData.description !== undefined) payload.description = testData.description
    if (testData.passing_score !== undefined) payload.passing_score = testData.passing_score
    if (testData.time_limit !== undefined) payload.time_limit = testData.time_limit
    if (testData.attempts !== undefined) payload.attempts = testData.attempts
    if (testData.is_active !== undefined) payload.is_active = testData.is_active

    const data = await apiRequest(`/courses/tests/${testType}/${testId}/update`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    return data.data
  }

  /**
   * Delete test
   * @param {number} testId - Test ID
   * @param {string} testType - 'lesson' or 'final'
   */
  async deleteTest(testId, testType) {
    await apiRequest(`/courses/tests/${testType}/${testId}/delete`, {
      method: 'DELETE',
    })
    return true
  }

  /**
   * Update test questions
   * @param {number} testId - Test ID
   * @param {string} testType - 'lesson' or 'final'
   * @param {Array} questions - Array of question objects
   */
  async updateTestQuestions(testId, testType, questions) {
    const payload = { questions }
    await apiRequest(`/courses/tests/${testType}/${testId}/questions`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    return true
  }

  // ==================== Test Results ====================

  /**
   * Get test results
   * @param {Object} filters - Filter options
   * @param {number} filters.test_id - Filter by test ID
   * @param {string} filters.test_type - Filter by test type
   * @param {string} filters.user_id - Filter by user ID
   */
  async getTestResults(filters = {}) {
    const params = new URLSearchParams()
    if (filters.test_id) params.append('test_id', filters.test_id)
    if (filters.test_type) params.append('test_type', filters.test_type)
    if (filters.user_id) params.append('user_id', filters.user_id)

    const url = `/courses/tests/results${params.toString() ? '?' + params.toString() : ''}`
    const data = await apiRequest(url)
    return data.data || []
  }

  /**
   * Get test result by ID
   * @param {number} resultId - Result ID
   */
  async getTestResult(resultId) {
    const data = await apiRequest(`/courses/tests/results/${resultId}`)
    return data.data || null
  }
}

// Create and export singleton instance
const testService = new TestService()
export default testService

