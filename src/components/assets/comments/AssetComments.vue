<template>
  <div v-if="comments">
    <div class="pb-4 pt-2">
      <h3 id="comments-count" class="font-weight-light">{{ pluralize('comment', comments.length, {0: 'No'}) }}</h3>
    </div>
    <v-container fluid>
      <v-row class="elevation-1 mb-2 py-2">
        <v-col class="pt-6" cols="2">
          <Avatar class="float-right" size="medium" :user="$currentUser" />
        </v-col>
        <v-col cols="8">
          <div class="pb-2">
            <font-awesome-icon class="primary--text" icon="graduation-cap" />
            {{ $currentUser.canvasFullName }} (me)
          </div>
          <EditCommentForm :after-save="refresh" :asset-id="assetId" />
        </v-col>
      </v-row>
      <v-row v-for="comment in comments" :id="`comment-${comment.id}`" :key="comment.id">
        <v-col cols="2">
          <Avatar class="float-right" :user="comment.user" />
        </v-col>
        <v-col cols="8">
          <div class="align-center d-flex justify-space-between">
            <div>
              {{ comment.user.canvasFullName }} on {{ comment.createdAt | moment('LL') }}
            </div>
            <div class="d-flex">
              <div>
                <v-btn
                  :id="`reply-to-comment-${comment.id}-btn`"
                  :disabled="disableActions"
                  icon
                  @click="replyTo(comment.id)"
                  @keypress.enter="replyTo(comment.id)"
                >
                  <span class="sr-only">Reply to {{ getPossessive(comment) }} comment</span>
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
                  <span class="sr-only">Edit {{ getPossessive(comment) }} comment</span>
                  <font-awesome-icon icon="pencil-alt" />
                </v-btn>
              </div>
            </div>
          </div>
          <div>
            <div v-if="comment.id === editCommentId" cols="8">
              <EditCommentForm
                :after-cancel="() => editCommentId = null"
                :after-save="refresh"
                :asset-id="assetId"
                :comment="comment"
              />
            </div>
            <div v-if="editCommentId !== comment.id" :id="`comment-${comment.id}-body`">
              {{ comment.body }}
            </div>
            <div v-if="comment.replies.length">
              <div
                v-for="reply in comment.replies"
                :id="`comment-${reply.id}-body`"
                :key="reply.id"
                class="pa-5"
              >
                {{ reply.body }}
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import DeleteCommentDialog from '@/components/assets/comments/DeleteCommentDialog'
import EditCommentForm from '@/components/assets/comments/EditCommentForm'
import Utils from '@/mixins/Utils'
import {getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
  components: {Avatar, DeleteCommentDialog, EditCommentForm},
  mixins: [Utils],
  props: {
    assetId: {
      required: true,
      type: Number
    },
    parentId: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  data: () => ({
    comments: undefined,
    editCommentId: undefined,
    replyToCommentId: undefined
  }),
  computed: {
    disableActions() {
      return !!(this.editCommentId || this.replyToCommentId)
    }
  },
  created() {
    this.refresh()
  },
  methods: {
    edit(commentId) {
      this.editCommentId = commentId
    },
    getPossessive(comment) {
      return comment.userId === this.$currentUser.id ? 'your' : `${comment.user.canvasFullName}'s`
    },
    refresh(comment=undefined) {
      this.editCommentId = null
      getComments(this.assetId).then(data => {
        this.comments = data
        if (comment) {
          this.scrollTo(`#comment-${comment.id}`, 0)
        }
      })
    },
    replyTo(commentId) {
      console.log(`TODO: reply to comment ${commentId}`)
    }
  }
}
</script>
