import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useSafetyCrud(station, loadData) {
  const showSafetyDialog = ref(false)
  const editingSafetySystem = ref(null)
  const safetyForm = ref({
    name: '',
    description: '',
    manufacturer: '',
    features: ['']
  })

  const editSafetySystem = (item) => {
    editingSafetySystem.value = item
    const featureNames = item.feature_names || (Array.isArray(item.features) ? item.features.map(f => typeof f === 'string' ? f : f.feature_name) : [])
    safetyForm.value = {
      name: item.name,
      description: item.description || '',
      manufacturer: item.manufacturer || '',
      features: featureNames.length > 0 ? [...featureNames] : [''],
      featureIds: Array.isArray(item.features) ? item.features.map(f => typeof f === 'object' ? f.id : null).filter(id => id !== null) : []
    }
    showSafetyDialog.value = true
  }

  const saveSafetySystem = async () => {
    try {
      const features = safetyForm.value.features.filter(f => f && f.trim())
      
      if (editingSafetySystem.value) {
        await stationService.updateSafetySystem(station.value.id, editingSafetySystem.value.id, {
          name: safetyForm.value.name,
          description: safetyForm.value.description,
          manufacturer: safetyForm.value.manufacturer
        })
        
        const existingFeatures = editingSafetySystem.value.features || []
        for (const feature of existingFeatures) {
          if (typeof feature === 'object' && feature.id) {
            try {
              await stationService.deleteSafetySystemFeature(station.value.id, editingSafetySystem.value.id, feature.id)
            } catch (e) {
              console.warn('Failed to delete feature:', e)
            }
          }
        }
        
        for (const featureName of features) {
          if (featureName.trim()) {
            await stationService.createSafetySystemFeature(station.value.id, editingSafetySystem.value.id, {
              feature_name: featureName.trim()
            })
          }
        }
        
        ElMessage.success('Система безопасности обновлена')
      } else {
        const newSystem = await stationService.createSafetySystem(station.value.id, {
          name: safetyForm.value.name,
          description: safetyForm.value.description,
          manufacturer: safetyForm.value.manufacturer
        })
        
        for (const featureName of features) {
          if (featureName.trim()) {
            await stationService.createSafetySystemFeature(station.value.id, newSystem.id, {
              feature_name: featureName.trim()
            })
          }
        }
        
        ElMessage.success('Система безопасности добавлена')
      }
      
      showSafetyDialog.value = false
      editingSafetySystem.value = null
      safetyForm.value = { name: '', description: '', manufacturer: '', features: [''], featureIds: [] }
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка: ' + error.message)
    }
  }

  const deleteSafetySystem = async (item) => {
    try {
      await stationService.deleteSafetySystem(station.value.id, item.id)
      ElMessage.success('Система безопасности удалена')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    showSafetyDialog,
    editingSafetySystem,
    safetyForm,
    editSafetySystem,
    saveSafetySystem,
    deleteSafetySystem
  }
}

