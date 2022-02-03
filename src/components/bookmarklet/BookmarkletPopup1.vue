<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>What do you want to add?</h1>
        <v-radio-group v-model="model">
          <v-radio label="Add this entire page" value="linkAsset" />
          <v-radio label="Add items from this page" value="imageAssets" />
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
      if (this.images.length === 0) {
        this.go('/bookmarklet/popup/2')
      }
      this.$ready('Bookmarklet is ready!')
    })
  }
}
</script>
