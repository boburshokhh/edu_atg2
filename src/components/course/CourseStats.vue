<template>
  <div class="flex flex-wrap gap-4">
    <div class="flex items-center gap-2">
      <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
        <ClockIcon class="w-5 h-5 text-white" />
      </div>
      <div>
        <div class="text-white/70 text-xs">
          Длительность
        </div>
        <div class="text-white font-bold">
          {{ stats.duration }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
        <PlayCircleIcon class="w-5 h-5 text-white" />
      </div>
      <div>
        <div class="text-white/70 text-xs">
          Видеоуроков
        </div>
        <div class="text-white font-bold">
          {{ stats.videos }}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-9 h-9 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center">
        <DocumentTextIcon class="w-5 h-5 text-white" />
      </div>
      <div>
        <div class="text-white/70 text-xs">
          Материалов
        </div>
        <div class="text-white font-bold">
          {{ stats.materials }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ClockIcon, PlayCircleIcon, DocumentTextIcon } from '@heroicons/vue/24/solid'

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
  }
}
</script>

