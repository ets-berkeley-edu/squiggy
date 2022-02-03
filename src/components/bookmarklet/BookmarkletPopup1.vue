<template>
  <div v-if="!isLoading">
    <v-container v-if="isAuthorized" fluid>
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
    <v-container v-if="!isAuthorized" fluid>
      <v-row no-gutters>
        <v-col>
          <h1 class="red--text">Uh oh!</h1>
          <div class="py-3 subtitle-1">
            Sorry, you are no longer a member of {{ course ? course.name : 'the course' }} and thus
            you are unable to use this previously installed bookmarklet. We suggest:
            <ol>
              <li>Delete the bookmarklet from your browser's toolbar.</li>
              <li>Return to SuiteC and install the bookmarklet of a course of which you are a member</li>
            </ol>
          </div>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="pt-5">
          <BookmarkletButtons />
        </v-col>
      </v-row>
    </v-container>
  </div>
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
