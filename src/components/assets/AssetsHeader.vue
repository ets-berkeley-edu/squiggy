<template>
  <div>
    <div v-if="!expanded" class="align-start d-flex justify-space-between">
      <div class="w-50">
        <v-text-field
          id="basic-search-input"
          v-model="keywords"
          clearable
          :disabled="isSearching"
          label="Search"
          solo
          type="search"
          @click:append-outer="fetch"
        >
          <template #append>
            <v-btn
              id="search-assets-btn"
              class="ml-2"
              :disabled="isSearching"
              icon
              @click="toggle"
            >
              <font-awesome-icon icon="caret-down" />
            </v-btn>
          </template>
          <template #append-outer>
            <v-btn
              id="search"
              class="mb-2"
              :disabled="isSearching || (!$_.trim(keywords) && !expanded)"
              icon
            >
              <font-awesome-icon
                class="mb-3"
                icon="search"
                size="lg"
              />
            </v-btn>
          </template>
        </v-text-field>
      </div>
      <div>
        <v-btn
          elevation="2"
          :disabled="isSearching"
          large
          @click="go('/assets/manage')"
          @keypress.enter="go('/assets/manage')"
        >
          <span class="pr-2">
            <font-awesome-icon icon="cog" />
          </span>
          Manage Assets
        </v-btn>
      </div>
    </div>
    <v-expand-transition>
      <v-container v-if="expanded" fluid>
        <v-row>
          <v-col cols="2">Search</v-col>
          <v-col>
            <v-text-field
              id="adv-search-keywords-input"
              v-model="keywords"
              placeholder="Keyword"
              type="search"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">Filter by</v-col>
          <v-col>
            <v-row>
              <v-col>
                <v-select
                  v-model="categoryId"
                  :items="categories"
                  label="Category"
                  item-text="title"
                  item-value="id"
                  outlined
                />
              </v-col>
              <v-col>
                <v-select
                  v-model="assetType"
                  :items="$_.map($config.assetTypes, t => ({text: $_.capitalize(t), value: t}))"
                  label="Asset type"
                  outlined
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-select
                  v-model="userId"
                  :items="users"
                  label="User"
                  item-text="canvasFullName"
                  item-value="id"
                  outlined
                />
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">
            Sort by
          </v-col>
          <v-col>
            <v-select
              v-model="orderBy"
              :items="$_.map($config.orderByOptions, (text, value) => ({text, value}))"
              outlined
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex flex-row-reverse">
              <div>
                <v-btn
                  id="adv-search-assets-btn"
                  color="primary"
                  :disabled="isSearching || (!$_.trim(keywords) && !expanded)"
                  elevation="1"
                  @click="fetch"
                >
                  Search
                </v-btn>
              </div>
              <div class="pr-2">
                <v-btn :disabled="isSearching" elevation="1" @click="toggle">Cancel</v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-expand-transition>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import AssetsSearch from '@/mixins/AssetsSearch'

export default {
  name: 'AssetsHeader',
  mixins: [AssetsSearch, Utils],
  props: {
    categories: {
      required: true,
      type: Array
    },
    users: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    assetType: undefined,
    categoryId: undefined,
    expanded: false,
    keywords: undefined,
    isSearching: false,
    orderBy: 'recent',
    userId: undefined
  }),
  watch: {
    expanded() {
      this.assetType = null
      this.categoryId = null
      this.orderBy = 'recent'
      this.userId = null
    }
  },
  methods: {
    toggle() {
      this.expanded = !this.expanded
      this.$announcer.polite(`Advanced search form is ${this.expanded ? 'open' : 'closed'}.`)
      this.$putFocusNextTick(this.expanded ? 'keywords-input' : 'basic-search-input')
    },
    fetch() {
      this.isSearching = true
      this.search({
        assetType: this.assetType,
        categoryId: this.categoryId,
        keywords: this.keywords,
        orderBy: this.orderBy,
        userId: this.userId
      }).then(() => {
        this.isSearching = false
      })
    }
  }
}
</script>
