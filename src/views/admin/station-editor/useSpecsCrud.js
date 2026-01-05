import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useSpecsCrud(station, loadData) {
  const showSpecDialog = ref(false)
  const editingSpec = ref(null)
  const specForm = ref({
    category: '',
    value: '',
    unit: '',
    description: ''
  })

  const editSpec = (item) => {
    editingSpec.value = item
    specForm.value = { ...item }
    showSpecDialog.value = true
  }

  const saveSpec = async () => {
    try {
      if (editingSpec.value) {
        await stationService.updateSpecification(station.value.id, editingSpec.value.id, specForm.value)
        ElMessage.success('Характеристика обновлена')
      } else {
        await stationService.createSpecification(station.value.id, specForm.value)
        ElMessage.success('Характеристика добавлена')
      }
      showSpecDialog.value = false
      editingSpec.value = null
      specForm.value = { category: '', value: '', unit: '', description: '' }
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка: ' + error.message)
    }
  }

  const deleteSpec = async (item) => {
    try {
      await stationService.deleteSpecification(station.value.id, item.id)
      ElMessage.success('Характеристика удалена')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    showSpecDialog,
    editingSpec,
    specForm,
    editSpec,
    saveSpec,
    deleteSpec
  }
}

