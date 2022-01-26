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
        When browsing the web, click the Asset Library bookmark when you find something interesting about this course.
      </div>
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'

export default {
  name: 'BookmarkletStart',
  components: {BackToAssetLibrary},
  mixins: [Context],
  data: () => ({
    pageTitle: 'How to use the bookmark',
    screenshot: undefined
  }),
  created() {
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-4-${this.currentBrowser}.png`)
    this.$ready(this.pageTitle)
  }
}
</script>
