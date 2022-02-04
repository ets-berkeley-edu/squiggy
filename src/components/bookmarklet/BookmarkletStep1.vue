<template>
  <div>
    <BackToAssetLibrary anchor="asset-library" :disabled="isLoading" />
    <div class="align-center d-flex">
      <div class="pr-3">
        <font-awesome-icon icon="bookmark" size="lg" />
      </div>
      <div>
        <PageTitle text="Easily add assets from anywhere on the web" />
      </div>
    </div>
    <div v-if="!isLoading" class="pt-2">
      <img
        aria-label="Screenshot showing SuiteC Asset Library"
        alt="Screenshot showing SuiteC Asset Library"
        :src="screenshot"
      />
      <div class="pl-3">
        Add assets directly to the Asset Library from any webpage without logging in.
      </div>
      <div class="pl-3 pt-5">
        <v-btn
          id="go-to-next-step-btn"
          color="primary"
          @click="go('/bookmarklet/step2')"
          @keypress.enter="go('/bookmarklet/step2')"
        >
          Get started
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
  name: 'BookmarkletStep1',
  components: {BackToAssetLibrary, PageTitle},
  mixins: [Context, Utils],
  data: () => ({
    screenshot: undefined
  }),
  created() {
    this.screenshot = require('@/assets/bookmarklet/bookmarklet-1.png')
    this.$ready('Bookmarklet instructions, part 1')
  }
}
</script>
