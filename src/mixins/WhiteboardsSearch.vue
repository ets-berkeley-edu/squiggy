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
      'isBusy',
      'isDirty',
      'keywords',
      'limit',
      'offset',
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
      'search',
      'setBusy',
      'setCollaborator',
      'setDirty',
      'setExpanded',
      'setIncludeDeleted',
      'setKeywords',
      'setOffset',
      'setOrderBy',
      'setUserId',
      'updateWhiteboardStore'
    ])
  }
}
</script>
