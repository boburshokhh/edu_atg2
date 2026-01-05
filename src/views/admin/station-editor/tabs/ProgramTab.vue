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
        </div>
      </el-collapse-item>
    </el-collapse>

    <TopicFilesDialog />
  </div>
</template>

<script setup>
import { Upload, Plus } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import TopicFilesDialog from '../dialogs/TopicFilesDialog.vue'

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
  handlePromoVideoUpload,
  deletePromoVideo
} = useStationEditorContext()
</script>

