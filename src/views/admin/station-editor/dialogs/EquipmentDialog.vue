<template>
  <el-dialog
    v-model="showEquipmentDialog"
    :title="editingEquipment ? 'Редактировать оборудование' : 'Добавить оборудование'"
    width="600px"
  >
    <el-form
      :model="equipmentForm"
      label-width="150px"
    >
      <el-form-item
        label="Название"
        required
      >
        <el-input v-model="equipmentForm.name" />
      </el-form-item>
      <el-form-item label="Модель">
        <el-input v-model="equipmentForm.model" />
      </el-form-item>
      <el-form-item label="Производитель">
        <el-input v-model="equipmentForm.manufacturer" />
      </el-form-item>
      <el-form-item label="Количество">
        <el-input-number
          v-model="equipmentForm.quantity"
          :min="1"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="Мощность">
        <el-input v-model="equipmentForm.power" />
      </el-form-item>
      <el-form-item label="Описание">
        <el-input
          v-model="equipmentForm.description"
          type="textarea"
          rows="3"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showEquipmentDialog = false">
        Отмена
      </el-button>
      <el-button
        type="primary"
        @click="saveEquipment"
      >
        Сохранить
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useStationEditorContext } from '../context'

const {
  showEquipmentDialog,
  editingEquipment,
  equipmentForm,
  saveEquipment
} = useStationEditorContext()
</script>

