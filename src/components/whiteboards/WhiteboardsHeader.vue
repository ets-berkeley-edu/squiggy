<template>
  <div>
    <div class="align-center d-flex justify-space-between py-3">
      <div>
        <h2>My whiteboards</h2>
      </div>
      <div>
        <v-btn
          id="done-btn"
          color="primary"
          @click="$router.push('/whiteboard/create', $_.noop)"
          @keypress.enter="$router.push('/whiteboard/create', $_.noop)"
        >
          <font-awesome-icon class="mr-2" icon="plus" />
          <span class="sr-only">Create new </span>Whiteboard
        </v-btn>
      </div>
    </div>
    <div v-if="!$currentUser.isObserver && !$currentUser.isStudent">
      <v-expand-transition>
        <div v-if="!expanded" class="align-start d-flex justify-space-between w-50">
          <v-text-field
            id="basic-search-input"
            :value="keywords"
            clearable
            :disabled="isBusy"
            label="Search"
            solo
            type="search"
            @click:append-outer="fetch"
            @click:clear="onClickClearSearchInput"
            @input="setKeywords"
            @keypress.enter="fetch"
          >
            <template #append>
              <v-btn
                id="search-whiteboards-btn"
                class="ml-2"
                :disabled="isLoading || isBusy"
                icon
                @click="reset(!expanded)"
              >
                <font-awesome-icon icon="caret-down" />
                <span class="sr-only">{{ expanded ? 'Hide' : 'Show' }} advanced search</span>
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
                <span class="sr-only">Search whiteboards</span>
              </v-btn>
            </template>
          </v-text-field>
        </div>
      </v-expand-transition>
      <v-expand-transition>
        <v-card v-if="expanded" class="pr-16">
          <v-container fluid>
            <v-row class="mb-4" no-gutters>
              <v-col class="pr-3 pt-4 text-right" cols="1">
                Search
              </v-col>
              <v-col>
                <v-text-field
                  id="adv-search-keywords-input"
                  clearable
                  :disabled="isLoading || isBusy"
                  height="50"
                  :hide-details="true"
                  placeholder="Keyword"
                  solo
                  type="search"
                  :value="keywords"
                  @input="setKeywords"
                  @keypress.enter="fetch"
                />
              </v-col>
            </v-row>
            <v-row class="mb-4" no-gutters>
              <v-col class="pr-3 pt-2 text-right" cols="1">Filter by</v-col>
              <v-col>
                <v-row no-gutters>
                  <v-col class="w-100">
                    <AccessibleSelect
                      :key="keyForSelectReset"
                      :disabled="isBusy"
                      id-prefix="adv-search-user"
                      :hide-details="true"
                      :items="users"
                      item-text="canvasFullName"
                      item-value="id"
                      label="Collaborator"
                      :value="userId"
                      @input="setUserId"
                    />
                  </v-col>
                </v-row>
              </v-col>
              <v-col class="pr-3 pt-2 text-right" cols="1">
                Sort by
              </v-col>
              <v-col>
                <AccessibleSelect
                  :key="keyForSelectReset"
                  :disabled="isBusy"
                  :hide-details="true"
                  id-prefix="adv-search-order-by"
                  :items="[
                    {
                      text: 'Most recent',
                      value: 'recent'
                    },
                    {
                      text: 'Collaborator',
                      value: 'collaborator'
                    }
                  ]"
                  :unclearable="true"
                  :value="orderBy"
                  @input="setOrderBy"
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="1"></v-col>
              <v-col cols="5">
                <v-checkbox
                  id="include-deleted-checkbox"
                  class="ma-0 pa-0"
                  label="Include deleted"
                  :value="includeDeleted"
                  @change="value => setIncludeDeleted(value)"
                />
              </v-col>
              <v-col class="d-flex justify-end pt-2" cols="6">
                <div class="pr-2">
                  <v-btn
                    id="adv-search-btn"
                    class="text-capitalize"
                    color="primary"
                    :disabled="isBusy || (!$_.trim(keywords) && !expanded)"
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
                <div v-if="isDirty" class="pl-2">
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
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-expand-transition>
    </div>
    <Alert
      v-if="alert && (isDirty || !totalWhiteboardCount)"
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
import WhiteboardsSearch from '@/mixins/WhiteboardsSearch'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'WhiteboardsHeader',
  components: {AccessibleSelect, Alert},
  mixins: [WhiteboardsSearch, Context, Utils],
  props: {
    putFocusOnLoad: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    alert: undefined,
    alertType: undefined,
    keyForSelectReset: new Date().getTime()
  }),
  watch: {
    expanded() {
      if (!this.isBusy) {
        this.$putFocusNextTick(this.expanded ? 'adv-search-keywords-input' : 'basic-search-input')
      }
    },
    isDirty() {
      this.clearAlert()
    }
  },
  created() {
    this.init().then(() => {
      this.setExpanded(this.orderBy !== this.orderByDefault && !!this.userId)
      if (this.putFocusOnLoad) {
        this.$putFocusNextTick(this.putFocusOnLoad)
      }
      this.setBusy(false)
    })
  },
  methods: {
    clearAlert() {
      this.alert = null
      this.alertType = null
    },
    fetch() {
      this.alert = undefined
      if (this.includeDeleted || this.$_.trim(this.keywords) || this.orderBy || this.userId) {
        this.setBusy(true)
        this.resetOffset()
        this.$announcer.polite('Searching')
        this.search().then(data => {
          this.updateSearchBookmark()
          this.setDirty(true)
          this.setBusy(false)
          if (data.total) {
            this.$announcer.polite(`${data.total} matching ${data.total === 1 ? 'whiteboard' : 'whiteboards'} found`)
          } else {
            this.alertType = 'warning'
            this.alert = 'No matching whiteboards found'
          }
        })
      } else {
        this.setDirty(false)
      }
    },
    onClickClearSearchInput() {
      this.setKeywords(undefined)
      this.setIncludeDeleted(false)
      this.setOrderBy('recent')
      this.setUserId(undefined)
      this.fetch()
    },
    reset(expand, fetchAgain) {
      this.setOrderBy(this.orderByDefault)
      this.setUserId(null)
      this.setIncludeDeleted(false)
      this.rewriteBookmarkHash({orderBy: this.orderByDefault})
      this.setDirty(false)
      this.alert = null
      this.alertType = null
      if (this.expanded !== expand) {
        this.setExpanded(expand)
        this.$announcer.polite(`Advanced search form is ${this.expanded ? 'open' : 'closed'}.`)
      } else {
        this.setKeywords(undefined)
        this.keyForSelectReset = new Date().getTime()
      }
      if (fetchAgain) {
        this.fetch()
      }
      this.$putFocusNextTick(this.expanded ? 'keywords-input' : 'basic-search-input')
    },
  }
}
</script>
