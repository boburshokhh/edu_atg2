// Supabase removed - service disabled

class VideoService {
  // Загрузка видео
  async uploadVideo(file, lessonId) {
    try {
      // Supabase removed - service disabled
      return { success: false, error: 'Video upload disabled - Supabase removed' }
    } catch (error) {
      console.error('Error uploading video:', error)
      return { success: false, error: error.message }
    }
  }

  // Получение URL видео по ID урока
  async getVideoUrl(lessonId) {
    try {
      // Supabase removed - service disabled
      return { success: false, error: 'Video service disabled - Supabase removed' }
    } catch (error) {
      console.error('Error getting video URL:', error)
      return { success: false, error: error.message }
    }
  }

  // Сохранение прогресса просмотра видео
  async saveProgress(userId, lessonId, progress) {
    try {
      // Supabase removed - service disabled
      return { success: false, error: 'Progress save disabled - Supabase removed' }
    } catch (error) {
      console.error('Error saving progress:', error)
      return { success: false, error: error.message }
    }
  }

  // Отметить урок как завершенный
  async completeLesson(userId, lessonId) {
    try {
      // Supabase removed - service disabled
      return { success: false, error: 'Lesson completion disabled - Supabase removed' }
    } catch (error) {
      console.error('Error completing lesson:', error)
      return { success: false, error: error.message }
    }
  }

  // Получить прогресс урока
  async getLessonProgress(userId, lessonId) {
    try {
      // Supabase removed - return zero progress
      return { success: true, progress: 0 }
    } catch (error) {
      console.error('Error getting lesson progress:', error)
      return { success: false, error: error.message }
    }
  }
}

const videoService = new VideoService()
export default videoService
