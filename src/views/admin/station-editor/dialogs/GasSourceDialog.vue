<template>
  <el-dialog
    v-model="showGasSourceDialog"
    :title="editingGasSource ? 'Редактировать источник' : 'Добавить источник'"
    width="500px"
  >
    <el-form
      :model="gasSourceForm"
      label-width="150px"
    >
      <el-form-item
        label="Название источника"
        required
      >
        <el-input v-model="gasSourceForm.source_name" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showGasSourceDialog = false">
        Отмена
      </el-button>
      <el-button
        type="primary"
        @click="saveGasSource"
      >
        Сохранить
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useStationEditorContext } from '../context'

const {
  showGasSourceDialog,
  editingGasSource,
  gasSourceForm,
  saveGasSource
} = useStationEditorContext()
</script>

