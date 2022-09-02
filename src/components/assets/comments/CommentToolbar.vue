<template>
  <div class="align-center d-flex justify-space-between w-100">
    <div :id="`comment-${comment.id}-user-name`">
      <UserLink :user="comment.user" source="assetlibrary" />
      on {{ comment.createdAt | moment('LL') }}
    </div>
    <div class="d-flex">
      <div v-if="!comment.parentId">
        <v-btn
          :id="`reply-to-comment-${comment.id}-btn`"
          :disabled="disableActions"
          icon
          @click="replyTo(comment)"
          @keypress.enter="replyTo(comment)"
        >
          <span class="sr-only">Reply to {{ getPossessive(comment) }} comment</span>
          <font-awesome-icon icon="reply" />
        </v-btn>
      </div>
      <div v-if="($currentUser.isAdmin || $currentUser.isTeaching || (comment.userId === $currentUser.id)) && !comment.replies.length">
        <DeleteCommentDialog
          :after-delete="refresh"
          :comment="comment"
          :disable="disableActions"
        />
      </div>
      <div v-if="$currentUser.isAdmin || $currentUser.isTeaching || (comment.userId === $currentUser.id)">
        <v-btn
          :id="`edit-comment-${comment.id}-btn`"
          :disabled="disableActions"
          icon
          @click="edit(comment)"
          @keypress.enter="edit(comment)"
        >
          <span class="sr-only">Edit {{ getPossessive(comment) }} comment</span>
          <font-awesome-icon icon="pencil-alt" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import DeleteCommentDialog from '@/components/assets/comments/DeleteCommentDialog'
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'CommentToolbar',
  components: {DeleteCommentDialog, UserLink},
  mixins: [Utils],
  props: {
    comment: {
      required: true,
      type: Object
    },
    disableActions: {
      required: true,
      type: Boolean
    },
    edit: {
      required: true,
      type: Function
    },
    refresh: {
      required: true,
      type: Function
    },
    replyTo: {
      default: () => {},
      required: false,
      type: Function
    }
  }
}
</script>
