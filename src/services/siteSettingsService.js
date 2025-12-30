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
}

const siteSettingsService = new SiteSettingsService()
export default siteSettingsService


