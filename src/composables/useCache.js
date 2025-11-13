import { ref, readonly } from 'vue'
import { LRUCache } from '@/utils/performance'

/**
 * Composable для управления кэшированием
 */
export function useCache(options = {}) {
  const maxSize = options.maxSize || 50
  const ttl = options.ttl || 5 * 60 * 1000 // 5 минут
  
  const cache = new LRUCache(maxSize)
  const stats = ref({
    hits: 0,
    misses: 0,
    size: 0
  })
  
  const get = (key) => {
    const cached = cache.get(key)
    
    if (cached) {
      // Проверяем TTL
      if (Date.now() - cached.timestamp < ttl) {
        stats.value.hits++
        return cached.value
      } else {
        // Удаляем устаревший элемент
        cache.delete(key)
      }
    }
    
    stats.value.misses++
    return undefined
  }
  
  const set = (key, value) => {
    cache.set(key, {
      value,
      timestamp: Date.now()
    })
    stats.value.size = cache.size
  }
  
  const has = (key) => {
    return cache.has(key)
  }
  
  const clear = () => {
    cache.clear()
    stats.value = {
      hits: 0,
      misses: 0,
      size: 0
    }
  }
  
  const remove = (key) => {
    cache.delete(key)
    stats.value.size = cache.size
  }
  
  // Кэширующая обёртка для функций
  const cached = (key, fn) => {
    const cachedValue = get(key)
    if (cachedValue !== undefined) {
      return Promise.resolve(cachedValue)
    }
    
    return Promise.resolve(fn()).then(result => {
      set(key, result)
      return result
    })
  }
  
  return {
    get,
    set,
    has,
    clear,
    remove,
    cached,
    stats: readonly(stats)
  }
}

