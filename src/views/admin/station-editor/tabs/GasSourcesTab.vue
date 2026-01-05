<template>
  <div>
    <div class="mb-4">
      <el-button
        type="primary"
        @click="showGasSourceDialog = true"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon> Добавить источник
      </el-button>
    </div>
    
    <el-table
      :data="gasSources"
      stripe
      border
    >
      <el-table-column
        prop="source_name"
        label="Название источника"
        min-width="300"
      />
      <el-table-column
        label="Действия"
        width="150"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            size="small"
            @click="editGasSource(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить источник?"
            @confirm="deleteGasSource(row)"
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

    <GasSourceDialog />
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import GasSourceDialog from '../dialogs/GasSourceDialog.vue'

const {
  gasSources,
  showGasSourceDialog,
  editGasSource,
  deleteGasSource
} = useStationEditorContext()
</script>

