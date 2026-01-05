<template>
  <div class="container mx-auto px-4 py-8">
    <StationEditorHeader
      :is-editing="isEditing"
      :station-name="station.name"
    />

    <el-tabs
      v-model="activeTab"
      v-loading="loading"
      class="bg-white p-6 rounded-lg shadow"
    >
      <el-tab-pane
        label="Общая информация"
        name="general"
      >
        <GeneralTab />
      </el-tab-pane>

      <el-tab-pane
        label="Программа обучения"
        name="program"
        :disabled="!isEditing"
      >
        <ProgramTab />
      </el-tab-pane>

      <el-tab-pane
        label="Оборудование"
        name="equipment"
        :disabled="!isEditing"
      >
        <EquipmentTab />
      </el-tab-pane>

      <el-tab-pane
        label="Технические характеристики"
        name="specs"
        :disabled="!isEditing"
      >
        <SpecsTab />
      </el-tab-pane>

      <el-tab-pane
        label="Системы безопасности"
        name="safety"
        :disabled="!isEditing"
      >
        <SafetyTab />
      </el-tab-pane>

      <el-tab-pane
        label="Источники подачи газа"
        name="gasSources"
        :disabled="!isEditing"
      >
        <GasSourcesTab />
      </el-tab-pane>

      <el-tab-pane
        label="Фотографии"
        name="photos"
        :disabled="!isEditing"
      >
        <PhotosTab />
      </el-tab-pane>

      <el-tab-pane
        label="Документы"
        name="docs"
        :disabled="!isEditing"
      >
        <DocsTab />
      </el-tab-pane>
    </el-tabs>
          </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { provideStationEditorContext } from './station-editor/context'
import { useStationData } from './station-editor/useStationData'
import { useGeneralTab } from './station-editor/useGeneralTab'
import { useCourseProgram } from './station-editor/useCourseProgram'
import { usePromoVideo } from './station-editor/usePromoVideo'
import { useEquipmentCrud } from './station-editor/useEquipmentCrud'
import { useSpecsCrud } from './station-editor/useSpecsCrud'
import { useSafetyCrud } from './station-editor/useSafetyCrud'
import { useGasSourcesCrud } from './station-editor/useGasSourcesCrud'
import { usePhotosCrud } from './station-editor/usePhotosCrud'
import { useDocsCrud } from './station-editor/useDocsCrud'
import StationEditorHeader from './station-editor/StationEditorHeader.vue'
import GeneralTab from './station-editor/tabs/GeneralTab.vue'
import ProgramTab from './station-editor/tabs/ProgramTab.vue'
import EquipmentTab from './station-editor/tabs/EquipmentTab.vue'
import SpecsTab from './station-editor/tabs/SpecsTab.vue'
import SafetyTab from './station-editor/tabs/SafetyTab.vue'
import GasSourcesTab from './station-editor/tabs/GasSourcesTab.vue'
import PhotosTab from './station-editor/tabs/PhotosTab.vue'
import DocsTab from './station-editor/tabs/DocsTab.vue'

const route = useRoute()
const activeTab = ref('general')

// Initialize all composables
const stationData = useStationData()
const {
  loading,
  station,
  photos,
  docs,
  equipment,
  specs,
  safetySystems,
  gasSources,
  isEditing,
  loadData
} = stationData

const generalTab = useGeneralTab(station, isEditing, loadData)
const {
  saving,
  saveGeneral,
  handleMainImageUpload,
  handleTechMapUpload
} = generalTab

const courseProgramComposable = useCourseProgram(station, isEditing)
const {
  courseProgram,
  savingCourseProgram,
  loadCourseProgram,
  saveCourseProgram,
  addLesson,
  removeLesson,
  addTopic,
  showTopicFilesDialog,
  activeTopic,
  topicFiles,
  uploadingTopicFile,
  newTopicFileType,
  newTopicFileIsMain,
  openTopicFiles,
  handleTopicFileUpload,
  updateTopicFile,
  deleteTopicFile,
  previewTopicFile
} = courseProgramComposable

const promoVideoComposable = usePromoVideo(station, isEditing)
const {
  promoVideo,
  promoVideoUrl,
  uploadingPromoVideo,
  loadPromoVideo,
  handlePromoVideoUpload,
  deletePromoVideo
} = promoVideoComposable

const equipmentCrud = useEquipmentCrud(station, loadData)
const {
  showEquipmentDialog,
  editingEquipment,
  equipmentForm,
  editEquipment,
  saveEquipment,
  deleteEquipment
} = equipmentCrud

const specsCrud = useSpecsCrud(station, loadData)
const {
  showSpecDialog,
  editingSpec,
  specForm,
  editSpec,
  saveSpec,
  deleteSpec
} = specsCrud

const safetyCrud = useSafetyCrud(station, loadData)
const {
  showSafetyDialog,
  editingSafetySystem,
  safetyForm,
  editSafetySystem,
  saveSafetySystem,
  deleteSafetySystem
} = safetyCrud

const gasSourcesCrud = useGasSourcesCrud(station, loadData)
const {
  showGasSourceDialog,
  editingGasSource,
  gasSourceForm,
  editGasSource,
  saveGasSource,
  deleteGasSource
} = gasSourcesCrud

const photosCrud = usePhotosCrud(station, photos, loadData)
const {
  uploadingPhoto,
  handlePhotoUpload,
  updatePhoto,
  deletePhoto
} = photosCrud

const docsCrud = useDocsCrud(station, docs, loadData)
const {
  uploadingDoc,
  handleDocUpload,
  deleteDoc
} = docsCrud

// Provide context to all child components
provideStationEditorContext({
  // Station data
  loading,
  station,
  photos,
  docs,
  equipment,
  specs,
  safetySystems,
  gasSources,
  isEditing,
  loadData,
  // General tab
  saving,
  saveGeneral,
  handleMainImageUpload,
  handleTechMapUpload,
  // Course program
  courseProgram,
  savingCourseProgram,
  saveCourseProgram,
  addLesson,
  removeLesson,
  addTopic,
  // Topic files
  showTopicFilesDialog,
  activeTopic,
  topicFiles,
  uploadingTopicFile,
  newTopicFileType,
  newTopicFileIsMain,
  openTopicFiles,
  handleTopicFileUpload,
  updateTopicFile,
  deleteTopicFile,
  previewTopicFile,
  // Promo video
  promoVideo,
  promoVideoUrl,
  uploadingPromoVideo,
  handlePromoVideoUpload,
  deletePromoVideo,
  // Equipment
  showEquipmentDialog,
  editingEquipment,
  equipmentForm,
  editEquipment,
  saveEquipment,
  deleteEquipment,
  // Specs
  showSpecDialog,
  editingSpec,
  specForm,
  editSpec,
  saveSpec,
  deleteSpec,
  // Safety
  showSafetyDialog,
  editingSafetySystem,
  safetyForm,
  editSafetySystem,
  saveSafetySystem,
  deleteSafetySystem,
  // Gas sources
  showGasSourceDialog,
  editingGasSource,
  gasSourceForm,
  editGasSource,
  saveGasSource,
  deleteGasSource,
  // Photos
  uploadingPhoto,
  handlePhotoUpload,
  updatePhoto,
  deletePhoto,
  // Docs
  uploadingDoc,
  handleDocUpload,
  deleteDoc
})

onMounted(async () => {
  await loadData()
    await loadCourseProgram()
    await loadPromoVideo()
})
</script>
