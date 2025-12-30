// Site settings service (Hero background, etc.)
// Unified API base - always use /api proxy (works in both dev and prod)
const API_BASE_URL = '/api'

function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (typeof token === 'string' && token.trim()) {
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

  if (token) headers['Authorization'] = token

  const fullUrl = `${API_BASE_URL}${url}`
  const response = await fetch(fullUrl, { ...options, headers })

  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { error: `HTTP ${response.status}: ${response.statusText}` }
    }
    const msg = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
    throw new Error(msg)
  }

  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

class SiteSettingsService {
  /**
   * Public: get current hero background
   * @returns {Promise<{image_key: string|null, url: string|null}>}
   */
  async getHeroImage() {
    const data = await apiRequest('/site/hero-image', { method: 'GET' })
    return {
      image_key: data?.image_key ?? null,
      url: data?.url ?? null,
    }
  }

  /**
   * Admin: set hero background to existing MinIO key
   * @param {string} key - object key in MinIO (must start with hero/)
   */
  async setHeroImageKey(key) {
    const data = await apiRequest('/site/hero-image', {
      method: 'PUT',
      body: JSON.stringify({ key }),
    })
    return data
  }

  /**
   * Admin: upload file to MinIO via backend /files/upload then bind key via /site/hero-image
   * Uses existing StationService upload helper to avoid any direct S3/MinIO access from frontend.
   * @param {File} file
   */
  async updateHeroImage(file) {
    const { default: stationService } = await import('./stationService')
    const key = await stationService.uploadFile(file, 'hero')
    return await this.setHeroImageKey(key)
  }

  /**
   * Public: get hero slider images
   * @returns {Promise<{items: Array<{id: number, key: string, url: string, orderIndex: number}>}>}
   */
  async getHeroSlider() {
    const data = await apiRequest('/site/hero-slider', { method: 'GET' })
    return {
      items: data?.items || [],
    }
  }

  /**
   * Admin: upload multiple files for hero slider
   * @param {File[]} files - Array of File objects
   * @returns {Promise<{uploaded: Array<{key: string, url: string}>}>}
   */
  async uploadHeroSlides(files) {
    if (!files || files.length === 0) {
      throw new Error('No files provided')
    }

    const token = getAuthToken()
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files[]', file)
    })

    const headers = {}
    if (token) headers['Authorization'] = token

    const response = await fetch(`${API_BASE_URL}/site/hero-slider/upload`, {
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
      const msg = errorData.error || errorData.message || errorData.detail || `HTTP ${response.status}`
      throw new Error(msg)
    }

    return await response.json()
  }

  /**
   * Admin: set hero slider keys (replace all)
   * @param {string[]} keys - Array of MinIO object keys (must start with hero/)
   * @returns {Promise<{ok: boolean, items: Array}>}
   */
  async setHeroSliderKeys(keys) {
    if (!Array.isArray(keys)) {
      throw new Error('keys must be an array')
    }

    const data = await apiRequest('/site/hero-slider', {
      method: 'PUT',
      body: JSON.stringify({ keys }),
    })
    return data
  }

  /**
   * Admin: load hero slider images from public/slider folder
   * @returns {Promise<{uploaded: Array<{key: string, url: string}>, count: number}>}
   */
  async loadHeroSlidesFromPublic() {
    const data = await apiRequest('/site/hero-slider/load-from-public', {
      method: 'POST',
    })
    return data
  }
}

const siteSettingsService = new SiteSettingsService()
export default siteSettingsService


