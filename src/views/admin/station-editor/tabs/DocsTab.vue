<template>
  <div>
    <div class="mb-4">
      <input
        ref="docInput"
        type="file"
        class="hidden"
        @change="handleDocUpload"
      >
      <el-button
        type="primary"
        :loading="uploadingDoc"
        @click="$refs.docInput.click()"
      >
        <el-icon class="mr-2">
          <DocumentAdd />
        </el-icon> Загрузить документ
      </el-button>
    </div>
    <el-table
      :data="docs"
      stripe
      border
    >
      <el-table-column
        prop="title"
        label="Название"
        min-width="200"
      />
      <el-table-column label="Файл">
        <template #default="{ row }">
          <a
            :href="row.downloadUrl || row.file_url"
            target="_blank"
            class="text-blue-600 hover:underline"
          >Скачать</a>
        </template>
      </el-table-column>
      <el-table-column
        label="Действия"
        width="120"
      >
        <template #default="{ row }">
          <el-popconfirm
            title="Удалить документ?"
            @confirm="deleteDoc(row)"
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
  </div>
</template>

<script setup>
import { DocumentAdd } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'

const {
  docs,
  uploadingDoc,
  handleDocUpload,
  deleteDoc
} = useStationEditorContext()
</script>

