/**
 * Helpers for resolving department media references (image) to either:
 * - absolute URL (http/https)
 * - public path (/departments/...)
 * - MinIO object key (departments/...) for presigned URL generation
 */

function normalizeKey(key) {
  return (key || '').trim().replace(/^\/+/, '')
}

function guessContentType(path) {
  const p = (path || '').toLowerCase()
  if (p.endsWith('.png')) return 'image/png'
  if (p.endsWith('.webp')) return 'image/webp'
  if (p.endsWith('.gif')) return 'image/gif'
  if (p.endsWith('.svg')) return 'image/svg+xml'
  if (p.endsWith('.jpg') || p.endsWith('.jpeg')) return 'image/jpeg'
  return 'application/octet-stream'
}

/**
 * @param {string} raw
 * @param {{ defaultFolder: 'departments' }} opts
 * @returns {{
 *   kind: 'none'|'url'|'public'|'minio',
 *   url?: string,
 *   objectKey?: string,
 *   contentType?: string,
 *   fallbackPublicPath?: string
 * }}
 */
export function resolveDepartmentMedia(raw, { defaultFolder }) {
  const value = (raw || '').trim()
  if (!value) return { kind: 'none' }

  if (value.startsWith('http://') || value.startsWith('https://')) {
    return { kind: 'url', url: value }
  }

  // Public/static path (served by Vite/Netlify)
  if (value.startsWith('/')) {
    return { kind: 'public', url: value }
  }

  // MinIO object key (normalize and ensure folder prefix)
  const withFolder = value.includes('/')
    ? value
    : `${defaultFolder}/${value}`

  const objectKey = normalizeKey(withFolder)
  return {
    kind: 'minio',
    objectKey,
    contentType: guessContentType(objectKey),
    fallbackPublicPath: `/${objectKey}`,
  }
}

