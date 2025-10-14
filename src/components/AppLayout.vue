<template>
  <div class="min-h-screen">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script>
import Header from './Header.vue'
import Footer from './Footer.vue'

export default {
  name: 'AppLayout',
  components: {
    Header,
    Footer
  }
}
</script>
