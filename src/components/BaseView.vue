<template>
  <v-main id="content" class="ma-3">
    <Spinner v-if="isLoading && !noSpinnerWhenLoading" />
    <router-view />
  </v-main>
</template>

<script>
import Context from '@/mixins/Context'
import Iframe from '@/mixins/Iframe'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Utils'

export default {
  name: 'BaseView',
  components: {Spinner},
  mixins: [Context, Iframe, Util],
  data: () => ({
    navItems: undefined,
  }),
  created() {
    if (!this.$isInIframe) {
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
