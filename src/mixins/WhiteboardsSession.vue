<script>
import Context from '@/mixins/Context'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'WhiteboardsSession',
  mixins: [Context],
  computed: {
    ...mapGetters('whiteboards', [
      'whiteboards',
      'whiteboardType',
      'collaborators',
      'collaborator',
      'expanded',
      'isDirty',
      'keywords',
      'limit',
      'orderBy',
      'orderByDefault',
      'totalWhiteboardCount',
      'userId',
      'users'
    ])
  },
  methods: {
    updateSearchBookmark() {
      this.rewriteBookmarkHash({
        collaborator: this.collaborator,
        keywords: this.keywords,
        orderBy: this.orderBy,
        userId: this.userId
      })
    },
    ...mapActions('whiteboards', [
      'init',
      'nextPage',
      'resetSearch',
      'search',
      'setCollaborator',
      'setExpanded',
      'setKeywords',
      'setOrderBy',
      'setUserId',
      'updateWhiteboardStore'
    ])
  }
}
</script>
