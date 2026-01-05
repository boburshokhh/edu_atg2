import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import stationService from '@/services/stationService'

export function useDocsCrud(station, docs, loadData) {
  const uploadingDoc = ref(false)

  const handleDocUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    uploadingDoc.value = true
    try {
      const key = await stationService.uploadFile(file, `stations/${station.value.id}/docs`)
      await stationService.createNormativeDoc(station.value.id, {
        title: file.name,
        file_url: key
      })
      ElMessage.success('Документ загружен')
      loadData()
    } catch (error) {
      ElMessage.error('Ошибка загрузки документа: ' + error.message)
    } finally {
      uploadingDoc.value = false
      event.target.value = ''
    }
  }

  const deleteDoc = async (doc) => {
    try {
      await stationService.deleteNormativeDoc(station.value.id, doc.id)
      ElMessage.success('Документ удален')
      docs.value = docs.value.filter(d => d.id !== doc.id)
    } catch (error) {
      ElMessage.error('Ошибка удаления: ' + error.message)
    }
  }

  return {
    uploadingDoc,
    handleDocUpload,
    deleteDoc
  }
}

