import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'
import minioService from '@/services/minioService'

const genStableKey = (prefix) => {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return `${prefix}_${crypto.randomUUID()}`
    }
  } catch {}
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

const normalizeCourseProgram = (p) => {
  const program = p || {}
  return {
    id: program.id || null,
    title: program.title || '',
    description: program.description || '',
    duration: program.duration || '',
    format: program.format || 'Онлайн',
    isActive: program.isActive !== undefined ? !!program.isActive : true,
    orderIndex: program.orderIndex || 0,
    learningOutcomes: Array.isArray(program.learningOutcomes) ? program.learningOutcomes : [],
    requirements: Array.isArray(program.requirements) ? program.requirements : [],
    targetAudience: Array.isArray(program.targetAudience) ? program.targetAudience : [],
    lessons: Array.isArray(program.lessons)
      ? program.lessons.map(l => ({
          id: l.id || null,
          lessonKey: l.lessonKey || l.lesson_key || genStableKey('lesson'),
          title: l.title || '',
          duration: l.duration || '',
          orderIndex: l.orderIndex ?? l.order_index ?? 0,
          test: l.test ? {
            id: l.test.id || null,
            title: l.test.title || '',
            questionsCount: l.test.questionsCount ?? l.test.questions_count ?? 0,
            passingScore: l.test.passingScore ?? l.test.passing_score ?? 70,
            timeLimit: l.test.timeLimit ?? l.test.time_limit ?? 30,
            attempts: l.test.attempts || null
          } : null,
          topics: Array.isArray(l.topics)
            ? l.topics.map(t => ({
                id: t.id || null,
                topicKey: t.topicKey || t.topic_key || genStableKey('topic'),
                code: t.code || '',
                title: t.title || '',
                duration: t.duration || '',
                orderIndex: t.orderIndex ?? t.order_index ?? 0,
                files: Array.isArray(t.files) ? t.files : []
              }))
            : []
        }))
      : []
  }
}

