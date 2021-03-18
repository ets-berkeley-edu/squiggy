<template>
  <div class="align-center d-flex justify-space-between">
    <div>
      {{ comment.user.canvasFullName }} on {{ comment.createdAt | moment('LL') }}
    </div>
    <div class="d-flex">
      <div v-if="!comment.parentId">
        <v-btn
          :id="`reply-to-comment-${comment.id}-btn`"
          :disabled="disableActions"
          icon
          @click="replyTo(comment.id)"
          @keypress.enter="replyTo(comment.id)"
        >
          <span class="sr-only">Reply to {{ possessive }} comment</span>
          <font-awesome-icon icon="reply" />
        </v-btn>
      </div>
      <div v-if="$currentUser.isAdmin || $currentUser.isTeaching || (comment.userId === $currentUser.id)">
        <DeleteCommentDialog
          :after-delete="refresh"
          :comment="comment"
          :disable="disableActions"
        />
      </div>
      <div v-if="$currentUser.isAdmin || (comment.userId === $currentUser.id)">
        <v-btn
          :id="`edit-comment-${comment.id}-btn`"
          :disabled="disableActions"
          icon
          @click="edit(comment.id)"
          @keypress.enter="edit(comment.id)"
        >
          <span class="sr-only">Edit {{ possessive }} comment</span>
          <font-awesome-icon icon="pencil-alt" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import DeleteCommentDialog from '@/components/assets/comments/DeleteCommentDialog'

export default {
  name: 'CommentToolbar',
  components: {DeleteCommentDialog},
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
    }
  },
  data: () => ({
    possessive: undefined
  }),
  created() {
    this.possessive = this.comment.userId === this.$currentUser.id ? 'your' : `${this.comment.user.canvasFullName}'s`
  },
  methods: {
    replyTo(commentId) {
      console.log(`TODO: reply to comment ${commentId}`)
    }
  }
}
</script>
