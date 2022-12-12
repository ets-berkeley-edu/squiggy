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
                <span class="sr-only">{{ isAdvancedSearchOpen ? 'Hide' : 'Show' }} advanced search</span>
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
                <font-awesome-icon icon="search" size="lg" />
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
      <v-card v-if="isAdvancedSearchOpen" class="px-4 py-2">
        <v-container fluid>
          <v-row align="center" class="pb-2 pt-3" justify="start">
            <v-col class="pr-4 text-no-wrap text-right" cols="1">
              Search
            </v-col>
            <v-col class="py-0">
              <div class="pr-2">
                <v-text-field
                  id="adv-search-keywords-input"
                  clearable
                  height="44"
                  hide-details
                  solo
                  placeholder="Keyword"
                  type="search"
                  :value="keywords"
                  @input="setKeywords"
                  @keypress.enter="fetch"
                />
              </div>
            </v-col>
          </v-row>
          <v-row align="start" justify="start">
            <v-col class="pr-4 text-no-wrap text-right" cols="1">Filter by</v-col>
            <v-col class="py-0">
              <div class="align-content-start d-flex flex-wrap w-100">
                <div class="pb-2 w-50">
                  <div class="pr-2">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :dense="true"
                      :disabled="isBusy"
                      hide-details
                      id-prefix="adv-search-categories"
                      :items="categories"
                      item-text="title"
                      item-value="id"
                      label="Category"
                      :value="categoryId"
                      @input="setCategoryId"
                    />
                  </div>
                </div>
                <div class="pb-2 w-50">
                  <div class="pr-2">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :dense="true"
                      :disabled="isBusy"
                      hide-details
                      id-prefix="adv-search-asset-types"
                      :items="$_.map($config.assetTypes, t => ({text: $_.capitalize(t), value: t}))"
                      label="Asset type"
                      :value="assetType"
                      @input="setAssetType"
                    />
                  </div>
                </div>
                <div class="pb-2 w-50">
                  <div class="pr-2">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :dense="true"
                      :disabled="isBusy"
                      hide-details
                      id-prefix="adv-search-user"
                      :items="users"
                      item-text="canvasFullName"
                      item-value="id"
                      label="User"
                      :value="userId"
                      @input="setUserId"
                    />
                  </div>
                </div>
                <div v-if="$currentUser.isAdmin || $currentUser.isTeaching" class="pb-2 w-50">
                  <div class="pr-2">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :dense="true"
                      :disabled="isBusy"
                      hide-details
                      id-prefix="adv-search-section"
                      :items="$_.orderBy(sections, 'text')"
                      item-text="text"
                      item-value="value"
                      label="Section"
                      @input="setSection"
                    />
                  </div>
                </div>
                <div v-if="canvasGroups.length" class="pb-2 w-50">
                  <div class="pr-2">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :dense="true"
                      :disabled="isBusy"
                      id-prefix="adv-search-group-set"
                      :items="canvasGroups"
                      item-text="label"
                      item-value="id"
                      label="Group"
                      @input="setGroupId"
                    />
                  </div>
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row align="center" class="pb-3" justify="start">
            <v-col class="pr-4 text-no-wrap text-right" cols="1">
              Sort by
            </v-col>
            <v-col class="py-0">
              <div class="pr-3">
                <AccessibleSelect
                  :key="keyForSelectReset"
                  class="w-50"
                  :dense="true"
                  :disabled="isBusy"
                  hide-details
                  id-prefix="adv-search-order-by"
                  :items="$_.map($config.orderByOptions, (text, value) => ({text, value}))"
                  :unclearable="true"
                  :value="orderBy"
                  @input="setOrderBy"
                />
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="text-right" cols="1"></v-col>
            <v-col class="text-right">
              <div class="d-flex">
                <div class="pr-2">
                  <v-btn
                    id="adv-search-btn"
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
    afterReset: {
      default: () => {},
      required: false,
      type: Function
    },
    disableBookmarkable: {
      required: false,
      type: Boolean
    },
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
      if (this.assetType || this.categoryId || this.groupId || this.keywords || this.orderBy || this.section || this.userId) {
        this.resetSearch()
        this.isBusy = true
        this.$announcer.polite('Searching')
        this.search().then(data => {
          if (!this.disableBookmarkable) {
            this.updateSearchBookmark()
          }
          this.isBusy = false
          if (data.total) {
            this.$announcer.polite(`${data.total} matching ${data.total === 1 ? 'asset' : 'assets'} found`)
          } else {
            this.$announcer.polite('No assets found.')
            this.alertType = 'warning'
            this.alert = 'No matching assets found'
          }
        })
      }
    },
    reset(openAdvancedSearch, fetchAgain) {
      this.setAssetType(null)
      this.setCategoryId(null)
      this.setGroupId(null)
      this.setOrderBy(this.orderByDefault)
      this.setUserId(null)
      this.setSection(null)
      if (!this.disableBookmarkable) {
        this.rewriteBookmarkHash({orderBy: this.orderByDefault})
      }
      this.alert = null
      this.alertType = null
      this.openAdvancedSearchOverride = openAdvancedSearch
      if (this.isAdvancedSearchOpen === openAdvancedSearch) {
        this.setKeywords(undefined)
        this.keyForSelectReset = new Date().getTime()
      }
      if (fetchAgain) {
        this.fetch()
      }
      this.putFocus()
      this.$announcer.polite(`Advanced search form is ${openAdvancedSearch ? 'open' : 'closed'}.`)
      this.afterReset()
    },
    putFocus() {
      this.$putFocusNextTick(this.isAdvancedSearchOpen ? 'adv-search-keywords-input' : 'basic-search-input')
    }
  }
}
</script>
