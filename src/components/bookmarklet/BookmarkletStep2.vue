<template>
  <div>
    <BackToAssetLibrary anchor="asset-library" :disabled="isLoading" />
    <div class="align-center d-flex">
      <div class="pr-3">
        <font-awesome-icon icon="bookmark" size="lg" />
      </div>
      <div>
        <PageTitle :text="pageTitle" />
      </div>
    </div>
    <div v-if="!isLoading" class="pt-2 w-100">
      <img
        :aria-label="`Screenshot showing ${pageTitle}`"
        :alt="`Screenshot showing ${pageTitle}`"
        :src="screenshot"
      />
      <div class="pl-3">
        First, enable your browser's {{ toolbarName }}.
      </div>
      <div class="pl-3 pt-5">
        <v-btn
          id="go-to-next-step-btn"
          color="primary"
          @click="go('/bookmarklet/step3')"
          @keypress.enter="go('/bookmarklet/step3')"
        >
          Next
          <font-awesome-icon class="ml-2" icon="arrow-right" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletStep2',
  components: {BackToAssetLibrary, PageTitle},
  mixins: [Context, Utils],
  data: () => ({
    pageTitle: 'How to enable the bookmark',
    screenshot: undefined,
    toolbarName: undefined
  }),
  created() {
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-2-${this.currentBrowser}.png`)
    this.toolbarName = this.$_.get({'chrome': 'Bookmarks Bar', 'safari': 'Favorites Bar', 'ie': 'Favorites bar'}, this.currentBrowser, 'bookmarks toolbar')
    this.$ready('Bookmarklet instructions, part 2')
  }
}
</script>
