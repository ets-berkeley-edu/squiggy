<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'InfiniteScrolling',
  mixins: [Context, Utils],
  data() {
    return {
      active: true,
      element: null,
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
        if (this.isInIframe && this.$supportsCustomMessaging) {
          this.getScrollInformation().then((scrollInformation) => {
            if (scrollInformation && scrollInformation.scrollToBottom) {
              this.handleInfiniteScrollLoad(scrollInformation.scrollToBottom)
            }
          })
        } else {
          this.handleInfiniteScrollLoad(this.element.scrollHeight - this.element.clientHeight - this.element.scrollTop)
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
      if (props.dialog) {
        // This brittle selector based on an internal Vuetify class name seems to be our current best shot, as we don't have a way
        // to pass an id through to the element.
        this.element = document.getElementsByClassName('v-dialog--active')[0]
      } else {
        this.element = document.documentElement
      }
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
