<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-6 max-w-4xl">
    <!-- Duration Card -->
    <div class="flex flex-col bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md hover:bg-white/10 hover:border-white/20 transition-all cursor-default group">
      <div class="flex items-center gap-3 text-blue-400 mb-3">
        <ClockIcon class="w-6 h-6 group-hover:scale-110 transition-transform" />
        <span class="text-sm font-bold uppercase tracking-wider text-gray-400">Длительность</span>
      </div>
      <div class="mt-auto">
        <span class="text-4xl font-bold text-white font-display block">{{ getDurationNumber(stats.duration) }}</span>
        <span class="text-lg font-medium text-gray-400">{{ getDurationLabel(stats.duration) }}</span>
      </div>
    </div>

    <!-- Videos Card -->
    <div class="flex flex-col bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md hover:bg-white/10 hover:border-white/20 transition-all cursor-default group">
      <div class="flex items-center gap-3 text-emerald-400 mb-3">
        <PlayCircleIcon class="w-6 h-6 group-hover:scale-110 transition-transform" />
        <span class="text-sm font-bold uppercase tracking-wider text-gray-400">Видеоуроки</span>
      </div>
      <div class="mt-auto">
        <span class="text-4xl font-bold text-white font-display block">{{ getVideosNumber(stats.videos) }}</span>
        <span class="text-lg font-medium text-gray-400">{{ getVideosLabel(stats.videos) }}</span>
      </div>
    </div>

    <!-- Materials Card -->
    <div class="flex flex-col bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md hover:bg-white/10 hover:border-white/20 transition-all cursor-default group">
      <div class="flex items-center gap-3 text-amber-400 mb-3">
        <DocumentTextIcon class="w-6 h-6 group-hover:scale-110 transition-transform" />
        <span class="text-sm font-bold uppercase tracking-wider text-gray-400">Материалы</span>
      </div>
      <div class="mt-auto">
        <span class="text-4xl font-bold text-white font-display block">{{ getMaterialsNumber(stats.materials) }}</span>
        <span class="text-lg font-medium text-gray-400">{{ getMaterialsLabel(stats.materials) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ClockIcon, PlayCircleIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'CourseStats',
  components: {
    ClockIcon,
    PlayCircleIcon,
    DocumentTextIcon
  },
  props: {
    stats: {
      type: Object,
      required: true,
      validator: (value) => {
        return value && typeof value.duration !== 'undefined' && 
               typeof value.videos !== 'undefined' && 
               typeof value.materials !== 'undefined'
      }
    }
  },
  setup() {
    const getDurationNumber = (duration) => {
      if (typeof duration === 'number') return duration
      // Extract number from string like "40 часов" or "40 академических часов"
      const match = String(duration).match(/\d+/)
      return match ? match[0] : duration
    }

    const getDurationLabel = (duration) => {
      if (typeof duration === 'number') return 'академических часов'
      // Extract label from string
      const match = String(duration).match(/\d+\s*(.+)/)
      return match ? match[1] : 'академических часов'
    }

    const getVideosNumber = (videos) => {
      if (typeof videos === 'number') return videos
      const match = String(videos).match(/\d+/)
      return match ? match[0] : videos
    }

    const getVideosLabel = (videos) => {
      if (typeof videos === 'number') return 'обучающих модулей'
      const match = String(videos).match(/\d+\s*(.+)/)
      return match ? match[1] : 'обучающих модулей'
    }

    const getMaterialsNumber = (materials) => {
      if (typeof materials === 'number') return materials
      const match = String(materials).match(/\d+/)
      return match ? match[0] : materials
    }

    const getMaterialsLabel = (materials) => {
      if (typeof materials === 'number') return 'файла для скачивания'
      const match = String(materials).match(/\d+\s*(.+)/)
      return match ? match[1] : 'файла для скачивания'
    }

    return {
      getDurationNumber,
      getDurationLabel,
      getVideosNumber,
      getVideosLabel,
      getMaterialsNumber,
      getMaterialsLabel
    }
  }
}
</script>
