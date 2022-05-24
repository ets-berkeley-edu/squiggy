<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary />

    <v-form v-model="linkAssetValid" @submit="submit">
      <v-container class="mt-2" fluid>
        <v-row justify="start">
          <v-col>
            <h2>Add a Link</h2>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-5 text-right" cols="2">
            <label for="asset-url-input">
              URL
              <font-awesome-icon
                aria-label="Icon indicates required field"
                class="deep-orange--text icon-denotes-required"
                icon="asterisk"
                size="xs"
              />
            </label>
          </v-col>
          <v-col cols="6">
            <v-text-field
              id="asset-url-input"
              v-model="url"
              label="Paste or type a URL here"
              outlined
              required
              :rules="urlRules"
              @blur="ensureUrlPrefix"
              @keydown.enter="submit"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-5 text-right" cols="2">
            <label for="asset-title-input">
              Title
              <font-awesome-icon
                aria-label="Icon indicates required field"
                class="deep-orange--text icon-denotes-required"
                icon="asterisk"
                size="xs"
              />
            </label>
          </v-col>
          <v-col cols="6">
            <v-text-field
              id="asset-title-input"
              v-model="title"
              label="Enter a title"
              outlined
              required
              :rules="titleRules"
              @keydown.enter="submit"
            />
          </v-col>
        </v-row>
        <v-row v-if="categories && categories.length">
          <v-col class="pt-5 text-right" cols="2">
            <label for="asset-category">Category</label>
          </v-col>
          <v-col cols="6">
            <AccessibleSelect
              id-prefix="asset-category"
              :items="categories"
              item-text="title"
              item-value="id"
              label="What assignment or topic is this related to"
              :value="categoryId"
              @input="c => (categoryId = c)"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-5 text-right" cols="2">
            <label for="asset-description-textarea">Description</label>
          </v-col>
          <v-col cols="6">
            <div class="d-flex flex-column flex-column-reverse">
              <div class="caption">Add some more context to your link. You can use plain text or #keywords</div>
              <div>
                <v-textarea
                  id="asset-description-textarea"
                  v-model="description"
                  hide-details
                  outlined
                />
              </div>
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex">
              <div class="pr-2">
                <v-btn
                  id="add-link-btn"
                  color="primary"
                  :disabled="!linkAssetValid"
                  elevation="1"
                  @click="submit"
                >
                  Add Link
                </v-btn>
              </div>
              <div>
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
import AccessibleSelect from '@/components/util/AccessibleSelect'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {createLinkAsset} from '@/api/assets'
import {getCategories} from '@/api/categories'

export default {
  name: 'AddLinkAsset',
  components: {AccessibleSelect, BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    categories: undefined,
    categoryId: undefined,
    description: undefined,
    linkAssetValid: false,
    title: '',
    titleRules: [
      v => !!v || 'Please enter a title',
      v => (!v || v.length <= 255) || 'Title must be 255 characters or less',
    ],
    url: '',
    urlRules: [
      v => !!v || 'Please enter a URL',
      v => (!v || v.length <= 255) || 'URL must be 255 characters or less',
    ]
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
    ensureUrlPrefix() {
      if (this.url && this.url.indexOf('://') === -1) {
        this.url = `https://${this.url}`
      }
    },
    submit() {
      this.ensureUrlPrefix()
      createLinkAsset(this.categoryId, this.description, this.title, this.url).then(() => {
        this.go('/assets')
      })
    }
  }
}
</script>
