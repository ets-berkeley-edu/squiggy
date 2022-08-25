<template>
  <div>
    <h2 class="sr-only">Asset Library</h2>
    <v-expand-transition>
      <div v-if="!isAdvancedSearchOpen" class="align-start d-flex justify-space-between">
        <div class="w-50">
          <v-text-field
            id="basic-search-input"
            :value="keywords"
            clearable
            :disabled="isBusy"
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
                :disabled="isLoading || isBusy"
                icon
                @click="reset(!isAdvancedSearchOpen)"
              >
                <font-awesome-icon icon="caret-down" />
                <span class="sr-only">{{ isAdvancedSearchOpen ? 'Hide' : 'Show' }} Show advanced search</span>
              </v-btn>
            </template>
            <template #append-outer>
              <v-btn
                id="search-btn"
                class="mb-2"
                :disabled="isLoading || isBusy"
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
            v-if="!hideManageAssetsButton && ($currentUser.isAdmin || $currentUser.isTeaching)"
            id="manage-assets-btn"
            elevation="2"
            :disabled="isBusy"
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
    </v-expand-transition>
    <v-expand-transition>
      <v-card v-if="isAdvancedSearchOpen" class="mb-6 pl-8 pr-16 pt-4">
        <v-container fluid>
          <v-row no-gutters>
            <v-col class="pr-4 pt-2 text-right" cols="1">
              Search
            </v-col>
            <v-col>
              <v-text-field
                id="adv-search-keywords-input"
                clearable
                solo
                placeholder="Keyword"
                type="search"
                :value="keywords"
                @input="setKeywords"
                @keypress.enter="fetch"
              />
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="pr-4 pt-2 text-right" cols="1">Filter by</v-col>
            <v-col class="w-75">
              <v-row no-gutters>
                <v-col class="pr-2 w-50">
                  <AccessibleSelect
                    :key="keyForSelectReset"
                    :dense="true"
                    :disabled="isBusy"
                    id-prefix="adv-search-categories"
                    :items="categories"
                    item-text="title"
                    item-value="id"
                    label="Category"
                    :value="categoryId"
                    @input="setCategoryId"
                  />
                </v-col>
                <v-col class="w-50">
                  <AccessibleSelect
                    :key="keyForSelectReset"
                    :dense="true"
                    :disabled="isBusy"
                    id-prefix="adv-search-asset-types"
                    :items="$_.map($config.assetTypes, t => ({text: $_.capitalize(t), value: t}))"
                    label="Asset type"
                    :value="assetType"
                    @input="setAssetType"
                  />
                </v-col>
              </v-row>
              <v-row no-gutters>
                <v-col class="w-50">
                  <AccessibleSelect
                    :key="keyForSelectReset"
                    class="w-50"
                    :dense="true"
                    :disabled="isBusy"
                    id-prefix="adv-search-user"
                    :items="users"
                    item-text="canvasFullName"
                    item-value="id"
                    label="User"
                    :value="userId"
                    @input="setUserId"
                  />
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="pr-4 pt-2 text-right" cols="1">
              Sort by
            </v-col>
            <v-col>
              <AccessibleSelect
                :key="keyForSelectReset"
                class="w-50"
                :dense="true"
                :disabled="isBusy"
                id-prefix="adv-search-order-by"
                :items="$_.map($config.orderByOptions, (text, value) => ({text, value}))"
                :unclearable="true"
                :value="orderBy"
                @input="setOrderBy"
              />
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col class="text-right" cols="12">
              <div class="d-flex">
                <div class="pr-2">
                  <v-btn
                    id="adv-search-btn"
                    class="text-capitalize"
                    color="primary"
                    :disabled="isBusy || (!$_.trim(keywords) && !isAdvancedSearchOpen)"
                    elevation="1"
                    medium
                    @click="fetch"
                  >
                    Search
                  </v-btn>
                </div>
                <div>
                  <v-btn
                    id="cancel-adv-search-btn"
                    class="text-capitalize"
                    :disabled="isBusy"
                    elevation="1"
                    medium
                    @click="reset(false)"
                  >
                    Cancel
                  </v-btn>
                </div>
                <div v-if="assetType || categoryId || $_.trim(keywords) || userId || (orderBy !== orderByDefault)" class="pl-2">
                  <v-btn
                    id="reset-adv-search-btn"
                    class="text-capitalize"
                    :disabled="isBusy"
                    medium
                    text
                    @click="reset(true, true)"
                  >
                    Reset
                  </v-btn>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </v-expand-transition>
    <Alert
      v-if="alert"
      id="assert-library-alert"
      class="my-2"
      :messages="[alert]"
      :type="alertType"
      width="auto"
    />
  </div>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Alert from '@/components/util/Alert'
import AssetsSearch from '@/mixins/AssetsSearch'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetsHeader',
  components: {AccessibleSelect, Alert},
  mixins: [AssetsSearch, Context, Utils],
  props: {
    hideManageAssetsButton: {
      required: false,
      type: Boolean
    },
    openAdvancedSearch: {
      required: true,
      type: Boolean
    },
    putFocusOnLoad: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    alert: undefined,
    alertType: undefined,
    openAdvancedSearchOverride: false,
    isBusy: true,
    keyForSelectReset: new Date().getTime()
  }),
  computed: {
    isAdvancedSearchOpen() {
      return this.openAdvancedSearch || this.openAdvancedSearchOverride
    }
  },
  watch: {
    isDirty() {
      this.clearAlert()
    },
    openAdvancedSearch() {
      if (this.openAdvancedSearch) {
        this.openAdvancedSearchOverride = true
      }
      this.putFocus()
    }
  },
  created() {
    this.isBusy = false
    if (this.putFocusOnLoad) {
      this.$putFocusNextTick(this.putFocusOnLoad)
    }
  },
  methods: {
    clearAlert() {
      this.alert = null
      this.alertType = null
    },
    fetch() {
      if (this.assetType || this.categoryId || this.keywords || this.orderBy || this.userId) {
        this.resetSearch()
        this.isBusy = true
        this.$announcer.polite('Searching')
        this.search().then(data => {
          this.updateSearchBookmark()
          this.isBusy = false
          if (data.total) {
            this.$announcer.polite(`${data.total} matching ${data.total === 1 ? 'asset' : 'assets'} found`)
          } else {
            this.alertType = 'warning'
            this.alert = 'No matching assets found'
          }
        })
      }
    },
    reset(openAdvancedSearch, fetchAgain) {
      this.setAssetType(null)
      this.setCategoryId(null)
      this.setOrderBy(this.orderByDefault)
      this.setUserId(null)
      this.rewriteBookmarkHash({orderBy: this.orderByDefault})
      this.alert = null
      this.alertType = null
      this.openAdvancedSearchOverride = openAdvancedSearch
      if (this.isAdvancedSearchOpen !== openAdvancedSearch) {
        this.$announcer.polite(`Advanced search form is ${this.isAdvancedSearchOpen ? 'open' : 'closed'}.`)
      } else {
        this.setKeywords(undefined)
        this.keyForSelectReset = new Date().getTime()
      }
      if (fetchAgain) {
        this.fetch()
      }
      this.putFocus()
    },
    putFocus() {
      this.$putFocusNextTick(this.isAdvancedSearchOpen ? 'adv-search-keywords-input' : 'basic-search-input')
    }
  }
}
</script>
