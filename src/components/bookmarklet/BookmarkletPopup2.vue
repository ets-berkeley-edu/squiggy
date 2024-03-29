<template>
  <v-container v-if="isAuthorized && !isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <PageTitle text="Add the current page" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="2">
        <label class="float-right" for="asset-url">URL</label>
      </v-col>
      <v-col cols="10">
        <span id="asset-url">{{ asset.url }}</span>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="2">
        <label class="float-right" for="asset-title-input">
          Title
          <font-awesome-icon
            aria-label="Icon indicates required field"
            class="deep-orange--text icon-denotes-required"
            icon="asterisk"
            size="xs"
          />
        </label>
      </v-col>
      <v-col cols="10">
        <v-text-field
          id="asset-title-input"
          v-model="asset.title"
          maxlength="255"
          outlined
          required
        />
      </v-col>
    </v-row>
    <v-row v-if="categories.length">
      <v-col cols="2">
        <label class="float-right" for="asset-category-select">Category</label>
      </v-col>
      <v-col cols="10">
        <AccessibleSelect
          id-prefix="asset-category"
          :items="categories"
          item-text="title"
          item-value="id"
          label="Select..."
          :value="asset.categoryId"
          @input="c => (asset.categoryId = c)"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="2">
        <label class="float-right" for="asset-description-textarea">Description</label>
      </v-col>
      <v-col cols="10">
        <div class="d-flex flex-column flex-column-reverse">
          <div class="caption">Add some more context to your link. You can use plain text or #keywords</div>
          <div>
            <v-textarea
              id="asset-description-textarea"
              v-model="asset.description"
              hide-details
              outlined
            />
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row justify="end" no-gutters>
      <v-col class="pt-5">
        <BookmarkletButtons
          :disable-save="!$_.trim(asset.title).length"
          :is-saving="isSaving"
          :on-click-save="onClickSave"
          :previous-step="1"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'
import {createLinkAsset} from '@/api/assets'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context, Utils],
  components: {AccessibleSelect, BookmarkletButtons, PageTitle},
  data: () => ({
    asset: undefined,
    isSaving: false
  }),
  created() {
    this.asset = {
      categoryId: undefined,
      description: this.targetPage.metadata.description,
      title: this.targetPage.metadata.title,
      url: this.targetPage.metadata.url
    }
    this.$ready('Bookmarklet ready')
  },
  methods: {
    onClickSave() {
      this.$announcer.polite('Creating asset...')
      this.isSaving = true
      createLinkAsset(
        this.asset.categoryId,
        this.asset.description,
        this.asset.title,
        this.asset.url
      ).then(asset => {
        this.setAssetsCreated([asset])
        this.$announcer.polite('Link asset created.')
        this.go('/bookmarklet/popup/5')
        this.isSaving = false
      })
    }
  }
}
</script>
