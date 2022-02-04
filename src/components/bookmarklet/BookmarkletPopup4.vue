<template>
  <v-container v-if="isAuthorized && !isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <PageTitle :text="`Add more information about the selected ${selectedImages.length > 1 ? 'items' : 'item'}`" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col
        v-for="(asset, index) in assets"
        :key="index"
        class="d-flex child-flex"
        cols="4"
      >
        <div class="d-flex flex-column">
          <div>
            <v-img
              :id="`image-${index}`"
              :alt="asset.title"
              aspect-ratio="1"
              class="grey lighten-2"
              :src="asset.src"
              :lazy-src="asset.src"
            >
              <template #placeholder>
                <v-row
                  class="fill-height ma-0"
                  align="center"
                  justify="center"
                >
                  <v-progress-circular
                    indeterminate
                    color="grey lighten-5"
                  />
                </v-row>
              </template>
            </v-img>
          </div>
          <div class="px-2">
            <div class="py-2">
              <label class="text--secondary" :for="`asset-title-input-${index}`">Title</label>
              <v-text-field
                :id="`asset-title-input-${index}`"
                v-model="asset.title"
                dense
                :hide-details="true"
                maxlength="255"
                outlined
                required
              />
            </div>
            <div v-if="categories.length" class="pb-2">
              <label class="text--secondary" :for="`asset-category-select-${index}-select`">Category</label>
              <AccessibleSelect
                :dense="true"
                :hide-details="true"
                :id-prefix="`asset-category-select-${index}`"
                :items="categories"
                item-text="title"
                item-value="id"
                label="Select..."
                :value="asset.categoryId"
                @input="c => (asset.categoryId = c)"
              />
            </div>
            <div class="pb-8">
              <label class="text--secondary" :for="`asset-description-textarea-${index}`">Description</label>
              <v-textarea
                :id="`asset-description-textarea-${index}`"
                v-model="asset.description"
                dense
                hide-details
                outlined
              />
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col class="pt-5">
        <BookmarkletButtons
          :disable-save="disableSave"
          :is-saving="isSaving"
          :on-click-save="onClickSave"
          :previous-step="3"
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
import {bookmarkletCreateFileAsset} from '@/api/assets'

export default {
  name: 'BookmarkletPopup4',
  mixins: [Bookmarklet, Context, Utils],
  components: {AccessibleSelect, BookmarkletButtons, PageTitle},
  computed: {
    disableSave() {
      return !!this.$_.find(this.assets, image => {
        return !this.$_.trim(image.title).length
      })
    }
  },
  data: () => ({
    assets: undefined,
    isSaving: false
  }),
  created() {
    this.assets = this.$_.cloneDeep(this.selectedImages)
    this.$ready('Bookmarklet ready')
    this.$announcer.polite(`The page has ${this.assets.length} assets`)
  },
  methods: {
    onClickSave() {
      const snippet = `${this.assets.length} ${this.assets.length === 1 ? 'asset' : 'assets'}`
      this.$announcer.polite(`Creating ${snippet}...`)
      this.isSaving = true
      const apiCalls = []
      this.$_.each(this.assets, asset => {
        apiCalls.push(bookmarkletCreateFileAsset(
          asset.categoryId,
          asset.description,
          asset.title,
          asset.src
        ))
      })
      Promise.all(apiCalls).then(assets => {
        this.setAssetsCreated(assets)
        this.$announcer.polite(`${snippet} created.`)
        this.isSaving = false
        this.go('/bookmarklet/popup/5')
      })
    }
  }
}
</script>
