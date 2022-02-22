<template>
  <div>
    <WhiteboardsHeader :put-focus-on-load="anchor ? null : 'basic-search-input'" />
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
import WhiteboardsSearch from '@/mixins/WhiteboardsSearch'
import WhiteboardsHeader from '@/components/whiteboards/WhiteboardsHeader'

export default {
  name: 'Whiteboards',
  mixins: [Context, InfiniteScrolling, Utils, WhiteboardsSearch],
  components: {WhiteboardCard, WhiteboardsHeader},
  data: () => ({
    anchor: null,
    isComplete: false,
    refreshJob: undefined
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
  destroyed() {
    clearTimeout(this.refreshJob)
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
          this.setOrderBy(bookmarkHash.orderBy)
          this.setUserId(parseInt(bookmarkHash.userId, 10))
          this.$announcer.polite('Searching for matching whiteboards')
          this.search().then(() => {
            this.handleResults(true)
          })
        } else if (this.$route.query.userId) {
          this.setUserId(parseInt(this.$route.query.userId, 10))
          this.$router.replace({query: {userId: undefined}})
          this.$announcer.polite('Searching for whiteboards by user')
          this.search().then(() => {
            this.updateSearchBookmark()
            this.handleResults(true)
          })
        } else {
          this.search().then(this.handleResults)
        }
      })
    }
  },
  methods: {
    fetch() {
      return this.nextPage().then(() => {
        if (this.totalWhiteboardCount) {
          this.$announcer.polite(`${this.whiteboards.length} of ${this.totalWhiteboardCount} whiteboards loaded.`)
        } else {
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalWhiteboardCount} whiteboards have loaded.`)
        }
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    handleResults(isSearching) {
      if (this.isReturning) {
        this.$ready('Whiteboards', null, 'Returning to Whiteboards')
      } else {
        const label = this.totalWhiteboardCount === 1 ? 'whiteboard' : 'whiteboards'
        const announce = isSearching ? `${this.totalWhiteboardCount} matching ${label} found` : null
        this.$ready('Whiteboards', null, announce)
      }
      this.isComplete = this.whiteboards.length === this.totalWhiteboardCount
      if (!this.isComplete) {
        this.startInfiniteLoading(this.fetch, {threshold: 800})
      }
      if (this.anchor) {
        this.scrollTo(`#${this.anchor}`)
        this.$putFocusNextTick(this.anchor)
      }
      this.scheduleRefreshJob()
    },
    scheduleRefreshJob() {
      clearTimeout(this.refreshJob)
      this.refreshJob = setTimeout(this.refresh, this.$config.whiteboardsRefreshInterval)
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
