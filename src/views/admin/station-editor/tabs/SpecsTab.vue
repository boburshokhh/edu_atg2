<template>
  <div>
    <div class="mb-4">
      <el-button
        type="primary"
        @click="showSpecDialog = true"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon> Добавить характеристику
      </el-button>
    </div>
    
    <el-table
      :data="specs"
      stripe
      border
    >
      <el-table-column
        prop="category"
        label="Категория"
        min-width="200"
      />
      <el-table-column
        prop="value"
        label="Значение"
        width="120"
      />
      <el-table-column
        prop="unit"
        label="Единица"
        width="100"
      />
      <el-table-column
        prop="description"
        label="Описание"
        min-width="250"
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
            @click="editSpec(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить характеристику?"
            @confirm="deleteSpec(row)"
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

    <SpecDialog />
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import SpecDialog from '../dialogs/SpecDialog.vue'

const {
  specs,
  showSpecDialog,
  editSpec,
  deleteSpec
} = useStationEditorContext()
</script>

