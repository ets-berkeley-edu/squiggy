<script>
import Context from '@/mixins/Context'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'WhiteboardsSearch',
  mixins: [Context],
  computed: {
    ...mapGetters('whiteboards', [
      'whiteboards',
      'collaborators',
      'collaborator',
      'expanded',
      'includeDeleted',
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
      'refresh',
      'resetSearch',
      'search',
      'setCollaborator',
      'setExpanded',
      'setIncludeDeleted',
      'setKeywords',
      'setOrderBy',
      'setUserId',
      'updateWhiteboardStore'
    ])
  }
}
</script>
