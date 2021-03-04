<template>
  <div v-if="!loading">
    <div>
      <v-btn
        id="asset-library-btn"
        class="bg-transparent"
        elevation="0"
        @click="go('/assets')"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to Asset Library
      </v-btn>
    </div>
    <v-container class="mt-2" fluid>
      <v-row justify="start">
        <v-col>
          <h2>Add Link</h2>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-7 text-right" cols="2">
          URL
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="url"
            label="Paste or type a URL here"
            maxlength="255"
            outlined
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-7 text-right" cols="2">
          Title
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="title"
            label="Enter a title"
            maxlength="255"
            outlined
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-7 text-right" cols="2">
          Category
        </v-col>
        <v-col cols="6">
          <v-select
            v-model="categoryId"
            :items="categories"
            label="What assignment or topic is this related to"
            item-text="title"
            item-value="id"
            outlined
          ></v-select>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-7 text-right" cols="2">
          Description
        </v-col>
        <v-col cols="6">
          <v-textarea
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
                color="primary"
                :disabled="disable"
                elevation="1"
                @click="submit"
              >
                Add Link
              </v-btn>
            </div>
            <div class="pr-2">
              <v-btn elevation="1" @click="go('/assets')">Cancel</v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getCategories} from '@/api/categories'
import {createLinkAsset} from '@/api/assets'

export default {
  name: 'AddLinkAsset',
  mixins: [Context, Utils],
  data: () => ({
    categories: undefined,
    categoryId: undefined,
    description: undefined,
    title: undefined,
    url: undefined
  }),
  computed: {
    disable() {
      let required = [this.categoryId, this.description, this.title, this.url]
      return !required.every(r => this.$_.trim(r))
    }
  },
  created() {
    getCategories().then(data => {
      this.categories = data
      this.$ready('Add a link asset')
    })
  },
  methods: {
    submit() {
      createLinkAsset(this.categoryId, this.description, this.title, this.url).then(() => {
        console.log('TODO: Go to asset page?')
      })
    }
  }
}
</script>
