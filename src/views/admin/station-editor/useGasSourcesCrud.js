import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useGasSourcesCrud(station, loadData) {
  const showGasSourceDialog = ref(false)
  const editingGasSource = ref(null)
  const gasSourceForm = ref({
    source_name: ''
  })

  const editGasSource = (item) => {
    editingGasSource.value = item
    gasSourceForm.value = { source_name: item.source_name }
    showGasSourceDialog.value = true
  }

  const saveGasSource = async () => {
    try {
      if (editingGasSource.value) {
        await stationService.updateGasSupplySource(station.value.id, editingGasSource.value.id, gasSourceForm.value)
        ElMessage.success('Источник обновлен')
      } else {
        await stationService.createGasSupplySource(station.value.id, gasSourceForm.value)
        ElMessage.success('Источник добавлен')
      }
      showGasSourceDialog.value = false
      editingGasSource.value = null
      gasSourceForm.value = { source_name: '' }
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка: ' + error.message)
    }
  }

  const deleteGasSource = async (item) => {
    try {
      await stationService.deleteGasSupplySource(station.value.id, item.id)
      ElMessage.success('Источник удален')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    showGasSourceDialog,
    editingGasSource,
    gasSourceForm,
    editGasSource,
    saveGasSource,
    deleteGasSource
  }
}

