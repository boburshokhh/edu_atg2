<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Управление станциями</h1>
      <el-button type="primary" @click="$router.push('/admin/stations/new')">
        <el-icon class="mr-2"><Plus /></el-icon>
        Добавить станцию
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="stations" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Название" min-width="200" />
        <el-table-column prop="short_name" label="Код" width="120" />
        <el-table-column prop="type" label="Тип" width="180" />
        <el-table-column prop="status" label="Статус" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? 'Активен' : 'Неактивен' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Действия" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/admin/stations/${row.id}`)">
              Редактировать
            </el-button>
            <el-popconfirm
              title="Вы уверены, что хотите удалить эту станцию?"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button size="small" type="danger">Удалить</el-button>
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
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

const stations = ref([])
const loading = ref(false)

const loadStations = async () => {
  loading.value = true
  try {
    stations.value = await stationService.getStations()
  } catch (error) {
    ElMessage.error('Ошибка при загрузке станций: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await stationService.deleteStation(row.id)
    ElMessage.success('Станция удалена')
    loadStations()
  } catch (error) {
    ElMessage.error('Ошибка при удалении: ' + error.message)
  }
}

onMounted(() => {
  loadStations()
})
</script>

