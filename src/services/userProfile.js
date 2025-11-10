import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://fusartgifhigtysskgfg.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ1c2FydGdpZmhpZ3R5c3NrZ2ZnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyMjQ1NzgsImV4cCI6MjA3NjgwMDU3OH0.l_xGpHpf4FuRmgG_Cz84lub8CLQCm-nMKGPn76CrddE'

const supabase = createClient(supabaseUrl, supabaseKey)

class UserProfileService {
  // Получение профиля пользователя
  async getProfile(userId) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error && error.code !== 'PGRST116') { // PGRST116 = not found
        throw error
      }

      return { success: true, data: data || {} }
    } catch (error) {
      console.error('Error getting profile:', error)
      return { success: false, error: error.message }
    }
  }

  // Создание или обновление профиля
  async saveProfile(userId, profileData) {
    try {
      const profile = {
        id: userId,
        ...profileData,
        updated_at: new Date().toISOString()
      }

      const { data, error } = await supabase
        .from('user_profiles')
        .upsert(profile)
        .select()
        .single()

      if (error) throw error
      return { success: true, data }
    } catch (error) {
      console.error('Error saving profile:', error)
      return { success: false, error: error.message }
    }
  }

  // Загрузка аватара
  async uploadAvatar(userId, file) {
    try {
      const fileExt = file.name.split('.').pop()
      const fileName = `${userId}-${Date.now()}.${fileExt}`
      const filePath = `avatars/${fileName}`

      // Загружаем файл в storage (нужно создать bucket 'avatars' в Supabase)
      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(filePath, file)

      if (uploadError) {
        // Если bucket не существует, сохраняем как base64
        return this.saveAvatarAsBase64(userId, file)
      }

      // Получаем публичный URL
      const { data: { publicUrl } } = supabase.storage
        .from('avatars')
        .getPublicUrl(filePath)

      // Обновляем профиль
      const { error: updateError } = await supabase
        .from('user_profiles')
        .update({ avatar_url: publicUrl })
        .eq('id', userId)

      if (updateError) throw updateError

      return { success: true, url: publicUrl }
    } catch (error) {
      console.error('Error uploading avatar:', error)
      // Fallback: сохраняем как base64
      return this.saveAvatarAsBase64(userId, file)
    }
  }

  // Сохранение аватара как base64 (если storage не настроен)
  async saveAvatarAsBase64(userId, file) {
    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = async () => {
        const base64 = reader.result
        const result = await this.saveProfile(userId, { avatar_url: base64 })
        resolve(result)
      }
      reader.readAsDataURL(file)
    })
  }

  // Получение курсов пользователя
  async getUserCourses(userId) {
    try {
      const { data, error } = await supabase
        .from('user_courses')
        .select(`
          *,
          course:courses(*)
        `)
        .eq('user_id', userId)
        .order('last_activity', { ascending: false })

      if (error) throw error
      return { success: true, data: data || [] }
    } catch (error) {
      console.error('Error getting user courses:', error)
      return { success: false, error: error.message }
    }
  }

  // Добавление курса пользователю
  async enrollInCourse(userId, courseId) {
    try {
      const { data, error } = await supabase
        .from('user_courses')
        .insert({
          user_id: userId,
          course_id: courseId,
          status: 'in_progress',
          progress_percent: 0
        })
        .select()
        .single()

      if (error) throw error
      
      // Обновляем статистику
      await this.updateUserStats(userId)
      
      return { success: true, data }
    } catch (error) {
      console.error('Error enrolling in course:', error)
      return { success: false, error: error.message }
    }
  }

  // Обновление прогресса курса
  async updateCourseProgress(userId, courseId, progress) {
    try {
      const { data, error } = await supabase
        .from('user_courses')
        .update({
          progress_percent: progress,
          last_activity: new Date().toISOString(),
          ...(progress === 100 ? { 
            status: 'completed',
            completed_at: new Date().toISOString()
          } : {})
        })
        .eq('user_id', userId)
        .eq('course_id', courseId)
        .select()
        .single()

      if (error) throw error
      
      // Обновляем статистику
      await this.updateUserStats(userId)
      
      return { success: true, data }
    } catch (error) {
      console.error('Error updating course progress:', error)
      return { success: false, error: error.message }
    }
  }

  // Получение статистики пользователя
  async getUserStats(userId) {
    try {
      // Получаем или создаем статистику
      let { data: stats } = await supabase
        .from('user_stats')
        .select('*')
        .eq('user_id', userId)
        .single()

      if (!stats) {
        await this.updateUserStats(userId)
        stats = await supabase
          .from('user_stats')
          .select('*')
          .eq('user_id', userId)
          .single()
        stats = stats.data
      }

      return { success: true, data: stats || {} }
    } catch (error) {
      console.error('Error getting user stats:', error)
      return { success: false, error: error.message }
    }
  }

  // Обновление статистики пользователя
  async updateUserStats(userId) {
    try {
      // Подсчитываем статистику
      const { data: userCourses } = await supabase
        .from('user_courses')
        .select('*')
        .eq('user_id', userId)

      const courses = userCourses || []
      const activeCourses = courses.filter(c => c.status === 'in_progress').length
      const completedCourses = courses.filter(c => c.status === 'completed').length
      const totalHours = courses.reduce((sum, c) => sum + (c.hours_studied || 0), 0)

      const { data: certificates } = await supabase
        .from('certificates')
        .select('id')
        .eq('user_id', userId)

      const stats = {
        user_id: userId,
        active_courses: activeCourses,
        completed_courses: completedCourses,
        total_hours_studied: totalHours,
        certificates_count: certificates?.length || 0,
        last_updated: new Date().toISOString()
      }

      const { error } = await supabase
        .from('user_stats')
        .upsert(stats)

      if (error) throw error
      return { success: true }
    } catch (error) {
      console.error('Error updating user stats:', error)
      return { success: false, error: error.message }
    }
  }

  // Получение сертификатов
  async getCertificates(userId) {
    try {
      const { data, error } = await supabase
        .from('certificates')
        .select(`
          *,
          course:courses(*)
        `)
        .eq('user_id', userId)
        .order('issued_at', { ascending: false })

      if (error) throw error
      return { success: true, data: data || [] }
    } catch (error) {
      console.error('Error getting certificates:', error)
      return { success: false, error: error.message }
    }
  }
}

const userProfileService = new UserProfileService()
export default userProfileService

