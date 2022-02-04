<template>
  <div v-if="!isLoading">
    <v-container v-if="isAuthorized" fluid>
      <v-row no-gutters>
        <v-col>
          <div>
            <PageTitle text="What do you want to add?" />
          </div>
          <div v-if="!targetPage.images.length" class="deep-orange--text font-weight-bold">
            The current page has no images of sufficient size for the Asset Library.
            You have one choice: add the entire page as a link asset.
          </div>
          <v-radio-group v-model="model">
            <v-radio
              id="entire-page-as-asset-radio"
              label="Add the entire page as a link asset"
              value="linkAsset"
            />
            <v-radio
              id="selected-items-from-page-radio"
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
          <PageTitle css-class="red--text" text="Uh oh!" />
          <div
            id="unauthorized-message"
            aria-live="polite"
            class="py-3 subtitle-1"
            role="alert"
          >
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
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons, PageTitle},
  computed: {
    model: {
      get() {
        return this.workflow
      },
      set(value) {
        this.$announcer.polite(this.model === 'linkAsset'? 'Page as asset' : 'Page items as assets')
        this.setWorkflow(value)
      }
    }
  },
  created() {
    this.init().then(() => {
      this.$ready('Bookmarklet, step 1')
    })
  }
}
</script>
