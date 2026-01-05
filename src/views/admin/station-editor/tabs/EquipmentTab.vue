<template>
  <div>
    <div class="mb-4">
      <el-button
        type="primary"
        @click="showEquipmentDialog = true"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon> Добавить оборудование
      </el-button>
    </div>
    
    <el-table
      :data="equipment"
      stripe
      border
    >
      <el-table-column
        prop="name"
        label="Название"
        min-width="200"
      />
      <el-table-column
        prop="model"
        label="Модель"
        width="150"
      />
      <el-table-column
        prop="manufacturer"
        label="Производитель"
        width="180"
      />
      <el-table-column
        prop="quantity"
        label="Количество"
        width="100"
        align="center"
      />
      <el-table-column
        prop="power"
        label="Мощность"
        width="150"
      />
      <el-table-column
        prop="description"
        label="Описание"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column
        label="Действия"
        width="150"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            size="small"
            @click="editEquipment(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить оборудование?"
            @confirm="deleteEquipment(row)"
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

    <EquipmentDialog />
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import EquipmentDialog from '../dialogs/EquipmentDialog.vue'

const {
  equipment,
  showEquipmentDialog,
  editEquipment,
  deleteEquipment
} = useStationEditorContext()
</script>

