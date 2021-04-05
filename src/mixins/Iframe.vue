<script>
import store from '@/store'

export default {
  name: 'Iframe',
  methods: {
    iframeParentLocation(location) {
      if (store.getters['context/isInIframe']) {
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
      if (store.getters['context/isInIframe']) {
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
