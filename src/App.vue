<template>
  <v-app :id="$vuetify.theme.dark ? 'dark' : 'light'">
    <VueAnnouncer />
    <router-view :key="stripAnchorRef($route.fullPath)" />
    <Footer />
  </v-app>
</template>

<script>
import Footer from '@/components/util/Footer'
import Util from '@/mixins/Utils'

export default {
  name: 'App',
  components: {Footer},
  mixins: [Util]
}
</script>

<style>
  @import './assets/styles/squiggy-dark.css';
  @import './assets/styles/squiggy-global.css';
  @import './assets/styles/squiggy-light.css';
</style>
