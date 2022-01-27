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
      <div class="pl-3 py-2">
        Drag
        <a class="bookmarklet mx-2" :href="bookmarklet" @click.prevent>
          <font-awesome-icon class="mr-1" icon="bookmark" /> Asset Library
        </a>
        to the browser's {{ toolbarName }}.
      </div>
      <div class="float-right">
        <v-btn
          id="go-to-next-step-btn"
          class="bg-transparent pl-0"
          elevation="0"
          @click="go('/bookmarklet/step4')"
          @keypress.enter="go('/bookmarklet/step4')"
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
  name: 'BookmarkletStart',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    pageTitle: 'How to enable the bookmark',
    screenshot: undefined,
    toolbarName: undefined
  }),
  created() {
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-3-${this.currentBrowser}.png`)
    this.toolbarName = this.$_.get({'chrome': 'Bookmarks Bar', 'safari': 'Favorites Bar', 'ie': 'Favorites bar'}, this.currentBrowser, 'bookmarks toolbar')
    this.$ready(this.pageTitle)
  },
  methods: {
    bookmarklet() {
      window.squiggy = window.squiggy || {
        initialized: false, // TODO: Is 'initialized' needed?
        canvasApiDomain: this.$currentUser.canvasApiDomain,
        apiBaseUrl: this.$config.apiBaseUrl,
        bookmarkletToken: this.$currentUser.bookmarkletToken,
        canvasCourseId: this.$currentUser.canvasCourseId,
        toolUrl: undefined, // TODO: Is tool_url needed?
        userId: this.$currentUser.id
      }
      if (window.squiggy.initialized) {
        if (this.isInIframe) {
          this.postIFrameMessage('squiggy.load', '*')
        }
      } else {
        window.squiggy.initialized = true
        const bookmarklet = document.createElement('script')
        bookmarklet.src = `${this.$config.apiBaseUrl}/assets/bookmarklet/bookmarklet.js`
        document.body.appendChild(bookmarklet)
      }
    }
  }
}
</script>

<style scoped>
.bookmarklet {
  border: 2px solid #0295DE;
  color: #333;
  padding: 10px 15px;
  text-decoration: none;
}
</style>
