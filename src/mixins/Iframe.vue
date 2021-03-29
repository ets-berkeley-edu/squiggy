<script>
import Vue from 'vue'

export default {
  name: 'Iframe',
  methods: {
    iframeParentLocation(location) {
      if (Vue.prototype.$isInIframe) {
        const message = JSON.stringify(
          {
            subject: 'changeParent',
            parentLocation: location
          }
        )
        this.iframePostMessage(message)
      }
    },
    iframePostMessage(message) {
      if (window.parent) {
        window.parent.postMessage(message, '*')
      }
    },
    iframeScrollToTop() {
      if (Vue.prototype.$isInIframe) {
        const message = JSON.stringify(
          {
            subject: 'changeParent',
            scrollToTop: true
          }
        )
        this.iframePostMessage(message)
      } else {
        window.scrollTo(0, 0)
      }
    }
  }
}
</script>
