<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Context',
  data: () => ({
    currentBrowser: undefined,
    isChrome: navigator.userAgent.match(/chrome|chromium|crios/i),
    isEdge: navigator.userAgent.match(/edg/i),
    isFirefox: navigator.userAgent.match(/firefox|fxios/i),
    isIE: !!document.documentMode,
    isSafari: window.navigator.userAgent.indexOf('Safari') !== -1 && window.navigator.userAgent.indexOf('Chrome') === -1
  }),
  computed: {
    ...mapGetters('context', [
      'isInIframe',
      'isLoading',
      'noSpinnerWhenLoading'
    ])
  },
  created() {
    const browsers = {chrome: this.isChrome, edge: this.isEdge, firefox: this.isFirefox, ie: this.isIE, safari: this.isSafari}
    this.currentBrowser = Object.keys(browsers).find(key => browsers[key])
  },
  methods: {
    ...mapActions('context', [
      'clearBookmarkHash',
      'getBookmarkHash',
      'rewriteBookmarkHash'
    ])
  }
}
</script>
