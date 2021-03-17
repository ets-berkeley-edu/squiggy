<template>
  <div>
    <v-btn
      :id="`delete-comment-${comment.id}-btn`"
      icon
      @click="confirmDelete(comment.id)"
      @keypress.enter="confirmDelete(comment.id)"
    >
      <span class="sr-only">Delete</span>
      <font-awesome-icon icon="trash" />
    </v-btn>
    <v-dialog v-model="confirmDeleteDialog" width="500">
      <v-card>
        <v-card-title id="delete-dialog-title" tabindex="-1">Delete comment?</v-card-title>
        <v-card-text class="pt-3">
          Are you sure you want to delete {{ comment.userId === $currentUser.id ? 'your' : `${comment.user.canvasFullName}'s` }} comment?
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <div class="d-flex flex-row-reverse pa-2">
            <div>
              <v-btn
                id="confirm-delete-btn"
                color="primary"
                @click="deleteConfirmed"
                @keypress.enter="deleteConfirmed"
              >
                Confirm
              </v-btn>
            </div>
            <div class="mr-2">
              <v-btn
                id="cancel-delete-btn"
                @click="cancelDelete"
                @keypress.enter="cancelDelete"
              >
                Cancel
              </v-btn>
            </div>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {deleteComment} from '@/api/comments'

export default {
  name: 'DeleteCommentDialog',
  props: {
    afterDelete: {
      default: () => {},
      required: false,
      type: Function
    },
    comment: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    confirmDeleteCommentId: undefined,
    confirmDeleteDialog: false
  }),
  methods: {
    cancelDelete() {
      this.confirmDeleteCommentId = this.confirmDeleteDialog = null
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick('asset-title')
    },
    confirmDelete(commentId) {
      this.confirmDeleteCommentId = commentId
      this.confirmDeleteDialog = true
      this.$announcer.polite('Confirm delete')
      this.$putFocusNextTick('delete-dialog-title')
    },
    deleteConfirmed() {
      const commentId = this.confirmDeleteCommentId
      this.confirmDeleteCommentId = this.confirmDeleteDialog = null
      deleteComment(commentId).then(() => {
        this.$announcer.polite('Comment deleted')
        this.afterDelete()
      })
    }
  }
}
</script>

<style scoped>

</style>