// Service for managing stations via Django REST API

// Unified API base:
// - Dev: use Vite proxy via same-origin path (/api)
// - Prod: use explicit URL (VITE_API_BASE_URL) or fall back to same-origin (/api)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

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
    console.log('[stationService] Using auth token:', token.substring(0, 30) + '...')
  } else {
    console.warn('[stationService] No auth token found in localStorage')
    console.log('[stationService] localStorage.auth_token:', localStorage.getItem('auth_token'))
  }

  const fullUrl = `${API_BASE_URL}${url}`
  console.log('[stationService] Request:', options.method || 'GET', fullUrl)

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
    console.error('[stationService] Error response:', response.status, errorData)
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

class StationService {
  // ==================== Stations ====================

  /**
   * Get all stations
   */
  async getStations() {
    const data = await apiRequest('/stations/')
    return data.data || []
  }

  /**
   * Get station by ID with all related data
   */
  async getStation(id) {
    const data = await apiRequest(`/stations/${id}`)
    return data
  }

  // ==================== Course Program ====================

  /**
   * Public: get course program structure for station (StationCourses/LessonViewer)
   */
  async getStationCourseProgram(stationId) {
    const data = await apiRequest(`/stations/${stationId}/course-program`)
    return data.courseProgram || null
  }

  /**
   * Admin: update course program structure for station
   */
  async updateStationCourseProgram(stationId, payload) {
    // Requires admin auth
    return await apiRequest(`/stations/${stationId}/course-program/update`, {
      method: 'PUT',
      body: JSON.stringify(payload || {}),
    })
  }

  // ==================== Promo Video ====================

  /**
   * Public: get station promo video (object key)
   */
  async getStationPromoVideo(stationId) {
    const data = await apiRequest(`/stations/${stationId}/promo-video`)
    return data.video || null
  }

  /**
   * Admin: set/replace promo video for station
   */
  async updateStationPromoVideo(stationId, payload) {
    return await apiRequest(`/stations/${stationId}/promo-video/update`, {
      method: 'PUT',
      body: JSON.stringify(payload || {}),
    })
  }

  /**
   * Admin: delete promo video record (optionally delete object too)
   */
  async deleteStationPromoVideo(stationId, { deleteObject = false } = {}) {
    const qs = deleteObject ? '?deleteObject=1' : ''
    return await apiRequest(`/stations/${stationId}/promo-video/delete${qs}`, {
      method: 'DELETE',
    })
  }

  // ==================== Course Program Topic Files ====================

  async getCourseProgramTopicFiles(stationId, topicId) {
    const data = await apiRequest(`/stations/${stationId}/course-program/topics/${topicId}/files`)
    return data.data || []
  }

