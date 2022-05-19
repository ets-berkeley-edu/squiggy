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
    isRefreshing: false,
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
    document.addEventListener('visibilitychange', this.onVisibilityChange)
    this.$loading(true)
  },
  destroyed() {
    document.removeEventListener('visibilitychange', this.onVisibilityChange)
    clearTimeout(this.refreshJob)
  },
  mounted() {
    this.anchor = this.$route.query.anchor
    this.isReturning = this.anchor && this.$_.size(this.whiteboards)
    if (this.isReturning) {
      this.handleResults()
    } else {
      this.setOffset(0)
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
        this.isComplete = this.whiteboards.length >= this.totalWhiteboardCount
        if (this.isComplete) {
          this.$announcer.polite(`All ${this.totalWhiteboardCount} whiteboards have loaded.`)
        } else {
          this.$announcer.polite(`${this.whiteboards.length} of ${this.totalWhiteboardCount} whiteboards loaded.`)
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
    onVisibilityChange() {
      if (document.visibilityState === 'visible') {
        clearTimeout(this.refreshJob)
        // We want to refresh all whiteboards visible to the user.
        const previousOffset = this.offset
        this.setOffset(0)
        this.search().then(() => {
          this.setOffset(previousOffset)
          this.scheduleRefreshJob()
        })
      }
    },
    runRefresh() {
      const run = !this.isRefreshing && (!this.isBusy || !this.$_.trim(this.keywords) || !this.orderBy || !this.userId)
      if (run) {
        this.isRefreshing = true
        this.refresh().then(() => {
          this.scheduleRefreshJob()
          this.isRefreshing = false
        })
      }
    },
    scheduleRefreshJob() {
      clearTimeout(this.refreshJob)
      this.refreshJob = setTimeout(this.runRefresh, this.$config.whiteboardsRefreshInterval)
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
