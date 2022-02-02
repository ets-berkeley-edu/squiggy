<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <h4>What do you want to add?</h4>
        <v-radio-group v-model="nextStep">
          <v-radio label="Add this entire page" :value="2" />
          <v-radio label="Add items from this page" :value="3" />
        </v-radio-group>
      </v-col>
    </v-row>
    <v-row justify="end" no-gutters>
      <v-col>
        <BookmarkletButtons :current-step="1" :next-step="nextStep" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context],
  components: {BookmarkletButtons},
  data: () => ({
    nextStep: 2
  }),
  created() {
    this.init().then(() => {
      this.$ready('Bookmarklet is ready!')
    })
  }
}
</script>
