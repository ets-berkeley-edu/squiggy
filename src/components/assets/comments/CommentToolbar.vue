<template>
  <div class="align-center d-flex justify-space-between w-100">
    <div :id="`comment-${comment.id}-user-name`">
      <UserLink :user="comment.user" source="assetlibrary" />
      on {{ comment.createdAt | moment('LL') }}
    </div>
  </div>
</template>

<script>
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'CommentToolbar',
  components: {UserLink},
  mixins: [Utils],
  props: {
    comment: {
      required: true,
      type: Object
    }
  }
}
</script>
