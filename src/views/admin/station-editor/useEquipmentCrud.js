import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useEquipmentCrud(station, loadData) {
  const showEquipmentDialog = ref(false)
  const editingEquipment = ref(null)
  const equipmentForm = ref({
    name: '',
    model: '',
    manufacturer: '',
    quantity: 1,
    power: '',
    description: ''
  })

  const editEquipment = (item) => {
    editingEquipment.value = item
    equipmentForm.value = { ...item }
    showEquipmentDialog.value = true
  }

  const saveEquipment = async () => {
    try {
      if (editingEquipment.value) {
        await stationService.updateEquipment(station.value.id, editingEquipment.value.id, equipmentForm.value)
        ElMessage.success('Оборудование обновлено')
      } else {
        await stationService.createEquipment(station.value.id, equipmentForm.value)
        ElMessage.success('Оборудование добавлено')
      }
      showEquipmentDialog.value = false
      editingEquipment.value = null
      equipmentForm.value = { name: '', model: '', manufacturer: '', quantity: 1, power: '', description: '' }
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка: ' + error.message)
    }
  }

  const deleteEquipment = async (item) => {
    try {
      await stationService.deleteEquipment(station.value.id, item.id)
      ElMessage.success('Оборудование удалено')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    showEquipmentDialog,
    editingEquipment,
    equipmentForm,
    editEquipment,
    saveEquipment,
    deleteEquipment
  }
}

