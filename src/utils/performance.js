/**
 * Утилиты для оптимизации производительности
 */

// Debounce - откладывает выполнение функции
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Throttle - ограничивает частоту вызова функции
export function throttle(func, limit = 300) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Мемоизация для функций
export function memoize(func, options = {}) {
  const cache = new Map()
  const maxSize = options.maxSize || 100
  const ttl = options.ttl || 5 * 60 * 1000 // 5 минут по умолчанию
  
  return function(...args) {
    const key = JSON.stringify(args)
    const cached = cache.get(key)
    
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.value
    }
    
    const result = func.apply(this, args)
    
    // Ограничиваем размер кэша
    if (cache.size >= maxSize) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }
    
    cache.set(key, {
      value: result,
      timestamp: Date.now()
    })
    
    return result
  }
}

// Кэш с LRU (Least Recently Used)
export class LRUCache {
  constructor(maxSize = 50) {
    this.maxSize = maxSize
    this.cache = new Map()
  }
  
  get(key) {
    if (!this.cache.has(key)) return undefined
    
    const value = this.cache.get(key)
    // Перемещаем в конец (делаем последним использованным)
    this.cache.delete(key)
    this.cache.set(key, value)
    
    return value
  }
  
  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key)
    }
    
    if (this.cache.size >= this.maxSize) {
      // Удаляем первый (самый старый) элемент
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    
    this.cache.set(key, value)
  }
  
  has(key) {
    return this.cache.has(key)
  }
  
  clear() {
    this.cache.clear()
  }
  
  get size() {
    return this.cache.size
  }
}

// Ленивая загрузка изображений
export function lazyLoadImages() {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target
          img.src = img.dataset.src
          img.classList.remove('lazy')
          observer.unobserve(img)
        }
      })
    })
    
    return imageObserver
  }
  
  return null
}

// Prefetch ресурса
export function prefetchResource(url, type = 'fetch') {
  if (typeof document === 'undefined') return
  
  const link = document.createElement('link')
  link.rel = type === 'preload' ? 'preload' : 'prefetch'
  link.href = url
  
  if (type === 'preload') {
    if (url.endsWith('.js')) {
      link.as = 'script'
    } else if (url.endsWith('.css')) {
      link.as = 'style'
    } else if (url.match(/\.(jpg|jpeg|png|webp|gif)$/)) {
      link.as = 'image'
    }
  }
  
  document.head.appendChild(link)
}

// Preconnect к домену
export function preconnectDomain(domain) {
  if (typeof document === 'undefined') return
  
  const link = document.createElement('link')
  link.rel = 'preconnect'
  link.href = domain
  link.crossOrigin = 'anonymous'
  document.head.appendChild(link)
}

// RAF Throttle для scroll/resize событий
export function rafThrottle(callback) {
  let requestId = null
  
  return function(...args) {
    if (requestId) {
      return
    }
    
    requestId = requestAnimationFrame(() => {
      callback.apply(this, args)
      requestId = null
    })
  }
}

// Idle callback wrapper
export function runWhenIdle(callback, options = {}) {
  if ('requestIdleCallback' in window) {
    return requestIdleCallback(callback, options)
  } else {
    return setTimeout(callback, 1)
  }
}

// Батчинг операций
export class BatchProcessor {
  constructor(processor, options = {}) {
    this.processor = processor
    this.batchSize = options.batchSize || 10
    this.delay = options.delay || 100
    this.queue = []
    this.timeoutId = null
  }
  
  add(item) {
    this.queue.push(item)
    
    if (this.queue.length >= this.batchSize) {
      this.flush()
    } else if (!this.timeoutId) {
      this.timeoutId = setTimeout(() => this.flush(), this.delay)
    }
  }
  
  flush() {
    if (this.queue.length === 0) return
    
    const batch = this.queue.splice(0, this.batchSize)
    this.processor(batch)
    
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
  }
}

