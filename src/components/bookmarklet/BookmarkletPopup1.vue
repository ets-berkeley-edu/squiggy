<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>What do you want to add?</h1>
        <div v-if="!targetPage.images.length" class="deep-orange--text font-weight-bold">
          The current page has no image eligible for the Asset Library. You have one choice: Add the entire page
          as a link asset. Click "Next" to proceed.
        </div>
        <v-radio-group v-model="model">
          <v-radio label="Add the entire page as a link asset" value="linkAsset" />
          <v-radio
            :disabled="!targetPage.images.length"
            label="Add selected items from this page"
            value="imageAssets"
          />
        </v-radio-group>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col class="pt-5">
        <BookmarkletButtons :next-step="model === 'linkAsset' ? 2 : 3" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons},
  computed: {
    model: {
      get() {
        return this.workflow
      },
      set(value) {
        this.setWorkflow(value)
      }
    }
  },
  created() {
    this.init().then(() => {
      this.$ready('Bookmarklet is ready!')
    })
  }
}
</script>
