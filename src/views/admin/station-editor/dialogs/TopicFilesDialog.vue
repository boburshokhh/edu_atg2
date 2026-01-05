<template>
  <el-dialog
    v-model="showTopicFilesDialog"
    title="Файлы темы"
    width="900px"
  >
    <div v-if="activeTopic">
      <div class="mb-3 text-sm text-gray-600">
        <div><span class="font-semibold">Тема:</span> {{ activeTopic.code }} — {{ activeTopic.title }}</div>
        <div class="text-xs text-gray-500">
          topic_id: {{ activeTopic.id }} | topicKey: {{ activeTopic.topicKey }}
        </div>
      </div>

      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <el-select
            v-model="newTopicFileType"
            placeholder="Тип"
            style="width: 180px"
          >
            <el-option
              label="PDF"
              value="pdf"
            />
            <el-option
              label="Видео"
              value="video"
            />
            <el-option
              label="Документ"
              value="document"
            />
          </el-select>
          <el-checkbox
            v-model="newTopicFileIsMain"
          >
            Основной материал
          </el-checkbox>
        </div>
        <div class="flex gap-2">
          <input
            ref="topicFileInput"
            type="file"
            class="hidden"
            @change="handleTopicFileUpload"
          >
          <el-button
            type="primary"
            :loading="uploadingTopicFile"
            @click="$refs.topicFileInput.click()"
          >
            <el-icon class="mr-2">
              <Upload />
            </el-icon> Загрузить файл
          </el-button>
        </div>
      </div>

      <el-table
        :data="topicFiles"
        stripe
        border
      >
        <el-table-column
          prop="fileType"
          label="Тип"
          width="110"
        />
        <el-table-column
          prop="isMain"
          label="Основной"
          width="120"
        >
          <template #default="{ row }">
            <el-switch
              v-model="row.isMain"
              @change="() => updateTopicFile(row, { isMain: row.isMain })"
            />
          </template>
        </el-table-column>
        <el-table-column
          label="Название"
          min-width="240"
        >
          <template #default="{ row }">
            <el-input
              v-model="row.title"
              @change="() => updateTopicFile(row, { title: row.title })"
            />
          </template>
        </el-table-column>
        <el-table-column
          label="Order"
          width="120"
        >
          <template #default="{ row }">
            <el-input-number
              v-model="row.orderIndex"
              :min="0"
              style="width: 100%"
              @change="() => updateTopicFile(row, { orderIndex: row.orderIndex })"
            />
          </template>
        </el-table-column>
        <el-table-column
          label="Preview"
          width="140"
        >
          <template #default="{ row }">
            <el-button
              size="small"
              @click="previewTopicFile(row)"
            >
              Открыть
            </el-button>
          </template>
        </el-table-column>
        <el-table-column
          label="Действия"
          width="140"
          fixed="right"
        >
          <template #default="{ row }">
            <el-popconfirm
              title="Удалить файл?"
              @confirm="deleteTopicFile(row)"
            >
              <template #reference>
                <el-button
                  size="small"
                  type="danger"
                >
                  Удалить
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <el-button @click="showTopicFilesDialog = false">
        Закрыть
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { Upload } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'

const {
  showTopicFilesDialog,
  activeTopic,
  topicFiles,
  uploadingTopicFile,
  newTopicFileType,
  newTopicFileIsMain,
  handleTopicFileUpload,
  updateTopicFile,
  deleteTopicFile,
  previewTopicFile
} = useStationEditorContext()
</script>

