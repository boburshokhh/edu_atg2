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
    headers['Authorization'] = token
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
    credentials: 'include'
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export default {
  /**
   * Get comments for a lesson/topic/file
   * @param {Object} params - Query parameters
   * @param {number} params.stationId - Station ID (required)
   * @param {number} [params.lessonIndex] - Lesson index
   * @param {number} [params.topicIndex] - Topic index
   * @param {string} [params.fileObjectKey] - File object key
   * @returns {Promise<Array>} Array of comments
   */
  async getComments({ stationId, lessonIndex, topicIndex, fileObjectKey }) {
    const params = new URLSearchParams({ station_id: stationId })
    
    if (lessonIndex !== undefined && lessonIndex !== null) {
      params.append('lesson_index', lessonIndex)
    }
    if (topicIndex !== undefined && topicIndex !== null) {
      params.append('topic_index', topicIndex)
    }
    if (fileObjectKey) {
      params.append('file_object_key', fileObjectKey)
    }

    const data = await apiRequest(`/courses/comments?${params.toString()}`)
    return data.data || []
  },

  /**
   * Create a new comment
   * @param {Object} commentData - Comment data
   * @param {number} commentData.stationId - Station ID (required)
   * @param {number} [commentData.lessonIndex] - Lesson index
   * @param {number} [commentData.topicIndex] - Topic index
   * @param {string} [commentData.fileObjectKey] - File object key
   * @param {string} commentData.commentText - Comment text (required)
   * @returns {Promise<Object>} Created comment
   */
  async createComment({ stationId, lessonIndex, topicIndex, fileObjectKey, commentText }) {
    const data = await apiRequest('/courses/comments', {
      method: 'POST',
      body: JSON.stringify({
        station_id: stationId,
        lesson_index: lessonIndex,
        topic_index: topicIndex,
        file_object_key: fileObjectKey,
        comment_text: commentText
      })
    })
    return data.data
  }
}

