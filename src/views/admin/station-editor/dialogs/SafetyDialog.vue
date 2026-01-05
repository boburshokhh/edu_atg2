<template>
  <el-dialog
    v-model="showSafetyDialog"
    :title="editingSafetySystem ? 'Редактировать систему безопасности' : 'Добавить систему безопасности'"
    width="700px"
  >
    <el-form
      :model="safetyForm"
      label-width="150px"
    >
      <el-form-item
        label="Название"
        required
      >
        <el-input v-model="safetyForm.name" />
      </el-form-item>
      <el-form-item label="Описание">
        <el-input
          v-model="safetyForm.description"
          type="textarea"
          rows="3"
        />
      </el-form-item>
      <el-form-item label="Производитель">
        <el-input v-model="safetyForm.manufacturer" />
      </el-form-item>
      <el-form-item label="Особенности">
        <div
          v-for="(feature, idx) in safetyForm.features"
          :key="idx"
          class="mb-2 flex items-center"
        >
          <el-input
            v-model="safetyForm.features[idx]"
            class="flex-1 mr-2"
          />
          <el-button
            type="danger"
            link
            @click="safetyForm.features.splice(idx, 1)"
          >
            Удалить
          </el-button>
        </div>
        <el-button
          size="small"
          @click="safetyForm.features.push('')"
        >
          + Добавить особенность
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showSafetyDialog = false">
        Отмена
      </el-button>
      <el-button
        type="primary"
        @click="saveSafetySystem"
      >
        Сохранить
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useStationEditorContext } from '../context'

const {
  showSafetyDialog,
  editingSafetySystem,
  safetyForm,
  saveSafetySystem
} = useStationEditorContext()
</script>

