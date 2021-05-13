<template>
  <v-app :id="$vuetify.theme.dark ? 'dark' : 'light'">
    <VueAnnouncer />
    <Spinner v-if="isLoading && !noSpinnerWhenLoading" />
    <router-view :key="stripAnchorRef($route.fullPath)" />
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import Utils from '@/mixins/Utils'

export default {
  name: 'App',
  components: {Spinner},
  mixins: [Context, Utils]
}
</script>

<style>
  @import './assets/styles/squiggy-dark.css';
  @import './assets/styles/squiggy-global.css';
  @import './assets/styles/squiggy-light.css';
</style>
