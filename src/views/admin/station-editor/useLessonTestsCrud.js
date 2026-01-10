import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

export function useLessonTestsCrud(lesson, saveCourseProgram) {
  const loadingTest = ref(false)
  const showTestDialog = ref(false)
  const editingTest = ref(null)
  const savingTest = ref(false)
  const savingQuestions = ref(false)
  const testDialogTab = ref('settings')

  const testForm = ref({
    title: '',
    description: '',
    passing_score: 70,
    time_limit: 30,
    attempts: null,
    is_active: true
  })

  const loadLessonTest = async () => {
    if (!lesson.value?.id) {
      return null
    }

    loadingTest.value = true
    try {
      const allTests = await testService.getTests('lesson')
      // Find test for this lesson
      const lessonTest = allTests.find(t => t.course_program_lesson_id === lesson.value.id)
      return lessonTest || null
    } catch (error) {
      ElMessage.error('Ошибка загрузки теста урока: ' + error.message)
      return null
    } finally {
      loadingTest.value = false
    }
  }

  const openTestDialog = async (test = null) => {
    editingTest.value = test
    if (test && test.test_id) {
      // Load full test with questions
      await loadTestDetails(test.test_id)
    } else {
      testForm.value = {
        title: lesson.value?.test?.title || `Тест к уроку: ${lesson.value?.title || ''}`,
        description: '',
        passing_score: 70,
        time_limit: 30,
        attempts: null,
        is_active: true,
        questions: []
      }
      showTestDialog.value = true
    }
  }

  const loadTestDetails = async (testId) => {
    try {
      const test = await testService.getTest(testId, 'lesson')
      testForm.value = {
        title: test.title || '',
        description: test.description || '',
        passing_score: test.passing_score || 70,
        time_limit: test.time_limit || 30,
        attempts: test.attempts,
        is_active: test.is_active !== undefined ? test.is_active : true
      }
      // Store questions for later
      testForm.value.questions = test.questions || []
      showTestDialog.value = true
    } catch (error) {
      ElMessage.error('Ошибка загрузки теста: ' + error.message)
    }
  }

  const saveTest = async () => {
    if (!testForm.value.title) {
      ElMessage.warning('Введите название теста')
      return
    }

    if (!lesson.value?.id) {
      ElMessage.warning('Сначала сохраните урок')
      return
    }

    savingTest.value = true
    try {
      if (editingTest.value && editingTest.value.test_id) {
        await testService.updateTest(editingTest.value.test_id, 'lesson', {
          title: testForm.value.title,
          description: testForm.value.description,
          passing_score: testForm.value.passing_score,
          time_limit: testForm.value.time_limit,
          attempts: testForm.value.attempts,
          is_active: testForm.value.is_active
        })
        ElMessage.success('Тест обновлен')
      } else {
        const result = await testService.createTest({
          test_type: 'lesson',
          lesson_id: lesson.value.id,
          title: testForm.value.title,
          description: testForm.value.description,
          passing_score: testForm.value.passing_score,
          time_limit: testForm.value.time_limit,
          attempts: testForm.value.attempts,
          is_active: testForm.value.is_active
        })
        // Update editingTest with the created test
        editingTest.value = { test_id: result.id, ...result }
        // Reload test details to get full info
        await loadTestDetails(result.id)
        ElMessage.success('Тест создан. Теперь вы можете добавить вопросы.')
        // Switch to questions tab after a short delay
        setTimeout(() => {
          testDialogTab.value = 'questions'
        }, 100)
      }
      // Reload course program to update lesson.test data
      if (saveCourseProgram) {
        await saveCourseProgram()
      }
      showTestDialog.value = false
    } catch (error) {
      ElMessage.error('Ошибка сохранения теста: ' + error.message)
    } finally {
      savingTest.value = false
    }
  }

  const saveTestQuestions = async (testId, questions) => {
    savingQuestions.value = true
    try {
      await testService.updateTestQuestions(testId, 'lesson', questions)
      ElMessage.success('Вопросы сохранены')
      // Reload test details
      if (editingTest.value && editingTest.value.test_id === testId) {
        await loadTestDetails(testId)
      }
      // Reload course program to update lesson.test data
      if (saveCourseProgram) {
        await saveCourseProgram()
      }
    } catch (error) {
      ElMessage.error('Ошибка сохранения вопросов: ' + error.message)
    } finally {
      savingQuestions.value = false
    }
  }

  const deleteTest = async (test) => {
    try {
      await testService.deleteTest(test.test_id, 'lesson')
      ElMessage.success('Тест удален')
      // Reload course program to update lesson.test data
      if (saveCourseProgram) {
        await saveCourseProgram()
      }
    } catch (error) {
      ElMessage.error('Ошибка удаления теста: ' + error.message)
    }
  }

  return {
    loadingTest,
    showTestDialog,
    editingTest,
    savingTest,
    savingQuestions,
    testForm,
    testDialogTab,
    loadLessonTest,
    openTestDialog,
    saveTest,
    saveTestQuestions,
    deleteTest
  }
}

