<template>
  <component :is="iconComponent" :class="iconClass" />
</template>

<script setup>
import { computed, h } from 'vue'

const props = defineProps({
  fileType: {
    type: String,
    default: 'document' // 'pdf', 'video', 'word', 'excel', 'powerpoint', 'document'
  },
  size: {
    type: String,
    default: 'md' // 'sm', 'md', 'lg'
  }
})

const iconClass = computed(() => {
  const sizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }
  return sizes[props.size] || sizes.md
})

// PDF Icon (Red)
const PdfIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', 
    fill: '#DC2626' 
  }),
  h('path', { 
    d: 'M14 2V8H20', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  }),
  h('path', { 
    d: 'M16 13H8V11H16V13Z', 
    fill: 'white' 
  }),
  h('path', { 
    d: 'M16 17H8V15H16V17Z', 
    fill: 'white' 
  }),
  h('path', { 
    d: 'M10 9H9V10H10V9Z', 
    fill: 'white' 
  })
])

// Video Icon (Red)
const VideoIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M15 10L20.553 6.276C20.8334 6.10747 21.1786 6.02763 21.5248 6.05074C21.871 6.07385 22.2004 6.19866 22.4539 6.40424C22.7074 6.60982 22.8698 6.88377 22.9146 7.18282C22.9594 7.48187 22.8838 7.78719 22.701 8.044L19 13L22.701 17.956C22.8838 18.2128 22.9594 18.5181 22.9146 18.8172C22.8698 19.1162 22.7074 19.3902 22.4539 19.5958C22.2004 19.8013 21.871 19.9262 21.5248 19.9493C21.1786 19.9724 20.8334 19.8925 20.553 19.724L15 16V10Z', 
    fill: '#EF4444' 
  }),
  h('path', { 
    d: 'M3 6C3 5.46957 3.21071 4.96086 3.58579 4.58579C3.96086 4.21071 4.46957 4 5 4H13C13.5304 4 14.0391 4.21071 14.4142 4.58579C14.7893 4.96086 15 5.46957 15 6V18C15 18.5304 14.7893 19.0391 14.4142 19.4142C14.0391 19.7893 13.5304 20 13 20H5C4.46957 20 3.96086 19.7893 3.58579 19.4142C3.21071 19.0391 3 18.5304 3 18V6Z', 
    fill: '#EF4444' 
  }),
  h('path', { 
    d: 'M9 8L12 10L9 12V8Z', 
    fill: 'white' 
  })
])

// Word Icon (Blue)
const WordIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', 
    fill: '#2563EB' 
  }),
  h('path', { 
    d: 'M14 2V8H20', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  }),
  h('path', { 
    d: 'M8 12L9.5 16.5L11 12M13 12V16.5M15.5 12L17 16.5L18.5 12', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  })
])

// Excel Icon (Green)
const ExcelIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', 
    fill: '#16A34A' 
  }),
  h('path', { 
    d: 'M14 2V8H20', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  }),
  h('path', { 
    d: 'M8 12L10.5 15.5L8 19M16 12V19M16 12H10.5', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  })
])

// PowerPoint Icon (Orange)
const PowerPointIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', 
    fill: '#EA580C' 
  }),
  h('path', { 
    d: 'M14 2V8H20', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  }),
  h('circle', { 
    cx: '12', 
    cy: '14', 
    r: '3', 
    fill: 'white' 
  }),
  h('path', { 
    d: 'M9 14H15', 
    stroke: '#EA580C', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round' 
  })
])

// Document Icon (Gray)
const DocumentIcon = () => h('svg', {
  viewBox: '0 0 24 24',
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  class: iconClass.value
}, [
  h('path', { 
    d: 'M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z', 
    fill: '#6B7280' 
  }),
  h('path', { 
    d: 'M14 2V8H20', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round', 
    'stroke-linejoin': 'round' 
  }),
  h('path', { 
    d: 'M8 12H16M8 16H16M8 9H12', 
    stroke: 'white', 
    'stroke-width': '1.5', 
    'stroke-linecap': 'round' 
  })
])

const iconComponent = computed(() => {
  const icons = {
    pdf: PdfIcon,
    video: VideoIcon,
    word: WordIcon,
    excel: ExcelIcon,
    powerpoint: PowerPointIcon,
    document: DocumentIcon
  }
  return icons[props.fileType.toLowerCase()] || DocumentIcon
})
</script>

