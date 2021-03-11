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
    <div>
      Edit details
    </div>
    <v-container>
      <v-row>
        <v-col>
          <v-img :src="imageUrl" width="50" />
        </v-col>
        <v-col>
          <div>
            Title
          </div>
          <div>
            <v-text-field
              id="asset-title-input"
              v-model="title"
              label="Enter a title"
              maxlength="255"
              outlined
              @keydown.enter="submit"
            />
          </div>
          <div>
            Category
          </div>
          <div>
            <v-select
              id="asset-category-select"
              v-model="categoryId"
              :items="categories"
              label="What assignment or topic is this related to"
              item-text="title"
              item-value="id"
              outlined
            />
          </div>
          <div>
            Description
          </div>
          <div>
            <v-textarea
              id="asset-description-textarea"
              v-model="description"
              outlined
              placeholder="Add some more context to your link. You can use plain text or #keywords"
            />
          </div>
        </v-col>
      </v-row>
    </v-container>
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
    categoryId: undefined,
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
      this.categoryId = data.categories.length ? data.categories[0] : null
      this.imageUrl = data.imageUrl || require('@/assets/img-not-found.png')
      getCategories().then(data => {
        this.categories = data
        this.$ready(this.title)
      })
    })
  },
  methods: {
    submit() {
      updateAsset(this.assetId, this.categoryId, this.description, this.title).then(data => {
        this.$announcer.polite(`${this.title} updated`)
        this.go(`/asset/${data.id}`)
      })
    },
    goBack() {
      this.go( `/asset/${this.assetId}`)
    }
  }
}
</script>
