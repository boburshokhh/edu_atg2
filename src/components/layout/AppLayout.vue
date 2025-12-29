<template>
  <div class="min-h-screen">
    <!-- Header -->
    <Header />

    <!-- Main Content -->
    <main class="pt-24 sm:pt-28 lg:pt-32">
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
