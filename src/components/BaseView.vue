<template>
  <v-main id="content" class="ma-3">
    <Spinner v-if="loading" />
    <router-view />
  </v-main>
</template>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Utils'

export default {
  name: 'BaseView',
  components: {Spinner},
  mixins: [Context, Util],
  data: () => ({
    navItems: undefined,
  }),
  created() {
    this.prefersColorScheme()
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