  async createCourseProgramTopicFile(stationId, topicId, fileData) {
    const payload = {
      title: fileData.title || '',
      originalName: fileData.originalName || fileData.original_name || fileData.fileName || '',
      objectKey: fileData.objectKey || fileData.object_key,
      fileType: fileData.fileType || fileData.file_type,
      isMain: !!(fileData.isMain ?? fileData.is_main),
      orderIndex: fileData.orderIndex ?? fileData.order_index ?? 0,
      fileSize: fileData.fileSize ?? fileData.file_size ?? null,
      mimeType: fileData.mimeType || fileData.mime_type || null,
    }
    return await apiRequest(`/stations/${stationId}/course-program/topics/${topicId}/files/create/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async updateCourseProgramTopicFile(stationId, topicId, fileId, patch) {
    const payload = { ...patch }
    return await apiRequest(
      `/stations/${stationId}/course-program/topics/${topicId}/files/${fileId}/update/`,
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      }
    )
  }

  async deleteCourseProgramTopicFile(stationId, topicId, fileId, { deleteObject = false } = {}) {
    const qs = deleteObject ? '?deleteObject=1' : ''
    return await apiRequest(
      `/stations/${stationId}/course-program/topics/${topicId}/files/${fileId}/delete/${qs}`,
      { method: 'DELETE' }
    )
  }

  /**
   * Create a new station
   */
  async createStation(stationData) {
    // Convert camelCase to snake_case for API
    const apiData = {
      name: stationData.name,
      short_name: stationData.shortName || stationData.short_name,
      description: stationData.description,
      image: stationData.image,
      tech_map_image: stationData.techMapImage || stationData.tech_map_image,
      power: stationData.power,
      commission_date: stationData.commissionDate || stationData.commission_date,
      courses_count: stationData.coursesCount || stationData.courses_count || 0,
      status: stationData.status || 'active',
      location: stationData.location,
      type: stationData.type,
      design_capacity: stationData.designCapacity || stationData.design_capacity,
      gas_pressure: stationData.gasPressure || stationData.gas_pressure,
      distance_from_border: stationData.distanceFromBorder || stationData.distance_from_border,
      pipeline_diameter: stationData.pipelineDiameter || stationData.pipeline_diameter,
      input_pressure: stationData.inputPressure || stationData.input_pressure,
      output_pressure: stationData.outputPressure || stationData.output_pressure,
      parallel_lines: stationData.parallelLines || stationData.parallel_lines,
    }
    return await apiRequest('/stations/create/', {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  /**
   * Update station
   */
  async updateStation(id, stationData) {
    // Check auth before making request
    const token = getAuthToken()
    if (!token) {
      console.error('[updateStation] No auth token! Please login first.')
      throw new Error('Требуется авторизация. Пожалуйста, войдите в систему.')
    }
    
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    console.log('[updateStation] User:', user.id, 'Role:', user.role)
    
    if (user.role !== 'admin') {
      console.error('[updateStation] User is not admin! Role:', user.role)
      throw new Error('Требуется роль администратора.')
    }
    
    const apiData = {
      name: stationData.name,
      short_name: stationData.shortName || stationData.short_name,
      description: stationData.description,
      image: stationData.image,
      tech_map_image: stationData.techMapImage || stationData.tech_map_image,
      power: stationData.power,
      commission_date: stationData.commissionDate || stationData.commission_date,
      courses_count: stationData.coursesCount || stationData.courses_count,
      status: stationData.status,
      location: stationData.location,
      type: stationData.type,
      design_capacity: stationData.designCapacity || stationData.design_capacity,
      gas_pressure: stationData.gasPressure || stationData.gas_pressure,
      distance_from_border: stationData.distanceFromBorder || stationData.distance_from_border,
      pipeline_diameter: stationData.pipelineDiameter || stationData.pipeline_diameter,
      input_pressure: stationData.inputPressure || stationData.input_pressure,
      output_pressure: stationData.outputPressure || stationData.output_pressure,
      parallel_lines: stationData.parallelLines || stationData.parallel_lines,
    }
    return await apiRequest(`/stations/${id}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  /**
   * Delete station
   */
  async deleteStation(id) {
    return await apiRequest(`/stations/${id}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Equipment ====================

  async getEquipment(stationId) {
    const data = await apiRequest(`/stations/${stationId}/equipment`)
    return data.data || []
  }

  async createEquipment(stationId, equipmentData) {
    const apiData = {
      name: equipmentData.name,
      model: equipmentData.model,
      manufacturer: equipmentData.manufacturer,
      quantity: equipmentData.quantity || 1,
      power: equipmentData.power,
      description: equipmentData.description,
      order_index: equipmentData.orderIndex || equipmentData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/equipment/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async updateEquipment(stationId, equipmentId, equipmentData) {
    const apiData = {
      name: equipmentData.name,
      model: equipmentData.model,
      manufacturer: equipmentData.manufacturer,
      quantity: equipmentData.quantity,
      power: equipmentData.power,
      description: equipmentData.description,
      order_index: equipmentData.orderIndex || equipmentData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/equipment/${equipmentId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  async deleteEquipment(stationId, equipmentId) {
    return await apiRequest(`/stations/${stationId}/equipment/${equipmentId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Specifications ====================

  async getSpecifications(stationId) {
    const data = await apiRequest(`/stations/${stationId}/specs`)
    return data.data || []
  }

  async createSpecification(stationId, specData) {
    const apiData = {
      category: specData.category,
      value: specData.value,
      unit: specData.unit,
      description: specData.description,
      order_index: specData.orderIndex || specData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/specs/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async updateSpecification(stationId, specId, specData) {
    const apiData = {
      category: specData.category,
      value: specData.value,
      unit: specData.unit,
      description: specData.description,
      order_index: specData.orderIndex || specData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/specs/${specId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  async deleteSpecification(stationId, specId) {
    return await apiRequest(`/stations/${stationId}/specs/${specId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Safety Systems ====================

  async getSafetySystems(stationId) {
    const data = await apiRequest(`/stations/${stationId}/safety`)
    return data.data || []
  }

  async createSafetySystem(stationId, safetyData) {
    const apiData = {
      name: safetyData.name,
      description: safetyData.description,
      manufacturer: safetyData.manufacturer,
      order_index: safetyData.orderIndex || safetyData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/safety/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async updateSafetySystem(stationId, safetyId, safetyData) {
    const apiData = {
      name: safetyData.name,
      description: safetyData.description,
      manufacturer: safetyData.manufacturer,
      order_index: safetyData.orderIndex || safetyData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/safety/${safetyId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  async deleteSafetySystem(stationId, safetyId) {
    return await apiRequest(`/stations/${stationId}/safety/${safetyId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Safety System Features ====================

  async createSafetySystemFeature(stationId, safetyId, featureData) {
    const apiData = {
      feature_name: featureData.featureName || featureData.feature_name,
      order_index: featureData.orderIndex || featureData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/safety/${safetyId}/features/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async updateSafetySystemFeature(stationId, safetyId, featureId, featureData) {
    const apiData = {
      feature_name: featureData.featureName || featureData.feature_name,
      order_index: featureData.orderIndex || featureData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/safety/${safetyId}/features/${featureId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  async deleteSafetySystemFeature(stationId, safetyId, featureId) {
    return await apiRequest(`/stations/${stationId}/safety/${safetyId}/features/${featureId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Gas Supply Sources ====================

  async getGasSupplySources(stationId) {
    const data = await apiRequest(`/stations/${stationId}/gas-sources`)
    return data.data || []
  }

  async createGasSupplySource(stationId, sourceData) {
    const apiData = {
      source_name: sourceData.sourceName || sourceData.source_name,
      order_index: sourceData.orderIndex || sourceData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/gas-sources/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async updateGasSupplySource(stationId, sourceId, sourceData) {
    const apiData = {
      source_name: sourceData.sourceName || sourceData.source_name,
      order_index: sourceData.orderIndex || sourceData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/gas-sources/${sourceId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  async deleteGasSupplySource(stationId, sourceId) {
    return await apiRequest(`/stations/${stationId}/gas-sources/${sourceId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== Photos ====================

  /**
   * Get all photos for a station
   */
  async getStationPhotos(stationId) {
    const data = await apiRequest(`/stations/${stationId}`)
    return data.photos || []
  }

  /**
   * Create a new station photo
   */
  async createStationPhoto(stationId, photoData) {
    const apiData = {
      title: photoData.title,
      view: photoData.view,
      image_url: photoData.imageUrl || photoData.image_url,
      order_index: photoData.orderIndex || photoData.order_index || 0,
    }
    return await apiRequest(`/stations/${stationId}/photos/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  /**
   * Update an existing station photo
   */
  async updateStationPhoto(stationId, photoId, photoData) {
    const apiData = {
      title: photoData.title,
      view: photoData.view,
      image_url: photoData.imageUrl || photoData.image_url,
      order_index: photoData.orderIndex || photoData.order_index,
    }
    return await apiRequest(`/stations/${stationId}/photos/${photoId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    })
  }

  /**
   * Delete a station photo
   */
  async deleteStationPhoto(stationId, photoId) {
    return await apiRequest(`/stations/${stationId}/photos/${photoId}/delete/`, {
      method: 'DELETE',
    })
  }

  /**
   * Create or update a station photo by view type
   * If a photo with the same view type exists, it will be updated; otherwise, a new one will be created
   */
  async createOrUpdateStationPhoto(stationId, photoData) {
    try {
      // Get all photos for this station
      const photos = await this.getStationPhotos(stationId)
      
      // Find existing photo with the same view type
      const existingPhoto = photos.find(p => p.view === photoData.view)
      
      if (existingPhoto) {
        // Update existing photo
        return await this.updateStationPhoto(stationId, existingPhoto.id, {
          title: photoData.title,
          imageUrl: photoData.imageUrl || photoData.image_url,
          view: photoData.view,
        })
      } else {
        // Create new photo
        return await this.createStationPhoto(stationId, {
          title: photoData.title,
          imageUrl: photoData.imageUrl || photoData.image_url,
          view: photoData.view,
          orderIndex: 0,
        })
      }
    } catch (error) {
      console.error('[createOrUpdateStationPhoto] Error:', error)
      throw error
    }
  }

  // Legacy methods for backward compatibility
  async createPhoto(stationId, photoData) {
    return this.createStationPhoto(stationId, photoData)
  }

  async updatePhoto(stationId, photoId, photoData) {
    return this.updateStationPhoto(stationId, photoId, photoData)
  }

  async deletePhoto(stationId, photoId) {
    return this.deleteStationPhoto(stationId, photoId)
  }

  // ==================== Normative Docs ====================

  async createNormativeDoc(stationId, docData) {
    const apiData = {
      title: docData.title,
      file_url: docData.fileUrl || docData.file_url,
    }
    return await apiRequest(`/stations/${stationId}/docs/create/`, {
      method: 'POST',
      body: JSON.stringify(apiData),
    })
  }

  async deleteNormativeDoc(stationId, docId) {
    return await apiRequest(`/stations/${stationId}/docs/${docId}/delete/`, {
      method: 'DELETE',
    })
  }

  // ==================== File Upload (Minio) ====================

  /**
   * Upload file to Minio via direct upload (bypasses presigned URL issues)
   * @param {File} file - File object to upload
   * @param {string} prefix - Folder prefix (e.g., 'stations/photos')
   * @returns {Promise<string>} - The uploaded file key (path in Minio)
   */
  async uploadFile(file, prefix = 'uploads') {
    const key = `${prefix}/${Date.now()}_${file.name}`.replace(/\s+/g, '_')
    
    // Use FormData for multipart upload
    const formData = new FormData()
    formData.append('file', file)
    formData.append('key', key)
    formData.append('contentType', file.type || 'application/octet-stream')

    // Upload directly through Django backend (uses correct Minio credentials)
    // Use fetch directly instead of apiRequest to avoid Content-Type header issues with FormData
    const token = getAuthToken()
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
    const fullUrl = `${API_BASE_URL}/files/upload`
    
    const headers = {}
    if (token) {
      headers['Authorization'] = token
    }
    // Don't set Content-Type - browser will set it with boundary for FormData

    const response = await fetch(fullUrl, {
      method: 'POST',
      headers,
      body: formData,
    })

    if (!response.ok) {
      let errorData
      try {
        errorData = await response.json()
      } catch {
        errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
      }
      const errorMessage = errorData.error || errorData.message || `HTTP ${response.status}`
      throw new Error(errorMessage)
    }

    const data = await response.json()
    if (!data.ok) {
      throw new Error(data.error || 'Upload failed')
    }

    return key
  }
}

// Create and export singleton instance
const stationService = new StationService()
export default stationService
