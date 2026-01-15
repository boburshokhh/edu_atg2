const API_BASE_URL = '/api'

export const MULTIPART_CHUNK_SIZE = 10 * 1024 * 1024 // 10MB
export const MULTIPART_THRESHOLD = 100 * 1024 * 1024 // 100MB

function getAuthToken() {
  const token = localStorage.getItem('auth_token')
  if (typeof token === 'string' && token.trim()) {
    return `Bearer ${token.trim()}`
  }
  return null
}

async function apiJsonRequest(url, options = {}) {
  const token = getAuthToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers['Authorization'] = token
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
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
    const errorMessage = errorData.error || errorData.message || `HTTP ${response.status}`
    throw new Error(errorMessage)
  }

  return response.json()
}

export async function initiateUpload(key, contentType) {
  return apiJsonRequest('/files/multipart/initiate', {
    method: 'POST',
    body: JSON.stringify({
      key,
      contentType: contentType || 'application/octet-stream',
    }),
  })
}

export async function completeUpload(uploadId, key, parts, contentType) {
  return apiJsonRequest('/files/multipart/complete', {
    method: 'POST',
    body: JSON.stringify({
      uploadId,
      key,
      parts,
      contentType: contentType || 'application/octet-stream',
    }),
  })
}

export async function abortUpload(uploadId, key) {
  return apiJsonRequest('/files/multipart/abort', {
    method: 'POST',
    body: JSON.stringify({ uploadId, key }),
  })
}

export function uploadPart(uploadId, key, partNumber, chunk, onProgress) {
  const token = getAuthToken()

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}/files/multipart/upload-part`)
    if (token) {
      xhr.setRequestHeader('Authorization', token)
    }

    xhr.upload.onprogress = (event) => {
      if (onProgress && event.lengthComputable) {
        onProgress(event.loaded, event.total)
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText)
          resolve(data)
        } catch (err) {
          reject(new Error('Invalid server response'))
        }
        return
      }
      let errorMessage = `HTTP ${xhr.status}`
      try {
        const errorData = JSON.parse(xhr.responseText || '{}')
        errorMessage = errorData.error || errorData.message || errorMessage
      } catch {
        // keep default
      }
      reject(new Error(errorMessage))
    }

    xhr.onerror = () => {
      reject(new Error('Network error during upload'))
    }

    const formData = new FormData()
    formData.append('uploadId', uploadId)
    formData.append('key', key)
    formData.append('partNumber', String(partNumber))
    formData.append('file', chunk)
    xhr.send(formData)
  })
}

export async function uploadFile(file, key, onProgress) {
  let uploadId = null
  try {
    const init = await initiateUpload(key, file.type || 'application/octet-stream')
    uploadId = init.uploadId

    const totalParts = Math.ceil(file.size / MULTIPART_CHUNK_SIZE)
    const parts = []
    let uploadedBytes = 0

    for (let partNumber = 1; partNumber <= totalParts; partNumber += 1) {
      const start = (partNumber - 1) * MULTIPART_CHUNK_SIZE
      const end = Math.min(start + MULTIPART_CHUNK_SIZE, file.size)
      const chunk = file.slice(start, end)

      const part = await uploadPart(uploadId, key, partNumber, chunk, (loaded) => {
        if (!onProgress) return
        const overallLoaded = uploadedBytes + loaded
        const percent = Math.floor((overallLoaded / file.size) * 100)
        onProgress(percent, overallLoaded, file.size)
      })

      parts.push({
        partNumber: part.partNumber || partNumber,
        etag: part.etag,
      })
      uploadedBytes += chunk.size
      if (onProgress) {
        const percent = Math.floor((uploadedBytes / file.size) * 100)
        onProgress(percent, uploadedBytes, file.size)
      }
    }

    const completed = await completeUpload(uploadId, key, parts, file.type || 'application/octet-stream')
    if (onProgress) {
      onProgress(100, file.size, file.size)
    }
    return completed
  } catch (error) {
    if (uploadId) {
      try {
        await abortUpload(uploadId, key)
      } catch (abortError) {
        console.warn('[multipartUploadService] Failed to abort upload:', abortError)
      }
    }
    throw error
  }
}
