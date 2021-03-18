<template>
  <div v-if="!isLoading">
    <div v-if="asset">
      <v-btn
        id="asset-library-btn"
        class="bg-transparent"
        elevation="0"
        @click="go(`/asset/${asset.id}`)"
        @keypress.enter="go(`/asset/${asset.id}`)"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to Asset
      </v-btn>
    </div>
    <div class="ma-3">
      <div class="py-2">
        <h2>Edit details</h2>
      </div>
      <v-card class="pa-3" outlined>
        <v-list-item>
          <v-list-item-avatar class="align-self-start pa-3" size="320" tile>
            <AssetImage :asset="asset" />
          </v-list-item-avatar>
          <v-list-item-content>
            <div>
              <v-text-field
                id="asset-title-input"
                v-model="title"
                label="Title"
                maxlength="255"
                outlined
                @keydown.enter="submit"
              />
            </div>
            <div>
              <AccessibleSelect
                :clearable="true"
                :dense="true"
                id-prefix="asset-category"
                item-text="title"
                item-value="id"
                :items="categories"
                label="Category"
                :value="categoryId"
                @input="c => (categoryId = c)"
              />
            </div>
            <div>
              <v-textarea
                id="asset-description-textarea"
                v-model="description"
                auto-grow
                outlined
                placeholder="Description"
              />
            </div>
          </v-list-item-content>
        </v-list-item>
        <v-card-actions>
          <v-spacer />
          <div class="d-flex flex-row-reverse">
            <v-btn
              id="confirm-delete-btn"
              class="mr-2"
              color="primary"
              :disabled="!$_.trim(title)"
              @click="submit"
              @keypress.enter="submit"
            >
              Save
            </v-btn>
            <v-btn
              id="cancel-delete-btn"
              class="mr-2"
              @click="cancel"
              @keypress.enter="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import AssetImage from '@/components/assets/AssetImage'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset, updateAsset} from '@/api/assets'
import {getCategories} from '@/api/categories'

export default {
  name: 'EditAsset',
  components: {AccessibleSelect, AssetImage},
  mixins: [Context, Utils],
  data: () => ({
    asset: undefined,
    categories: undefined,
    categoryId: undefined,
    description: undefined,
    title: undefined,
    valid: true,
  }),
  created() {
    this.$loading()
    getAsset(this.$route.params.id).then(data => {
      this.asset = data
      this.title = data.title
      this.description = data.description
      // TODO: Do we need to support multiple-category-select?
      this.categoryId = data.categories.length ? data.categories[0].id : null
      getCategories().then(data => {
        this.categories = data
        this.$ready(this.title)
      })
    })
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.go(`/asset/${this.asset.id}`)
    },
    submit() {
      this.$announcer.polite('Updating asset')
      updateAsset(this.asset.id, this.categoryId, this.description, this.title).then(() => {
        this.go(`/asset/${this.asset.id}`)
      })
    }
  }
}
</script>
