<template>
  <div class="max-w-5xl">
    <div class="flex items-center justify-between mb-4">
      <div class="text-xs text-gray-500">
        <span v-if="courseProgram.id">Program ID: {{ courseProgram.id }}</span>
        <span v-else>Программа еще не создана</span>
      </div>
      <el-button
        type="primary"
        :loading="savingCourseProgram"
        @click="saveCourseProgram"
      >
        Сохранить программу
      </el-button>
    </div>

    <el-form
      :model="courseProgram"
      label-width="200px"
    >
      <el-form-item
        label="Название"
        required
      >
        <el-input v-model="courseProgram.title" />
      </el-form-item>
      <el-form-item label="Описание">
        <el-input
          v-model="courseProgram.description"
          type="textarea"
          rows="4"
        />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Длительность">
            <el-input
              v-model="courseProgram.duration"
              placeholder="например: 10 академических часов"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Формат">
            <el-input
              v-model="courseProgram.format"
              placeholder="Онлайн"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Активна">
        <el-switch v-model="courseProgram.isActive" />
      </el-form-item>
    </el-form>

    <el-divider />

    <!-- Promo video -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-bold text-gray-800">
          Короткое видео о станции
        </h3>
        <div class="flex gap-2">
          <input
            ref="promoVideoInput"
            type="file"
            class="hidden"
            accept="video/*"
            @change="handlePromoVideoUpload"
          >
          <el-button
            type="primary"
            size="small"
            :loading="uploadingPromoVideo"
            @click="$refs.promoVideoInput.click()"
          >
            <el-icon class="mr-2">
              <Upload />
            </el-icon> Загрузить видео
          </el-button>
          <el-popconfirm
            title="Удалить видео?"
            @confirm="deletePromoVideo({ deleteObject: false })"
          >
            <template #reference>
              <el-button
                size="small"
                type="danger"
                :disabled="!promoVideo"
              >
                Удалить
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
      <div
        v-if="uploadingPromoVideo"
        class="mt-2"
      >
        <el-progress :percentage="promoVideoProgress" :stroke-width="8" />
      </div>

      <div
        v-if="promoVideoUrl"
        class="bg-gray-50 border border-gray-200 rounded-xl p-3"
      >
        <div class="text-sm text-gray-600 mb-2">
          <span class="font-semibold">Файл:</span> {{ promoVideo?.title || promoVideo?.objectKey }}
        </div>
        <video
          class="w-full rounded-lg bg-black"
          style="max-height: 260px;"
          :src="promoVideoUrl"
          controls
          playsinline
          preload="metadata"
          crossorigin="anonymous"
        />
        <div class="text-xs text-gray-500 mt-2">
          Видео проигрывается через presigned URL (Range requests), поэтому работает и на телефонах.
        </div>
      </div>
      <div
        v-else
        class="text-sm text-gray-500"
      >
        Видео не загружено.
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Learning outcomes -->
      <div>
        <h3 class="font-bold text-gray-800 mb-2">
          Что вы изучите
        </h3>
        <div
          v-for="(item, idx) in courseProgram.learningOutcomes"
          :key="`lo-${idx}`"
          class="flex gap-2 mb-2"
        >
          <el-input v-model="courseProgram.learningOutcomes[idx]" />
          <el-button
            type="danger"
            link
            @click="courseProgram.learningOutcomes.splice(idx, 1)"
          >
            Удалить
          </el-button>
        </div>
        <el-button
          size="small"
          @click="courseProgram.learningOutcomes.push('')"
        >
          + Добавить
        </el-button>
      </div>

      <!-- Requirements -->
      <div>
        <h3 class="font-bold text-gray-800 mb-2">
          Требования
        </h3>
        <div
          v-for="(item, idx) in courseProgram.requirements"
          :key="`req-${idx}`"
          class="flex gap-2 mb-2"
        >
          <el-input v-model="courseProgram.requirements[idx]" />
          <el-button
            type="danger"
            link
            @click="courseProgram.requirements.splice(idx, 1)"
          >
            Удалить
          </el-button>
        </div>
        <el-button
          size="small"
          @click="courseProgram.requirements.push('')"
        >
          + Добавить
        </el-button>
      </div>

      <!-- Target audience -->
      <div>
        <h3 class="font-bold text-gray-800 mb-2">
          Целевая аудитория
        </h3>
        <div
          v-for="(item, idx) in courseProgram.targetAudience"
          :key="`aud-${idx}`"
          class="flex gap-2 mb-2"
        >
          <el-input v-model="courseProgram.targetAudience[idx]" />
          <el-button
            type="danger"
            link
            @click="courseProgram.targetAudience.splice(idx, 1)"
          >
            Удалить
          </el-button>
        </div>
        <el-button
          size="small"
          @click="courseProgram.targetAudience.push('')"
        >
          + Добавить
        </el-button>
      </div>
    </div>

    <el-divider />

    <div class="flex items-center justify-between mb-3">
      <h3 class="text-lg font-bold text-gray-800">
        Уроки и темы
      </h3>
      <el-button
        type="primary"
        size="small"
        @click="addLesson"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon> Добавить урок
      </el-button>
    </div>

    <el-collapse accordion>
      <el-collapse-item
        v-for="(lesson, lessonIdx) in courseProgram.lessons"
        :key="lesson.lessonKey || lesson.id || lessonIdx"
        :name="lesson.lessonKey || lessonIdx"
      >
        <template #title>
          <div class="flex items-center gap-3">
            <span class="font-semibold">{{ lessonIdx + 1 }}.</span>
            <span class="font-semibold">{{ lesson.title || 'Новый урок' }}</span>
            <span
              v-if="lesson.lessonKey"
              class="text-xs text-gray-500"
            >key: {{ lesson.lessonKey }}</span>
          </div>
        </template>

        <div class="p-2">
          <el-form label-width="160px">
            <el-form-item label="Название урока">
              <el-input v-model="lesson.title" />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Длительность">
                  <el-input
                    v-model="lesson.duration"
                    placeholder="например: 2.5 часа"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Порядок">
                  <el-input-number
                    v-model="lesson.orderIndex"
                    :min="0"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <div class="flex items-center justify-between mb-2">
            <h4 class="font-semibold text-gray-700">
              Темы
            </h4>
            <div class="flex gap-2">
              <el-button
                size="small"
                @click="addTopic(lesson)"
              >
                <el-icon class="mr-1">
                  <Plus />
                </el-icon> Добавить тему
              </el-button>
              <el-popconfirm
                title="Удалить урок?"
                @confirm="removeLesson(lessonIdx)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить урок
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>

          <el-table
            :data="lesson.topics || []"
            stripe
            border
          >
            <el-table-column
              label="Key"
              min-width="220"
            >
              <template #default="{ row }">
                <span class="text-xs text-gray-500">{{ row.topicKey }}</span>
              </template>
            </el-table-column>
            <el-table-column
              label="Код"
              width="140"
            >
              <template #default="{ row }">
                <el-input v-model="row.code" />
              </template>
            </el-table-column>
            <el-table-column
              label="Название"
              min-width="240"
            >
              <template #default="{ row }">
                <el-input v-model="row.title" />
              </template>
            </el-table-column>
            <el-table-column
              label="Длительность"
              width="140"
            >
              <template #default="{ row }">
                <el-input v-model="row.duration" />
              </template>
            </el-table-column>
            <el-table-column
              label="Порядок"
              width="120"
            >
              <template #default="{ row }">
                <el-input-number
                  v-model="row.orderIndex"
                  :min="0"
                  style="width: 100%"
                />
              </template>
            </el-table-column>
            <el-table-column
              label="Файлы"
              width="140"
            >
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="openTopicFiles(row)"
                >
                  Файлы ({{ (row.files || []).length }})
                </el-button>
              </template>
            </el-table-column>
            <el-table-column
              label="Действия"
              width="120"
              fixed="right"
            >
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  link
                  @click="lesson.topics.splice($index, 1)"
                >
                  Удалить
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- Lesson Test Section -->
          <el-divider />
          <div class="flex items-center justify-between mb-3 mt-4">
            <h4 class="font-semibold text-gray-700">
              Тест урока
            </h4>
            <div class="flex gap-2">
              <el-button
                v-if="lesson.test && lesson.test.id"
                size="small"
                type="primary"
                @click="openLessonTestDialog(lesson, lessonIdx)"
              >
                <el-icon class="mr-1">
                  <Edit />
                </el-icon>
                Редактировать тест
              </el-button>
              <el-button
                v-else
                size="small"
                type="primary"
                @click="openLessonTestDialog(lesson, lessonIdx)"
              >
                <el-icon class="mr-1">
                  <Plus />
                </el-icon>
                Добавить тест
              </el-button>
              <el-popconfirm
                v-if="lesson.test && lesson.test.id"
                title="Удалить тест урока?"
                @confirm="deleteLessonTest(lesson, lessonIdx)"
              >
                <template #reference>
                  <el-button
                    size="small"
                    type="danger"
                  >
                    Удалить тест
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>

          <div
            v-if="lesson.test && lesson.test.id"
            class="p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-gray-900">{{ lesson.test.title }}</p>
                <p class="text-sm text-gray-600 mt-1">
                  Вопросов: {{ lesson.test.questionsCount || 0 }} | 
                  Проходной балл: {{ lesson.test.passingScore || 70 }}% | 
                  Время: {{ lesson.test.timeLimit || 30 }} мин
                </p>
              </div>
            </div>
          </div>
          <div
            v-else
            class="p-3 bg-gray-50 rounded-lg text-center text-gray-500 text-sm"
          >
            Тест для этого урока не создан
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <el-divider />

    <!-- Tests Section -->
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-lg font-bold text-gray-800">
        Тесты курса
      </h3>
      <el-button
        type="primary"
        size="small"
        :disabled="!courseProgram.id"
        @click="openTestDialog()"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon>
        Добавить тест
      </el-button>
    </div>

    <div
      v-if="!courseProgram.id"
      class="text-sm text-gray-500 mb-4"
    >
      Сначала сохраните программу курса, чтобы добавить тесты
    </div>

    <el-table
      v-else
      v-loading="loadingTests"
      :data="tests"
      stripe
      border
      class="mb-4"
    >
      <el-table-column
        prop="title"
        label="Название"
        min-width="200"
      />
      <el-table-column
        prop="description"
        label="Описание"
        min-width="250"
        show-overflow-tooltip
      />
      <el-table-column
        prop="questions_count"
        label="Вопросов"
        width="100"
        align="center"
      />
      <el-table-column
        prop="passing_score"
        label="Проходной балл"
        width="130"
        align="center"
      >
        <template #default="{ row }">
          {{ row.passing_score }}%
        </template>
      </el-table-column>
      <el-table-column
        prop="time_limit"
        label="Время (мин)"
        width="120"
        align="center"
      />
      <el-table-column
        prop="is_active"
        label="Статус"
        width="100"
        align="center"
      >
        <template #default="{ row }">
          <el-tag
            :type="row.is_active ? 'success' : 'info'"
            size="small"
          >
            {{ row.is_active ? 'Активен' : 'Неактивен' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="Действия"
        width="200"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="openTestDialog(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить тест?"
            @confirm="deleteTest(row)"
          >
            <template #reference>
              <el-button
                type="danger"
                size="small"
              >
                Удалить
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <TopicFilesDialog />
    
    <!-- Test Dialog -->
    <el-dialog
      v-model="showTestDialog"
      :title="editingTest ? 'Редактирование теста' : 'Создание теста'"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="testDialogTab">
        <el-tab-pane
          label="Настройки"
          name="settings"
        >
          <el-form
            :model="testForm"
            label-width="150px"
            class="mt-4"
          >
            <el-form-item
              label="Название"
              required
            >
              <el-input
                v-model="testForm.title"
                placeholder="Введите название теста"
              />
            </el-form-item>

            <el-form-item label="Описание">
              <el-input
                v-model="testForm.description"
                type="textarea"
                :rows="3"
                placeholder="Введите описание теста"
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Проходной балл (%)">
                  <el-input-number
                    v-model="testForm.passing_score"
                    :min="0"
                    :max="100"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Время (минут)">
                  <el-input-number
                    v-model="testForm.time_limit"
                    :min="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Попыток">
              <el-input-number
                v-model="testForm.attempts"
                :min="1"
                style="width: 100%"
                placeholder="Оставьте пустым для неограниченного"
              />
            </el-form-item>

            <el-form-item label="Статус">
              <el-switch
                v-model="testForm.is_active"
                active-text="Активен"
                inactive-text="Неактивен"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane
          v-if="editingTest"
          label="Вопросы"
          name="questions"
        >
          <TestQuestionsEditor
            :test-id="editingTest.id"
            test-type="final"
            :saving="savingQuestions"
            @save="(testId, questions) => saveTestQuestions(testId, questions)"
          />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showTestDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          :loading="savingTest"
          @click="saveTest"
        >
          {{ editingTest ? 'Сохранить' : 'Создать' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Lesson Test Dialog -->
    <el-dialog
      v-if="currentLessonTestContext"
      v-model="showLessonTestDialog"
      :title="currentLessonTestContext.editingTest ? 'Редактирование теста урока' : 'Создание теста урока'"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="currentLessonTestContext.testDialogTab">
        <el-tab-pane
          label="Настройки"
          name="settings"
        >
          <el-form
            :model="currentLessonTestContext.testForm"
            label-width="150px"
            class="mt-4"
          >
            <el-form-item
              label="Название"
              required
            >
              <el-input
                v-model="currentLessonTestContext.testForm.title"
                placeholder="Введите название теста"
              />
            </el-form-item>

            <el-form-item label="Описание">
              <el-input
                v-model="currentLessonTestContext.testForm.description"
                type="textarea"
                :rows="3"
                placeholder="Введите описание теста"
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Проходной балл (%)">
                  <el-input-number
                    v-model="currentLessonTestContext.testForm.passing_score"
                    :min="0"
                    :max="100"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Время (минут)">
                  <el-input-number
                    v-model="currentLessonTestContext.testForm.time_limit"
                    :min="1"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Попыток">
              <el-input-number
                v-model="currentLessonTestContext.testForm.attempts"
                :min="1"
                style="width: 100%"
                placeholder="Оставьте пустым для неограниченного"
              />
            </el-form-item>

            <el-form-item label="Статус">
              <el-switch
                v-model="currentLessonTestContext.testForm.is_active"
                active-text="Активен"
                inactive-text="Неактивен"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane
          v-if="currentLessonTestContext.editingTest && currentLessonTestContext.editingTest.test_id"
          label="Вопросы"
          name="questions"
        >
          <TestQuestionsEditor
            :test-id="currentLessonTestContext.editingTest.test_id"
            test-type="lesson"
            :saving="currentLessonTestContext.savingQuestions"
            @save="(testId, questions) => currentLessonTestContext.saveTestQuestions(testId, questions)"
          />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="showLessonTestDialog = false">
          Отмена
        </el-button>
        <el-button
          type="primary"
          :loading="currentLessonTestContext.savingTest"
          @click="currentLessonTestContext.saveTest()"
        >
          {{ currentLessonTestContext.editingTest ? 'Сохранить' : 'Создать' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Upload, Plus, Edit } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import TopicFilesDialog from '../dialogs/TopicFilesDialog.vue'
import { useTestsCrud } from '../useTestsCrud'
import { useLessonTestsCrud } from '../useLessonTestsCrud'
import TestQuestionsEditor from '../components/TestQuestionsEditor.vue'

const {
  courseProgram,
  savingCourseProgram,
  saveCourseProgram,
  addLesson,
  removeLesson,
  addTopic,
  openTopicFiles,
  promoVideo,
  promoVideoUrl,
  uploadingPromoVideo,
  promoVideoProgress,
  handlePromoVideoUpload,
  deletePromoVideo
} = useStationEditorContext()

const {
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
} = useTestsCrud(courseProgram, saveCourseProgram)

// Lesson tests management
const showLessonTestDialog = ref(false)
const currentLessonTestContext = ref(null)

const openLessonTestDialog = async (lesson, lessonIdx) => {
  // Create context for this lesson's test
  const lessonRef = ref(lesson)
  const lessonTestCrud = useLessonTestsCrud(lessonRef, saveCourseProgram)
  
  currentLessonTestContext.value = {
    lesson,
    lessonIdx,
    ...lessonTestCrud
  }
  
  // Open dialog with lesson test data
  const lessonTest = lesson.test ? { test_id: lesson.test.id } : null
  await lessonTestCrud.openTestDialog(lessonTest)
  showLessonTestDialog.value = true
}

const deleteLessonTest = async (lesson, lessonIdx) => {
  if (!lesson.test || !lesson.test.id) return
  
  const lessonRef = ref(lesson)
  const { deleteTest: deleteLessonTestInternal } = useLessonTestsCrud(lessonRef, saveCourseProgram)
  
  await deleteLessonTestInternal({ test_id: lesson.test.id })
}

// Watch for course program ID changes to load tests
watch(() => courseProgram.value?.id, (newId) => {
  if (newId) {
    loadTests()
  }
}, { immediate: true })

onMounted(() => {
  if (courseProgram.value?.id) {
    loadTests()
  }
})
</script>

