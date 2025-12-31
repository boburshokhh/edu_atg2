<template>
  <div class="min-h-screen">
    <!-- Header -->
    <Header v-if="showHeader" />

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <Footer v-if="showFooter" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './Header.vue'
import Footer from './Footer.vue'

export default {
  name: 'AppLayout',
  components: {
    Header,
    Footer
  },
  setup() {
    const route = useRoute()
    
    const showHeader = computed(() => {
      return !route.meta?.hideHeader
    })
    
    const showFooter = computed(() => {
      return !route.meta?.hideFooter
    })
    
    return {
      showHeader,
      showFooter
    }
  }
}
</script>
