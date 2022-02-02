<template>
  <div id="base">
    <v-main id="content" class="ma-3">
      <router-view />
    </v-main>
  </div>
</template>

<script>
import Util from '@/mixins/Utils'

export default {
  name: 'BasePopupView',
  mixins: [Util],
  created() {
    this.setColorScheme()
  }
}
</script>
