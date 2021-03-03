<template>
  <v-app :id="$vuetify.theme.dark ? 'dark' : 'light'">
    <VueAnnouncer />
    <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
  </v-app>
</template>

<script>
import Util from '@/mixins/Utils'

export default {
  name: 'App',
  mixins: [Util]
}
</script>

<style>
  @import './assets/styles/squiggy-dark.css';
  @import './assets/styles/squiggy-global.css';
  @import './assets/styles/squiggy-light.css';
</style>
