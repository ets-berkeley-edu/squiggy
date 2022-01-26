<template>
  <div>
    <BackToAssetLibrary anchor="asset-library" :disabled="isLoading" />
    <div class="align-center d-flex">
      <div class="pr-3">
        <font-awesome-icon icon="bookmark" size="lg" />
      </div>
      <div>
        <h2>Easily add assets from anywhere on the web</h2>
      </div>
    </div>
    <div v-if="!isLoading" class="pt-2">
      <img
        aria-label="Screenshot showing SuiteC Asset Library"
        alt="Screenshot showing SuiteC Asset Library"
        :src="screenshot"
      />
      <div>
        Add assets directly to the Asset Library from any webpage without logging in.
      </div>
      <div class="float-right">
        <v-btn
          id="go-to-next-step-btn"
          class="bg-transparent pl-0"
          elevation="0"
          @click="go('/bookmarklet/step2')"
          @keypress.enter="go('/bookmarklet/step2')"
        >
          Get started
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
  name: 'BookmarkletStep1',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    screenshot: undefined
  }),
  created() {
    this.screenshot = require('@/assets/bookmarklet/bookmarklet-1.png')
    this.$ready('Add assets more easily with the Bookmarklet.')
  }
}
</script>
