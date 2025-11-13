import { ref, computed } from 'vue'
import { debounce } from '@/utils/performance'

/**
 * Composable для работы с прогрессом обучения
 */
export function useProgress() {
  const completedTopics = ref(new Set())
  const passedTests = ref(new Set())
  
  // Загрузка прогресса из localStorage
  const loadProgress = () => {
    try {
      const savedTopics = localStorage.getItem('completedTopics')
      if (savedTopics) {
        completedTopics.value = new Set(JSON.parse(savedTopics))
      }
      
      const savedTests = localStorage.getItem('passedTests')
      if (savedTests) {
        passedTests.value = new Set(JSON.parse(savedTests))
      }
    } catch (error) {
      console.error('Ошибка загрузки прогресса:', error)
    }
  }
  
  // Сохранение прогресса в localStorage (debounced)
  const saveProgress = debounce(() => {
    try {
      localStorage.setItem('completedTopics', JSON.stringify([...completedTopics.value]))
      localStorage.setItem('passedTests', JSON.stringify([...passedTests.value]))
    } catch (error) {
      console.error('Ошибка сохранения прогресса:', error)
    }
  }, 500)
  
  // Вычисление общего прогресса
  const calculateCourseProgress = (lessons) => {
    let totalTopics = 0
    
    lessons.forEach(lesson => {
      totalTopics += lesson.topics?.length || 0
    })
    
    if (totalTopics === 0) return 0
    
    return Math.round((completedTopics.value.size / totalTopics) * 100)
  }
  
  // Проверка завершения темы
  const isTopicCompleted = (topicId) => {
    return completedTopics.value.has(topicId)
  }
  
  // Отметка темы как завершенной
  const markTopicAsCompleted = (topicId) => {
    if (!completedTopics.value.has(topicId)) {
      completedTopics.value.add(topicId)
      saveProgress()
      return true
    }
    return false
  }
  
  // Снятие отметки завершения
  const unmarkTopicAsCompleted = (topicId) => {
    if (completedTopics.value.has(topicId)) {
      completedTopics.value.delete(topicId)
      saveProgress()
      return true
    }
    return false
  }
  
  // Проверка прохождения теста
  const isTestPassed = (testId) => {
    return passedTests.value.has(testId)
  }
  
  // Отметка теста как пройденного
  const markTestAsPassed = (testId) => {
    if (!passedTests.value.has(testId)) {
      passedTests.value.add(testId)
      saveProgress()
      return true
    }
    return false
  }
  
  // Получение статистики по уроку
  const getLessonStats = (lesson) => {
    const totalTopics = lesson.topics?.length || 0
    let completedCount = 0
    
    lesson.topics?.forEach((topic, index) => {
      const topicId = `${lesson.id}-${index}`
      if (isTopicCompleted(topicId)) {
        completedCount++
      }
    })
    
    return {
      total: totalTopics,
      completed: completedCount,
      progress: totalTopics > 0 ? Math.round((completedCount / totalTopics) * 100) : 0
    }
  }
  
  // Очистка прогресса
  const clearProgress = () => {
    completedTopics.value.clear()
    passedTests.value.clear()
    saveProgress()
  }
  
  // Экспорт прогресса
  const exportProgress = () => {
    return {
      completedTopics: [...completedTopics.value],
      passedTests: [...passedTests.value],
      exportDate: new Date().toISOString()
    }
  }
  
  // Импорт прогресса
  const importProgress = (data) => {
    try {
      if (data.completedTopics) {
        completedTopics.value = new Set(data.completedTopics)
      }
      if (data.passedTests) {
        passedTests.value = new Set(data.passedTests)
      }
      saveProgress()
      return true
    } catch (error) {
      console.error('Ошибка импорта прогресса:', error)
      return false
    }
  }
  
  // Инициализация
  loadProgress()
  
  return {
    completedTopics,
    passedTests,
    loadProgress,
    saveProgress,
    calculateCourseProgress,
    isTopicCompleted,
    markTopicAsCompleted,
    unmarkTopicAsCompleted,
    isTestPassed,
    markTestAsPassed,
    getLessonStats,
    clearProgress,
    exportProgress,
    importProgress
  }
}

