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
    <div v-if="!isLoading" class="pt-2">
      <img
        :aria-label="`Screenshot showing ${pageTitle}`"
        :alt="`Screenshot showing ${pageTitle}`"
        :src="screenshot"
      />
      <div class="pl-3 py-2">
        Drag
        <a
          class="bookmarklet mx-2"
          :href="bookmarklet"
          @click.prevent="$_.noop"
        >
          <font-awesome-icon class="mr-1" icon="bookmark" /> Asset Library
        </a>
        to the browser's {{ toolbarName }}.
      </div>
      <div class="pl-3 pt-5">
        <v-btn
          id="go-to-next-step-btn"
          color="primary"
          @click="go('/bookmarklet/step4')"
          @keypress.enter="go('/bookmarklet/step4')"
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
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletStep3',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    bookmarklet: undefined,
    pageTitle: 'How to enable the bookmark',
    screenshot: undefined,
    toolbarName: undefined
  }),
  created() {
    const minimum = 150
    const url = `${this.$config.baseUrl}/bookmarklet/popup/1?_b=${this.$currentUser.bookmarkletAuth}`
    this.bookmarklet = `javascript:(() => {
      const images = [];
      const imageUrls = new Set();
      for (let i = 0; i < document.images.length; i++) {
        const img = document.images[i];
        const minWidth = 150;
        if (img.src && !imageUrls.has(img.src) && img.naturalHeight > ${minimum} && img.naturalWidth > ${minimum}) {
          images.push({
            src: img.src,
            height: img.naturalHeight,
            title: img.title || img.alt,
            width: img.naturalWidth
          });
          imageUrls.add(img.url);
        }
      }
      const description = document.querySelector('meta[name="description"]');
      const headers = document.getElementsByTagName('h1');
      const data = {
        description: (description && description.content) || (headers.length ? headers[0].innerHtml : null),
        images,
        title: document.title,
        url: window.location.href
      };
      window.open('${url}', JSON.stringify(data), 'popup');
    })()`
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-3-${this.currentBrowser}.png`)
    this.toolbarName = this.$_.get({'chrome': 'Bookmarks Bar', 'safari': 'Favorites Bar', 'ie': 'Favorites bar'}, this.currentBrowser, 'bookmarks toolbar')
    this.$ready(this.pageTitle)
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
