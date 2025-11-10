import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://fusartgifhigtysskgfg.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1c2FydGdpZmhpZ3R5c3NrZ2ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMjQ1NzgsImV4cCI6MjA3NjgwMDU3OH0.l_xGpHpf4FuRmgG_Cz84lub8CLQCm-nMKGPn76CrddE'

const supabase = createClient(supabaseUrl, supabaseKey)

class VideoService {
  // Загрузка видео в Supabase Storage
  async uploadVideo(file, lessonId) {
    try {
      const fileExt = file.name.split('.').pop()
      const fileName = `lesson-${lessonId}-${Date.now()}.${fileExt}`
      const filePath = `videos/${fileName}`

      // Загружаем файл
      const { error: uploadError } = await supabase.storage
        .from('videos')
        .upload(filePath, file)

      if (uploadError) throw uploadError

      // Получаем публичный URL
      const { data: { publicUrl } } = supabase.storage
        .from('videos')
        .getPublicUrl(filePath)

      return { success: true, url: publicUrl }
    } catch (error) {
      console.error('Error uploading video:', error)
      return { success: false, error: error.message }
    }
  }

  // Получение URL видео по ID урока
  async getVideoUrl(lessonId) {
    try {
      // Получаем информацию о видео из базы данных
      const { data, error } = await supabase
        .from('lessons') // Предполагается таблица lessons
        .select('video_url')
        .eq('id', lessonId)
        .single()

      if (error) throw error
      return { success: true, url: data?.video_url }
    } catch (error) {
      console.error('Error getting video URL:', error)
      return { success: false, error: error.message }
    }
  }

  // Сохранение прогресса просмотра видео
  async saveProgress(userId, lessonId, progress) {
    try {
      const { error } = await supabase
        .from('user_courses')
        .upsert({
          user_id: userId,
          course_id: lessonId, // или другой ID курса
          progress_percent: progress,
          last_activity: new Date().toISOString()
        })

      if (error) throw error
      return { success: true }
    } catch (error) {
      console.error('Error saving progress:', error)
      return { success: false, error: error.message }
    }
  }

  // Отметить урок как завершенный
  async completeLesson(userId, lessonId) {
    try {
      const { error } = await supabase
        .from('user_courses')
        .update({ 
          progress_percent: 100,
          status: 'completed',
          completed_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .eq('course_id', lessonId)

      if (error) throw error
      return { success: true }
    } catch (error) {
      console.error('Error completing lesson:', error)
      return { success: false, error: error.message }
    }
  }

  // Получить прогресс урока
  async getLessonProgress(userId, lessonId) {
    try {
      const { data, error } = await supabase
        .from('user_courses')
        .select('progress_percent, status, last_activity')
        .eq('user_id', userId)
        .eq('course_id', lessonId)
        .single()

      if (error && error.code !== 'PGRST116') throw error
      return { success: true, progress: data?.progress_percent || 0 }
    } catch (error) {
      console.error('Error getting lesson progress:', error)
      return { success: false, error: error.message }
    }
  }
}

const videoService = new VideoService()
export default videoService


