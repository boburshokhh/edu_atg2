<template>
  <div>
    <div class="mb-4">
      <el-button
        type="primary"
        @click="showSafetyDialog = true"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon> Добавить систему безопасности
      </el-button>
    </div>
    
    <el-table
      :data="safetySystems"
      stripe
      border
    >
      <el-table-column
        prop="name"
        label="Название"
        min-width="200"
      />
      <el-table-column
        prop="description"
        label="Описание"
        min-width="250"
        show-overflow-tooltip
      />
      <el-table-column
        prop="manufacturer"
        label="Производитель"
        width="150"
      />
      <el-table-column
        label="Особенности"
        min-width="200"
      >
        <template #default="{ row }">
          <el-tag
            v-for="(feature, idx) in (row.feature_names || row.features || [])"
            :key="idx"
            class="mr-1 mb-1"
            size="small"
          >
            {{ typeof feature === 'string' ? feature : feature.feature_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        label="Действия"
        width="150"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            size="small"
            @click="editSafetySystem(row)"
          >
            Редактировать
          </el-button>
          <el-popconfirm
            title="Удалить систему?"
            @confirm="deleteSafetySystem(row)"
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

    <SafetyDialog />
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { useStationEditorContext } from '../context'
import SafetyDialog from '../dialogs/SafetyDialog.vue'

const {
  safetySystems,
  showSafetyDialog,
  editSafetySystem,
  deleteSafetySystem
} = useStationEditorContext()
</script>

