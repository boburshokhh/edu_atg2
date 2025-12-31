<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-6">
      <el-button
        class="mr-4"
        @click="$router.push('/admin')"
      >
        <el-icon class="mr-2">
          <ArrowLeft />
        </el-icon>
        Назад
      </el-button>
      <h1 class="text-2xl font-bold text-gray-800">
        {{ isEditing ? `Редактирование отдела: ${department.name || 'Загрузка...'}` : 'Новый отдел' }}
      </h1>
    </div>

    <el-tabs
      v-model="activeTab"
      v-loading="loading"
      class="bg-white p-6 rounded-lg shadow"
    >
      <!-- General Info -->
      <el-tab-pane
        label="Общая информация"
        name="general"
      >
        <el-form
          :model="department"
          label-width="200px"
          class="max-w-4xl"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                label="Название"
                required
              >
                <el-input v-model="department.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="Короткое название"
                required
              >
                <el-input v-model="department.short_name" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="Описание">
            <el-input
              v-model="department.description"
              type="textarea"
              rows="4"
            />
          </el-form-item>
          
          <el-form-item label="Статус">
            <el-select
              v-model="department.status"
              style="width: 100%"
            >
              <el-option
                label="Активен"
                value="active"
              />
              <el-option
                label="Неактивен"
                value="inactive"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="Основное изображение">
            <el-input
              v-model="department.image"
              placeholder="Путь к изображению или Minio key"
            />
            <div class="mt-2">
              <input
                ref="mainImageInput"
                type="file"
                class="hidden"
                accept="image/*"
                @change="handleMainImageUpload"
              >
              <el-button
                size="small"
                @click="$refs.mainImageInput.click()"
              >
                Загрузить изображение
              </el-button>
              <div
                v-if="department.image && department.imageUrl"
                class="mt-4"
              >
                <img
                  :src="department.imageUrl"
                  alt="Department image"
                  class="max-w-xs rounded-lg shadow-md"
                >
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="saving"
              @click="saveGeneral"
            >
              Сохранить
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Placeholder for future tabs -->
      <!-- Additional tabs can be added here for future functionality -->
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import departmentService from '@/services/departmentService'
import stationService from '@/services/stationService'
import minioService from '@/services/minioService'
import { resolveDepartmentMedia } from '@/utils/departmentsMedia'

const route = useRoute()
const router = useRouter()
const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)

const department = ref({
  name: '',
  short_name: '',
  description: '',
  image: '',
  status: 'active',
  imageUrl: ''
})

const mainImageInput = ref(null)

const isEditing = computed(() => {
  // Check route name first (more reliable)
  if (route.name === 'AdminDepartmentCreate') return false
  // Then check if id param exists and is not 'new'
  return route.params.id && route.params.id !== 'new'
})

const loadData = async () => {
  if (!isEditing.value) {
    return
  }
  
  // Ensure we have a valid ID
  if (!route.params.id) {
    return
  }
  
  loading.value = true
  try {
    const data = await departmentService.getDepartment(route.params.id)
    if (data) {
      department.value = { ...data }
      
      // Load image URL if exists
      if (data.image) {
        const resolved = resolveDepartmentMedia(data.image, { defaultFolder: 'departments' })
        if (resolved.kind === 'url' || resolved.kind === 'public') {
          department.value.imageUrl = resolved.url
        } else if (resolved.kind === 'minio') {
          try {
            department.value.imageUrl = await minioService.getPresignedDownloadUrl(
              resolved.objectKey,
              7 * 24 * 60 * 60,
              resolved.contentType
            )
          } catch (error) {
            console.error('Error loading image URL:', error)
            department.value.imageUrl = minioService.getFileUrl(resolved.objectKey)
          }
        }
      }
    }
  } catch (error) {
    ElMessage.error('Ошибка загрузки данных: ' + error.message)
  } finally {
    loading.value = false
  }
}

const saveGeneral = async () => {
  // Валидация обязательных полей
  if (!department.value.name || !department.value.name.trim()) {
    ElMessage.error('Поле "Название" обязательно для заполнения')
    return
  }
  
  if (!department.value.short_name || !department.value.short_name.trim()) {
    ElMessage.error('Поле "Короткое название" обязательно для заполнения')
    return
  }
  
  saving.value = true
  try {
    const departmentData = {
      name: department.value.name.trim(),
      shortName: department.value.short_name.trim(),
      description: department.value.description ? department.value.description.trim() : '',
      image: department.value.image || '',
      status: department.value.status || 'active'
    }
    
    if (isEditing.value) {
      const result = await departmentService.updateDepartment(route.params.id, departmentData)
      console.log('[DepartmentEditor] Update result:', result)
      ElMessage.success('Сохранено')
      await loadData() // Reload to get updated data
    } else {
      const result = await departmentService.createDepartment(departmentData)
      console.log('[DepartmentEditor] Create result:', result)
      
      // Обработка ответа - может быть объект напрямую или обернутый
      const newDepartment = result.data || result
      if (!newDepartment || !newDepartment.id) {
        throw new Error('Не удалось получить ID созданного отдела')
      }
      
      ElMessage.success('Отдел создан')
      router.push(`/admin/departments/${newDepartment.id}`)
    }
  } catch (error) {
    console.error('[DepartmentEditor] Save error:', error)
    const errorMessage = error.message || 'Неизвестная ошибка при сохранении'
    ElMessage.error('Ошибка сохранения: ' + errorMessage)
  } finally {
    saving.value = false
  }
}

const handleMainImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // If creating new department, we need to create it first to get an ID
  if (!isEditing.value && !department.value.id) {
    // Create department first with minimal data
    try {
      const departmentData = {
        name: department.value.name || 'Новый отдел',
        shortName: department.value.short_name || 'NEW',
        description: department.value.description || '',
        image: '',
        status: department.value.status || 'active'
      }
      const result = await departmentService.createDepartment(departmentData)
      // Обработка ответа - может быть объект напрямую или обернутый
      const newDepartment = result.data || result
      if (!newDepartment || !newDepartment.id) {
        throw new Error('Не удалось получить ID созданного отдела')
      }
      department.value.id = newDepartment.id
      // Update route to editing mode
      router.replace(`/admin/departments/${newDepartment.id}`)
    } catch (error) {
      ElMessage.error('Ошибка создания отдела: ' + error.message)
      event.target.value = ''
      return
    }
  }
  
  try {
    const departmentId = department.value.id || route.params.id
    const key = await stationService.uploadFile(file, `departments/${departmentId}/images`)
    department.value.image = key
    
    // Update image URL for preview
    const resolved = resolveDepartmentMedia(key, { defaultFolder: 'departments' })
    if (resolved.kind === 'minio') {
      try {
        department.value.imageUrl = await minioService.getPresignedDownloadUrl(
          resolved.objectKey,
          7 * 24 * 60 * 60,
          resolved.contentType
        )
      } catch (error) {
        department.value.imageUrl = minioService.getFileUrl(resolved.objectKey)
      }
    }
    
    await saveGeneral()
    ElMessage.success('Изображение загружено')
  } catch (error) {
    ElMessage.error('Ошибка загрузки изображения: ' + error.message)
  } finally {
    event.target.value = ''
  }
}

onMounted(() => {
  loadData()
})
</script>

