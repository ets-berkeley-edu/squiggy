<template>
  <v-app :id="$vuetify.theme.dark ? 'dark' : 'light'">
    <VueAnnouncer />
    <router-view :key="stripAnchorRef($route.fullPath)" />
    <FooterIFrame v-if="isInIframe" />
    <FooterStandalone v-if="!isInIframe && $currentUser.isAuthenticated" />
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import FooterStandalone from '@/components/util/FooterStandalone'
import FooterIFrame from '@/components/util/FooterIFrame'
import Util from '@/mixins/Utils'

export default {
  name: 'App',
  components: {FooterStandalone, FooterIFrame},
  mixins: [Context, Util]
}
</script>

<style>
  @import './assets/styles/squiggy-dark.css';
  @import './assets/styles/squiggy-global.css';
  @import './assets/styles/squiggy-light.css';
</style>
