<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary />

    <v-form @submit="submit">
      <v-container class="mt-2" fluid>
        <v-row justify="start">
          <v-col>
            <h2>Add a Link</h2>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-7 text-right" cols="2">
            URL
          </v-col>
          <v-col cols="6">
            <v-text-field
              id="asset-url-input"
              v-model="url"
              label="Paste or type a URL here"
              maxlength="255"
              outlined
              @keydown.enter="submit"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-7 text-right" cols="2">
            Title
          </v-col>
          <v-col cols="6">
            <v-text-field
              id="asset-title-input"
              v-model="title"
              label="Enter a title"
              maxlength="255"
              outlined
              @keydown.enter="submit"
            />
          </v-col>
        </v-row>
        <v-row v-if="categories.length">
          <v-col class="pt-7 text-right" cols="2">
            Category
          </v-col>
          <v-col cols="6">
            <v-select
              id="asset-category-select"
              v-model="categoryId"
              :items="categories"
              label="What assignment or topic is this related to"
              item-text="title"
              item-value="id"
              outlined
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-7 text-right" cols="2">
            Description
          </v-col>
          <v-col cols="6">
            <v-textarea
              id="asset-description-textarea"
              v-model="description"
              outlined
              placeholder="Add some more context to your link. You can use plain text or #keywords"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex flex-row-reverse">
              <div>
                <v-btn
                  id="add-link-btn"
                  color="primary"
                  :disabled="disable"
                  elevation="1"
                  @click="submit"
                >
                  Add Link
                </v-btn>
              </div>
              <div class="pr-2">
                <v-btn id="add-link-cancel-btn" elevation="1" @click="go('/assets')">Cancel</v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {createLinkAsset} from '@/api/assets'
import {getCategories} from '@/api/categories'

export default {
  name: 'AddLinkAsset',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    categories: undefined,
    categoryId: undefined,
    description: undefined,
    title: undefined,
    url: undefined,
    valid: true
  }),
  computed: {
    disable() {
      let required = [this.title, this.url]
      return !required.every(r => this.$_.trim(r))
    }
  },
  created() {
    this.$loading()
    getCategories().then(data => {
      this.categories = data
      this.$ready('Add a link asset')
    })
  },
  methods: {
    submit() {
      createLinkAsset(this.categoryId, this.description, this.title, this.url).then(() => {
        this.go('/assets')
      })
    }
  }
}
</script>
