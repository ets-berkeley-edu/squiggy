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
  data: () => ({
    navItems: undefined,
  }),
  created() {
    if (!this.isInIframe) {
      this.prefersColorScheme()
    }
  },
  methods: {
    prefersColorScheme() {
      const mq = window.matchMedia('(prefers-color-scheme: dark)')
      this.$vuetify.theme.dark = mq.matches
      if (typeof mq.addEventListener === 'function') {
        mq.addEventListener('change', e => this.$vuetify.theme.dark = e.matches)
      }
    }
  }
}
</script>
