<template>
  <el-dialog
    v-model="showSpecDialog"
    :title="editingSpec ? 'Редактировать характеристику' : 'Добавить характеристику'"
    width="600px"
  >
    <el-form
      :model="specForm"
      label-width="150px"
    >
      <el-form-item
        label="Категория"
        required
      >
        <el-input v-model="specForm.category" />
      </el-form-item>
      <el-form-item label="Значение">
        <el-input v-model="specForm.value" />
      </el-form-item>
      <el-form-item label="Единица измерения">
        <el-input v-model="specForm.unit" />
      </el-form-item>
      <el-form-item label="Описание">
        <el-input
          v-model="specForm.description"
          type="textarea"
          rows="3"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showSpecDialog = false">
        Отмена
      </el-button>
      <el-button
        type="primary"
        @click="saveSpec"
      >
        Сохранить
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useStationEditorContext } from '../context'

const {
  showSpecDialog,
  editingSpec,
  specForm,
  saveSpec
} = useStationEditorContext()
</script>

