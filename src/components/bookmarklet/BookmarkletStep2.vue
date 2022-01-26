<template>
  <div>
    <BackToAssetLibrary anchor="asset-library" :disabled="isLoading" />
    <div class="align-center d-flex">
      <div class="pr-3">
        <font-awesome-icon icon="bookmark" size="lg" />
      </div>
      <div>
        <h2>{{ pageTitle }}</h2>
      </div>
    </div>
    <div v-if="!isLoading" class="pt-2 w-100">
      <img
        :aria-label="`Screenshot showing ${pageTitle}`"
        :alt="`Screenshot showing ${pageTitle}`"
        :src="screenshot"
      />
      <div>
        First, enable your browser's <b>TODO: data-ng-bind="toolbar"</b>.
      </div>
      <div class="float-right">
        <v-btn
          id="go-to-next-step-btn"
          class="bg-transparent pl-0"
          elevation="0"
          @click="go('/bookmarklet/step3')"
          @keypress.enter="go('/bookmarklet/step3')"
        >
          Next
          <font-awesome-icon class="ml-2" icon="greater-than" size="lg" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletStep2',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    pageTitle: 'How to enable the bookmark',
    screenshot: undefined
  }),
  created() {
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-2-${this.currentBrowser}.png`)
    this.$ready(this.pageTitle)
  }
}
</script>
