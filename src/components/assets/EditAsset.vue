<template>
  <div v-if="!loading">
    <div>
      <v-btn
        id="asset-library-btn"
        class="bg-transparent"
        elevation="0"
        @click="go(`/asset/${assetId}`)"
        @keypress.enter="go(`/asset/${assetId}`)"
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
            <v-img alt="Image preview of the asset" :src="imageUrl" @error="imgError" />
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
              <v-select
                id="asset-category-select"
                v-model="category"
                :items="categories"
                label="Category"
                item-text="title"
                item-value="id"
                outlined
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
            >
              Save
            </v-btn>
            <v-btn id="cancel-delete-btn" class="mr-2" @click="cancel">
              Cancel
            </v-btn>
          </div>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset, updateAsset} from '@/api/assets'
import {getCategories} from '@/api/categories'

export default {
  name: 'EditAsset',
  mixins: [Context, Utils],
  data: () => ({
    assetId: undefined,
    categories: undefined,
    category: undefined,
    description: undefined,
    imageUrl: undefined,
    title: undefined,
    valid: true,
  }),
  created() {
    this.$loading()
    getAsset(this.$route.params.id).then(data => {
      this.assetId = data.id
      this.title = data.title
      this.description = data.description
      this.category = data.categories.length ? data.categories[0] : null
      this.imageUrl = data.imageUrl || require('@/assets/img-not-found.png')
      getCategories().then(data => {
        this.categories = data
        this.$ready(this.title)
      })
    })
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.go(`/asset/${this.assetId}`)
    },
    goBack() {
      this.go( `/asset/${this.assetId}`)
    },
    imgError() {
      this.imageUrl = require('@/assets/img-not-found.png')
    },
    submit() {
      updateAsset(this.assetId, this.category.id, this.description, this.title).then(data => {
        this.$announcer.polite(`${data.title} updated`)
        this.go(`/asset/${this.assetId}`)
      })
    }
  }
}
</script>
