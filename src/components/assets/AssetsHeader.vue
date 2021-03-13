<template>
  <div>
    <div v-if="!expanded" class="align-start d-flex justify-space-between">
      <div class="w-50">
        <v-text-field
          id="basic-search-input"
          :value="keywords"
          clearable
          :disabled="isSearching"
          label="Search"
          solo
          type="search"
          @click:append-outer="fetch"
          @input="setKeywords"
          @keypress.enter="fetch"
        >
          <template #append>
            <v-btn
              id="search-assets-btn"
              class="ml-2"
              :disabled="isLoading || isSearching"
              icon
              @click="toggle"
            >
              <font-awesome-icon icon="caret-down" />
              <span class="sr-only">{{ expanded ? 'Hide' : 'Show' }} advanced search</span>
            </v-btn>
          </template>
          <template #append-outer>
            <v-btn
              id="search-btn"
              class="mb-2"
              :disabled="isLoading || isSearching || (!$_.trim(keywords) && !expanded)"
              icon
              @click="fetch"
              @keypress.enter="fetch"
            >
              <font-awesome-icon
                class="mb-3"
                icon="search"
                size="lg"
              />
              <span class="sr-only">Search assets</span>
            </v-btn>
          </template>
        </v-text-field>
      </div>
      <div>
        <v-btn
          id="manage-assets-btn"
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
              placeholder="Keyword"
              type="search"
              :value="keywords"
              @input="setKeywords"
              @keypress.enter="fetch"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">Filter by</v-col>
          <v-col>
            <v-row>
              <v-col>
                <v-select
                  :items="categories"
                  item-text="title"
                  item-value="id"
                  label="Category"
                  outlined
                  :value="categoryId"
                  @input="setCategoryId"
                />
              </v-col>
              <v-col>
                <v-select
                  :items="$_.map($config.assetTypes, t => ({text: $_.capitalize(t), value: t}))"
                  label="Asset type"
                  outlined
                  :value="assetType"
                  @input="setAssetType"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-select
                  :items="users"
                  item-text="canvasFullName"
                  item-value="id"
                  label="User"
                  outlined
                  :value="userId"
                  @change="setUserId"
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
              :items="$_.map($config.orderByOptions, (text, value) => ({text, value}))"
              outlined
              :value="orderBy"
              @input="setOrderBy"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex flex-row-reverse">
              <div>
                <v-btn
                  id="adv-search-btn"
                  color="primary"
                  :disabled="isSearching || (!$_.trim(keywords) && !expanded)"
                  elevation="1"
                  @click="fetch"
                >
                  Search
                </v-btn>
              </div>
              <div class="pr-2">
                <v-btn
                  id="cancel-adv-search-btn"
                  :disabled="isSearching"
                  elevation="1"
                  @click="toggle"
                >
                  Cancel
                </v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-expand-transition>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import AssetsSearch from '@/mixins/AssetsSearch'

export default {
  name: 'AssetsHeader',
  mixins: [AssetsSearch, Context, Utils],
  props: {
    categories: {
      default: () => [],
      required: false,
      type: Array
    },
    users: {
      default: () => [],
      required: false,
      type: Array
    }
  },
  data: () => ({
    expanded: false,
    isSearching: false
  }),
  created() {
    this.expanded = !!(this.assetType || this.categoryId || (this.orderBy !== this.orderByDefault) || this.userId)
  },
  methods: {
    toggle() {
      this.setAssetType(null)
      this.setCategoryId(null)
      this.setOrderBy('recent')
      this.setUserId(null)
      this.expanded = !this.expanded
      this.$announcer.polite(`Advanced search form is ${this.expanded ? 'open' : 'closed'}.`)
      this.$putFocusNextTick(this.expanded ? 'keywords-input' : 'basic-search-input')
    },
    fetch() {
      if (this.assetType || this.categoryId || this.keywords || this.orderBy || this.userId) {
        this.isSearching = true
        this.search().then(() => {
          this.isSearching = false
        })
      }
    }
  }
}
</script>
