<template>
  <div id="base">
    <v-main id="content" class="ma-3">
      <router-view />
    </v-main>
    <FooterIFrame v-if="isInIframe" />
    <FooterStandalone v-if="!isInIframe && $currentUser.isAuthenticated" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import FooterIFrame from '@/components/util/FooterIFrame'
import FooterStandalone from '@/components/util/FooterStandalone'
import Util from '@/mixins/Utils'

export default {
  name: 'BaseView',
  components: {FooterIFrame, FooterStandalone},
  mixins: [Context, Util],
  created() {
    this.setColorScheme()
  }
}
</script>
