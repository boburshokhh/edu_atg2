import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useGeneralTab(station, isEditing, loadData) {
  const router = useRouter()
  const saving = ref(false)

  const saveGeneral = async () => {
    saving.value = true
    try {
      const stationData = {
        ...station.value,
        short_name: station.value.short_name,
        commission_date: station.value.commission_date,
        courses_count: station.value.courses_count || 0,
        design_capacity: station.value.design_capacity,
        gas_pressure: station.value.gas_pressure,
        distance_from_border: station.value.distance_from_border,
        pipeline_diameter: station.value.pipeline_diameter,
        input_pressure: station.value.input_pressure,
        output_pressure: station.value.output_pressure,
        parallel_lines: station.value.parallel_lines,
        tech_map_image: station.value.tech_map_image
      }
      
      if (isEditing.value) {
        await stationService.updateStation(station.value.id, stationData)
        ElMessage.success('Сохранено')
        loadData() // Reload to get updated data
      } else {
        const newStation = await stationService.createStation(stationData)
        ElMessage.success('Станция создана')
        router.push(`/admin/stations/${newStation.id}`)
      }
    } catch (error) {
      ElMessage.error('Ошибка сохранения: ' + error.message)
    } finally {
      saving.value = false
    }
  }

  const handleMainImageUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/images`)
      station.value.image = key
      await saveGeneral()
      ElMessage.success('Изображение загружено')
    } catch (error) {
      ElMessage.error('Ошибка загрузки изображения: ' + error.message)
    } finally {
      event.target.value = ''
    }
  }

  const handleTechMapUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/tech_maps`)
      station.value.tech_map_image = key
      await saveGeneral()
      ElMessage.success('Техническая карта загружена')
    } catch (error) {
      ElMessage.error('Ошибка загрузки технической карты: ' + error.message)
    } finally {
      event.target.value = ''
    }
  }

  return {
    saving,
    saveGeneral,
    handleMainImageUpload,
    handleTechMapUpload
  }
}