export function useCourseProgram(station, isEditing) {
  const route = useRoute()
  const savingCourseProgram = ref(false)
  const courseProgram = ref({
    id: null,
    title: '',
    description: '',
    duration: '',
    format: 'Онлайн',
    isActive: true,
    orderIndex: 0,
    learningOutcomes: [],
    requirements: [],
    targetAudience: [],
    lessons: []
  })

  // Topic Files Dialog state
  const showTopicFilesDialog = ref(false)
  const activeTopic = ref(null)
  const topicFiles = ref([])
  const uploadingTopicFile = ref(false)
  const newTopicFileType = ref('pdf')
  const newTopicFileIsMain = ref(false)

  const loadCourseProgram = async () => {
    if (!isEditing.value) return
    try {
      const p = await stationService.getStationCourseProgram(route.params.id)
      if (p) {
        courseProgram.value = normalizeCourseProgram(p)
      } else {
        courseProgram.value = normalizeCourseProgram({
          title: station.value?.name ? `Программа онлайн-тренинга \"${station.value.name}\"` : 'Программа онлайн-тренинга',
          format: 'Онлайн',
          isActive: true
        })
      }
    } catch (e) {
      console.error('[StationEditor] Failed to load course program:', e)
      courseProgram.value = normalizeCourseProgram(null)
    }
  }

  const addLesson = () => {
    courseProgram.value.lessons.push({
      id: null,
      lessonKey: genStableKey('lesson'),
      title: '',
      duration: '',
      orderIndex: courseProgram.value.lessons.length,
      topics: []
    })
  }

  const removeLesson = (lessonIdx) => {
    courseProgram.value.lessons.splice(lessonIdx, 1)
  }

  const addTopic = (lesson) => {
    if (!lesson.topics) lesson.topics = []
    lesson.topics.push({
      id: null,
      topicKey: genStableKey('topic'),
      code: '',
      title: '',
      duration: '',
      orderIndex: lesson.topics.length
    })
  }

  const openTopicFiles = async (topic) => {
    activeTopic.value = topic
    showTopicFilesDialog.value = true
    topicFiles.value = []
    newTopicFileType.value = 'pdf'
    newTopicFileIsMain.value = false

    if (!topic?.id) {
      ElMessage.warning('Сначала сохраните программу (чтобы темы получили ID).')
      return
    }

    try {
      const rows = await stationService.getCourseProgramTopicFiles(route.params.id, topic.id)
      topicFiles.value = rows.filter(f => f.isActive !== false)
    } catch (e) {
      ElMessage.error('Ошибка загрузки файлов темы: ' + (e?.message || e))
    }
  }

  const handleTopicFileUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!activeTopic.value?.id) {
      ElMessage.warning('Тема не сохранена')
      event.target.value = ''
      return
    }

    uploadingTopicFile.value = true
    try {
      // Логирование для анализа "_outline" в названиях файлов при загрузке
      if (file.name && (file.name.toLowerCase().includes('outline') || file.name.toLowerCase().includes('_outline'))) {
        console.warn('[useCourseProgram] Uploading file with "_outline" in name:', {
          fileName: file.name,
          fileSize: file.size,
          fileType: file.type,
          topicId: activeTopic.value.id,
          topicKey: activeTopic.value.topicKey
        })
      }

      const folder = `stations/${station.value.id}/course_program/topics/${activeTopic.value.topicKey || activeTopic.value.id}`
      const objectKey = await stationService.uploadFile(file, folder)

      const fileType = newTopicFileType.value
      const isMain = !!newTopicFileIsMain.value

      const resp = await stationService.createCourseProgramTopicFile(route.params.id, activeTopic.value.id, {
        title: file.name,
        originalName: file.name,
        objectKey,
        fileType,
        isMain,
        orderIndex: topicFiles.value.length,
        fileSize: file.size,
        mimeType: file.type || null,
      })

      const created = resp?.data
      if (created) {
        const allFiles = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
        topicFiles.value = allFiles.filter(f => f.isActive !== false)
        activeTopic.value.files = topicFiles.value
      }
      ElMessage.success('Файл добавлен')
    } catch (e) {
      ElMessage.error('Ошибка загрузки файла: ' + (e?.message || e))
    } finally {
      uploadingTopicFile.value = false
      event.target.value = ''
    }
  }

  const updateTopicFile = async (row, patch) => {
    if (!activeTopic.value?.id) return
    try {
      await stationService.updateCourseProgramTopicFile(route.params.id, activeTopic.value.id, row.id, patch)
      const allFiles = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
      topicFiles.value = allFiles.filter(f => f.isActive !== false)
      activeTopic.value.files = topicFiles.value
    } catch (e) {
      ElMessage.error('Ошибка обновления: ' + (e?.message || e))
    }
  }

  const deleteTopicFile = async (row) => {
    if (!activeTopic.value?.id) return
    try {
      await stationService.deleteCourseProgramTopicFile(route.params.id, activeTopic.value.id, row.id, { deleteObject: false })
      const allFiles = await stationService.getCourseProgramTopicFiles(route.params.id, activeTopic.value.id)
      topicFiles.value = allFiles.filter(f => f.isActive !== false)
      activeTopic.value.files = topicFiles.value
      ElMessage.success('Удалено')
    } catch (e) {
      ElMessage.error('Ошибка удаления: ' + (e?.message || e))
    }
  }

  const previewTopicFile = async (row) => {
    try {
      const url = await minioService.getPresignedDownloadUrl(row.objectKey, 7 * 24 * 60 * 60, row.mimeType || null)
      window.open(url, '_blank')
    } catch (e) {
      ElMessage.error('Не удалось открыть файл: ' + (e?.message || e))
    }
  }

  const saveCourseProgram = async () => {
    if (!isEditing.value) return
    savingCourseProgram.value = true
    try {
      const payload = {
        id: courseProgram.value.id,
        title: courseProgram.value.title,
        description: courseProgram.value.description,
        duration: courseProgram.value.duration,
        format: courseProgram.value.format,
        isActive: courseProgram.value.isActive,
        orderIndex: courseProgram.value.orderIndex || 0,
        learningOutcomes: (courseProgram.value.learningOutcomes || []).filter(x => String(x || '').trim()),
        requirements: (courseProgram.value.requirements || []).filter(x => String(x || '').trim()),
        targetAudience: (courseProgram.value.targetAudience || []).filter(x => String(x || '').trim()),
        lessons: (courseProgram.value.lessons || []).map(l => ({
          lessonKey: l.lessonKey,
          title: l.title,
          duration: l.duration || null,
          orderIndex: l.orderIndex || 0,
          isActive: true,
          topics: (l.topics || []).map(t => ({
            topicKey: t.topicKey,
            code: t.code || null,
            title: t.title,
            duration: t.duration || null,
            orderIndex: t.orderIndex || 0,
            isActive: true
          }))
        }))
      }

      const resp = await stationService.updateStationCourseProgram(route.params.id, payload)
      courseProgram.value = normalizeCourseProgram(resp?.courseProgram)
      ElMessage.success('Программа обучения сохранена')
    } catch (e) {
      ElMessage.error('Ошибка сохранения программы: ' + (e?.message || e))
    } finally {
      savingCourseProgram.value = false
    }
  }

  return {
    courseProgram,
    savingCourseProgram,
    loadCourseProgram,
    saveCourseProgram,
    addLesson,
    removeLesson,
    addTopic,
    // Topic Files Dialog
    showTopicFilesDialog,
    activeTopic,
    topicFiles,
    uploadingTopicFile,
    newTopicFileType,
    newTopicFileIsMain,
    openTopicFiles,
    handleTopicFileUpload,
    updateTopicFile,
    deleteTopicFile,
    previewTopicFile
  }
}

