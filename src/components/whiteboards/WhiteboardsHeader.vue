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
    <v-alert
      v-if="!$_.isNil(totalWhiteboardCount) && !totalWhiteboardCount"
      role="alert"
      outlined
      text
      type="success"
      elevation="2"
    >
      <router-link to="/whiteboard/create" class="hover-link">Create a whiteboard</router-link>. You currently have none.
    </v-alert>
    <!--
    <div data-ng-if="me.is_admin && (!me.course.active || me.course.reactivated)" data-ng-include="'/app/shared/syncdisabled.html'"></div>
    <whiteboards-search
      data-is-advanced-search="isAdvancedSearch"
      data-search-options-keywords="searchOptions.keywords"
      data-search-options-user="searchOptions.user"
      class="col-xs-{{ isAdvancedSearch ? 12 : 8 }} whiteboards-list-search-container"
    />
    <div role="alert" data-ng-if="popupBlocked">
      Your browser prevented us from opening the whiteboard. <strong><a target="_blank" data-ng-href="{{generateWhiteboardURL(deepLinkedWhiteboard)}}">Open the whiteboard.</a></strong>
    </div>
    <div v-if="!$_.isNil(totalWhiteboardCount) && !totalWhiteboardCount">
    </div>
    -->
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
                :items="$_.map($config.orderByOptions, (text, value) => ({text, value}))"
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
              <div v-if="$_.trim(keywords) || userId || (orderBy !== orderByDefault)" class="pl-2">
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
    <Alert
      v-if="alert"
      id="assert-library-alert"
      class="my-2"
      :messages="[alert]"
      :type="alertType"
      width="auto"
    />
  </div>
  <!--
  <div>
    <div>

>>>> SIMPLE SEARCH <<<<

      <div data-ng-show="!isAdvancedSearch">
        <form class="form-inline search-form" name="whiteboardsSearchForm" data-ng-submit="search()">
          <label for="whiteboards-search" class="sr-only">Search Whiteboards</label>
          <div class="input-group search-container">
            <input type="text" id="whiteboards-search" class="form-control" placeholder="Search" data-ng-model="keywords">
            <button class="btn btn-link search-advanced" title="Advanced search" type="button" data-ng-click="showAdvancedView()">
              <i class="fa fa-caret-down">
                <span class="sr-only">Advanced search</span>
              </i>
            </button>
            <span class="input-group-btn">
              <button type="submit" class="btn btn-default" title="Search">
                <i class="fa fa-search">
                  <span class="sr-only">Search</span>
                </i>
              </button>
            </span>
          </div>
        </div>
      </form>

>>>> ADVANCED SEARCH <<<<

      <div data-ng-show="isAdvancedSearch" class="col-pane">
        <form name="whiteboardsSearchAdvancedForm" class="form-horizontal search-advancedform" data-ng-submit="search()" novalidate>

>>>> SEARCH <<<<

          <div class="form-group">
            <label for="whiteboards-search-keywords" class="col-sm-1 control-label">Search</label>
            <div class="col-sm-11">
              <input type="text" id="whiteboards-search-keywords" data-ng-model="keywords" name="whiteboardsSearchKeywords" class="form-control" placeholder="Keyword" data-ng-maxlength="255">
            </div>
          </div>

>>>> FILTER BY <<<<

          <div class="form-group">
            <label for="whiteboards-search-user" class="col-sm-1 control-label">Filter by</label>
            <div class="col-sm-4">
              <select id="whiteboards-search-user" class="form-control" data-ng-model="user" data-value="{{user}}" data-ng-options="user.id as user.canvas_full_name for user in users">
                <option value="" selected>Collaborator</option>
              </select>
            </div>
          </div>

>>>> INCLUDE DELETED <<<<

          <div class="form-group">
            <div class="col-sm-1"></div>
            <div class="col-sm-7">
              <input id="whiteboards-search-include-deleted" type="checkbox" class="form-checkbox" data-ng-model="includeDeleted">
              <label for="whiteboards-search-include-deleted">Include deleted whiteboards</label>
            </div>
          </div>

>>>> BUTTONS <<<<

          <div class="form-group text-right">
            <div class="col-sm-offset-1 col-sm-11">
              <a class="btn btn-default" data-ng-click="showSimpleView()">Cancel</a>
              <button type="submit" class="btn btn-primary">Search</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
  -->
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
    isBusy: true,
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
      this.isBusy = false
    })
  },
  methods: {
    clearAlert() {
      this.alert = null
      this.alertType = null
    },
    fetch() {
      if (this.keywords || this.orderBy || this.userId) {
        this.resetSearch()
        this.isBusy = true
        this.$announcer.polite('Searching')
        this.search().then(data => {
          this.updateSearchBookmark()
          this.isBusy = false
          if (data.total) {
            this.$announcer.polite(`${data.total} matching ${data.total === 1 ? 'whiteboard' : 'whiteboards'} found`)
          } else {
            this.alertType = 'warning'
            this.alert = 'No matching whiteboards found'
          }
        })
      }
    },
    reset(expand, fetchAgain) {
      this.setOrderBy(this.orderByDefault)
      this.setUserId(null)
      this.rewriteBookmarkHash({orderBy: this.orderByDefault})
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
