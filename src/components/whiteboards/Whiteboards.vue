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
        <!--        <v-btn @click data-ng-href="/whiteboards/create">-->
        <!--          <i class="fa fa-plus-circle"></i>-->
        <!--          <span class="sr-only">Add </span>-->
        <!--          <span>Whiteboard</span>-->
        <!--        </v-btn>-->
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
    <div data-ng-if="me.is_admin && (!me.course.active || me.course.reactivated)" data-ng-include="'/app/shared/syncdisabled.html'"></div>
    <div v-if="!$_.isNil(totalWhiteboardCount) && !totalWhiteboardCount">
      <!-- SEARCH -->
      <WhiteboardSearch />
      <!--
      <whiteboards-search
        data-is-advanced-search="isAdvancedSearch"
        data-search-options-keywords="searchOptions.keywords"
        data-search-options-user="searchOptions.user"
        class="col-xs-{{ isAdvancedSearch ? 12 : 8 }} whiteboards-list-search-container"></whiteboards-search>
      -->
    </div>
    <!--
    <div role="alert" data-ng-if="popupBlocked">
      Your browser prevented us from opening the whiteboard. <strong><a target="_blank" data-ng-href="{{generateWhiteboardURL(deepLinkedWhiteboard)}}">Open the whiteboard.</a></strong>
    </div>
    -->

    <v-card class="d-flex flex-wrap" flat tile>
      <WhiteboardCard
        v-for="(whiteboard, index) in whiteboardGrid"
        :key="index"
        :whiteboard="whiteboard"
        class="whiteboard-card ma-3"
      />
    </v-card>
    <!--
    <div
      data-infinite-scroll="getWhiteboards()"
      data-infinite-scroll-ready="list.ready"
      data-infinite-scroll-distance="400" data-infinite-scroll-container="window">
      <ul>
        <li class="list-inline col-xs-6 col-sm-4 col-md-3" data-ng-repeat="whiteboard in whiteboards">
          <div class="col-list-item-container">
            <a target="_blank" data-ng-href="{{generateWhiteboardURL(whiteboard)}}">
              <div class="col-list-item-tile">
                <img class="img-responsive" data-ng-src="{{whiteboard.thumbnail_url}}" data-ng-if="whiteboard.thumbnail_url">
                <div class="text-center col-list-item-thumbnail-default" data-ng-if="!whiteboard.thumbnail_url">
                  <i class="fa fa-calendar-o"></i>
                </div>
                <div class="col-list-item-metadata" data-ng-class="{'col-list-item-metadata-deleted': whiteboard.deleted_at}">
                  <span class="col-threedots">{{whiteboard.title}}</span>
                  <small class="col-threedots" data-ng-if="!whiteboard.deleted_at">{{whiteboard.online_count}} online</small>
                  <small class="col-threedots" data-ng-if="whiteboard.deleted_at">Deleted</small>
                </div>
              </div>
            </a>
          </div>
        </li>
      </ul>
    </div>
    -->

    <!--
    <div class="alert alert-info whiteboards-list-alert" data-ng-if="hasRequested && whiteboards.length === 0">
      <span data-ng-if="!isSearch">
        You don't have any whiteboards yet. <strong><a data-ng-href="/whiteboards/create">Create your first whiteboard</a></strong>
      </span>
      <span data-ng-if="isSearch">
        No matching whiteboards were found.
      </span>
    </div>
    -->
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import InfiniteScrolling from '@/mixins/InfiniteScrolling'
import Utils from '@/mixins/Utils'
import WhiteboardCard from '@/components/whiteboards/WhiteboardCard'
import WhiteboardsSession from '@/mixins/WhiteboardsSession'
import WhiteboardSearch from '@/components/whiteboards/WhiteboardSearch'

export default {
  name: 'Whiteboards',
  mixins: [Context, InfiniteScrolling, Utils, WhiteboardsSession],
  components: {WhiteboardCard, WhiteboardSearch},
  data: () => ({
    anchor: null,
    isComplete: false
  }),
  computed: {
    whiteboardGrid() {
      this.$nextTick(this.resizeIFrame)
      if (this.isLoading) {
        return this.getSkeletons(20)
      } else if (this.isComplete) {
        return this.whiteboards
      } else {
        let skeletonCount = 10
        if (this.totalWhiteboardCount && (this.totalWhiteboardCount - this.whiteboards.length) < skeletonCount) {
          skeletonCount = Math.max(0, this.totalWhiteboardCount - this.whiteboards.length)
        }
        return this.whiteboards.concat(this.getSkeletons(skeletonCount))
      }
    }
  },
  created() {
    this.$loading(true)
  },
  mounted() {
    this.anchor = this.$route.query.anchor
    this.isReturning = this.anchor && this.$_.size(this.whiteboards)
    if (this.isReturning) {
      this.handleResults()
    } else {
      this.resetSearch()
      this.isComplete = false
      this.stopInfiniteLoading()
      this.getBookmarkHash().then(bookmarkHash => {
        if (bookmarkHash && Object.keys(bookmarkHash).length) {
          this.setWhiteboardType(bookmarkHash.whiteboardType)
          this.setCategoryId(bookmarkHash.categoryId)
          this.setOrderBy(bookmarkHash.orderBy)
          this.setUserId(parseInt(bookmarkHash.userId, 10))
          this.$announcer.polite('Searching for matching whiteboards')
          this.search().then(data => {
            this.handleResults(data, true)
          })
        } else if (this.$route.query.userId) {
          this.setWhiteboardType(undefined)
          this.setCategoryId(undefined)
          this.setUserId(parseInt(this.$route.query.userId, 10))
          this.$router.replace({query: {userId: undefined}})
          this.$announcer.polite('Searching for whiteboards by user')
          this.search().then(data => {
            this.updateSearchBookmark()
            this.handleResults(data, true)
          })
        } else if (this.$route.query.categoryId) {
          this.setWhiteboardType(undefined)
          this.setCategoryId(parseInt(this.$route.query.categoryId, 10))
          this.setUserId(undefined)
          this.$router.replace({query: {categoryId: undefined}})
          this.$announcer.polite('Searching for whiteboards by category')
          this.search().then(data => {
            this.updateSearchBookmark()
            this.handleResults(data, true)
          })
        } else {
          this.search().then(this.handleResults)
        }
      })
    }
  },
  methods: {
    fetch() {
      return this.nextPage().then(data => {
        if (data.results.length) {
          this.$announcer.polite(`${this.whiteboards.length} of ${this.totalWhiteboardCount} whiteboards loaded.`)
        } else {
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalWhiteboardCount} whiteboards have loaded.`)
        }
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    handleResults(data, isSearching) {
      const whiteboardTotal = data ? data.total : this.totalWhiteboardCount
      this.isComplete = data ? !data.results.length : (this.whiteboards.length === this.totalWhiteboardCount)

      let announcement = null
      if (this.isReturning) {
        announcement = 'Returning to Whiteboard Library'
      } else if (isSearching) {
        announcement = `${whiteboardTotal} matching ${whiteboardTotal === 1 ? 'whiteboard' : 'whiteboards'} found`
      }
      this.$ready('Whiteboard Library', null, announcement)

      if (!this.isComplete) {
        this.startInfiniteLoading(this.fetch, {threshold: 800})
      }
      if (this.anchor) {
        this.scrollTo(`#${this.anchor}`)
        this.$putFocusNextTick(this.anchor)
      }
    }
  }
}
</script>

<style scoped>
.whiteboard-card {
  height: 270px !important;
  width: 236px !important;
}
</style>
