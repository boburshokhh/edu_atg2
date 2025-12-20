import { ref } from 'vue'

// Глобальное состояние уведомлений
const notifications = ref([])

// Счетчик для генерации уникальных ID
let count = 0

export default function useNotify() {
  
  /**
   * Удалить уведомление по ID
   * @param {number} id 
   */
  const remove = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * Добавить уведомление
   * @param {Object} options Параметры уведомления
   * @param {string} options.type 'success', 'error', 'warning', 'info'
   * @param {string} options.title Заголовок
   * @param {string} options.message Основной текст
   * @param {number} options.duration Время показа в мс (0 - не закрывать автоматически)
   * @param {Array} options.actions Массив кнопок [{ label, onClick, variant }]
   */
  const add = ({ 
    type = 'info', 
    title = '', 
    message = '', 
    duration = 5000,
    actions = [] 
  }) => {
    const id = count++
    
    const notification = {
      id,
      type,
      title,
      message,
      duration,
      actions
    }

    notifications.value.push(notification)

    // Автоматическое закрытие
    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  // Удобные методы-обертки
  const success = (options) => add({ ...options, type: 'success' })
  const error = (options) => add({ ...options, type: 'error' })
  const warning = (options) => add({ ...options, type: 'warning' })
  const info = (options) => add({ ...options, type: 'info' })

  return {
    notifications,
    add,
    remove,
    success,
    error,
    warning,
    info
  }
}


