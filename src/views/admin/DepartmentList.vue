<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-4">
        <el-button @click="$router.push('/admin')">
          <el-icon class="mr-2">
            <ArrowLeft />
          </el-icon>
          Назад
        </el-button>
        <h1 class="text-2xl font-bold text-gray-800">
          Управление отделами
        </h1>
      </div>
      <el-button
        type="primary"
        @click="$router.push('/admin/departments/new')"
      >
        <el-icon class="mr-2">
          <Plus />
        </el-icon>
        Добавить отдел
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table
        :data="departments"
        stripe
        style="width: 100%"
      >
        <el-table-column
          prop="id"
          label="ID"
          width="80"
        />
        <el-table-column
          label="Название (RU / EN)"
          min-width="300"
        >
          <template #default="{ row }">
            <div>
              <div class="font-semibold">{{ row.name_ru || row.name || '-' }}</div>
              <div class="text-sm text-gray-500">{{ row.name_en || '-' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="short_name"
          label="Код"
          width="120"
        />
        <el-table-column
          prop="status"
          label="Статус"
          width="120"
        >
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? 'Активен' : 'Неактивен' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="Действия"
          width="180"
          fixed="right"
        >
          <template #default="{ row }">
            <el-button
              size="small"
              @click="$router.push(`/admin/departments/${row.id}`)"
            >
              Редактировать
            </el-button>
            <el-popconfirm
              title="Вы уверены, что хотите удалить этот отдел?"
              @confirm="handleDelete(row)"
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import departmentService from '@/services/departmentService'

const departments = ref([])
const loading = ref(false)

const loadDepartments = async () => {
  loading.value = true
  try {
    departments.value = await departmentService.getDepartments()
  } catch (error) {
    ElMessage.error('Ошибка при загрузке отделов: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await departmentService.deleteDepartment(row.id)
    ElMessage.success('Отдел удален')
    loadDepartments()
  } catch (error) {
    ElMessage.error('Ошибка при удалении: ' + error.message)
  }
}

onMounted(() => {
  loadDepartments()
})
</script>

