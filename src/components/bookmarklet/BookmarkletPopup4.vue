<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>Add more information about the selected {{ selectedImages.length > 1 ? 'items' : 'item' }}</h1>
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
                  ></v-progress-circular>
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
              <label class="text--secondary" :for="`asset-category-select-${index}`">Category</label>
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
import Utils from '@/mixins/Utils'
import {createLinkAsset} from '@/api/assets'

export default {
  name: 'BookmarkletPopup4',
  mixins: [Bookmarklet, Context, Utils],
  components: {AccessibleSelect, BookmarkletButtons},
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
    this.$ready('Ready')
  },
  methods: {
    onClickSave() {
      this.isSaving = true
      this.$_.each(this.assets, asset => {
        createLinkAsset(
          asset.categoryId,
          asset.description,
          asset.title,
          asset.src
        ).then(() => {
          this.$announcer.polite(`${this.assets.length} asset(s) created.`)
          this.closePopup()
          this.isSaving = false
        })
      })
    }
  }
}
</script>
