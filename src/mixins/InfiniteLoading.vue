<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'InfiniteLoading',
  mixins: [Context, Utils],
  data() {
    return {
      active: true,
      infiniteScrollInterval: null,
      loadFunction: undefined,
      loading: false,
      threshold: 500,
    }
  },
  activated() {
    this.active = true
  },
  deactivated() {
    this.active = false
  },
  methods: {
    checkInfiniteScrollLoad() {
      if (!this.isComplete) {
        if (this.isInIframe) {
          this.getScrollInformation().then((scrollInformation) => {
            if (scrollInformation && scrollInformation.scrollToBottom) {
              this.handleInfiniteScrollLoad(scrollInformation.scrollToBottom)
            }
          })
        } else {
          const doc = document.documentElement
          this.handleInfiniteScrollLoad(doc.scrollHeight - doc.clientHeight - doc.scrollTop)
        }
      }
    },
    handleInfiniteScrollLoad(distance) {
      if (!this.loading && distance < this.threshold) {
        this.loading = true
        this.fetch().then(() => {
          this.loading = false
        })
      }
    },
    startInfiniteLoading(loadFunction, props) {
      this.loadFunction = loadFunction
      if (props.threshold) {
        this.threshold = props.threshold
      }
      this.infiniteScrollInterval = setInterval(this.checkInfiniteScrollLoad, 250)
    },
    stopInfiniteLoading() {
      clearInterval(this.infiniteScrollInterval)
    },
  },
  destroyed() {
    this.stopInfiniteLoading()
  },
}
</script>
