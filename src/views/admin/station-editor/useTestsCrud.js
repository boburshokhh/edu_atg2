import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import testService from '@/services/testService'

export function useTestsCrud(courseProgram, loadCourseProgram) {
  const route = useRoute()
  const loadingTests = ref(false)
  const tests = ref([])
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

  const loadTests = async () => {
    if (!courseProgram.value?.id) {
      tests.value = []
      return
    }

    loadingTests.value = true
    try {
      const allTests = await testService.getTests('final')
      // Filter tests for this course program
      tests.value = allTests.filter(t => t.course_program_id === courseProgram.value.id)
    } catch (error) {
      ElMessage.error('Ошибка загрузки тестов: ' + error.message)
    } finally {
      loadingTests.value = false
    }
  }

  const openTestDialog = (test = null) => {
    editingTest.value = test
    if (test && test.id) {
      // Load full test with questions
      loadTestDetails(test.id)
    } else {
      testForm.value = {
        title: '',
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
      const test = await testService.getTest(testId, 'final')
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

    if (!courseProgram.value?.id) {
      ElMessage.warning('Сначала сохраните программу курса')
      return
    }

    savingTest.value = true
    try {
      if (editingTest.value) {
        await testService.updateTest(editingTest.value.id, 'final', {
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
          test_type: 'final',
          course_program_id: courseProgram.value.id,
          title: testForm.value.title,
          description: testForm.value.description,
          passing_score: testForm.value.passing_score,
          time_limit: testForm.value.time_limit,
          attempts: testForm.value.attempts,
          is_active: testForm.value.is_active
        })
        // Update editingTest with the created test
        editingTest.value = { id: result.id, ...result }
        // Reload test details to get full info
        await loadTestDetails(result.id)
        ElMessage.success('Тест создан. Теперь вы можете добавить вопросы.')
        // Switch to questions tab after a short delay
        setTimeout(() => {
          testDialogTab.value = 'questions'
        }, 100)
      }
      await loadTests()
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
      await testService.updateTestQuestions(testId, 'final', questions)
      ElMessage.success('Вопросы сохранены')
      await loadTests()
      // Reload test details
      if (editingTest.value && editingTest.value.id === testId) {
        await loadTestDetails(testId)
      }
    } catch (error) {
      ElMessage.error('Ошибка сохранения вопросов: ' + error.message)
    } finally {
      savingQuestions.value = false
    }
  }

  const deleteTest = async (test) => {
    try {
      await testService.deleteTest(test.id, 'final')
      ElMessage.success('Тест удален')
      await loadTests()
    } catch (error) {
      ElMessage.error('Ошибка удаления теста: ' + error.message)
    }
  }

  return {
    loadingTests,
    tests,
    showTestDialog,
    editingTest,
    savingTest,
    savingQuestions,
    testForm,
    testDialogTab,
    loadTests,
    openTestDialog,
    saveTest,
    saveTestQuestions,
    deleteTest
  }
}

