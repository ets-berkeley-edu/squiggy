<template>
  <div v-if="comments">
    <div class="d-flex justify-center my-5 px-5 w-100">
      <div class="pr-5 pt-3">
        <Avatar size="medium" :user="$currentUser" />
      </div>
      <div class="w-75">
        <div class="pb-2">
          <font-awesome-icon class="primary--text" icon="graduation-cap" />
          {{ $currentUser.canvasFullName }} (me)
        </div>
        <div>
          <v-textarea
            id="comment-body-textarea"
            v-model="body"
            auto-grow
            dense
            outlined
            placeholder="Add a comment"
          />
        </div>
        <div class="text-right">
          <v-btn
            id="post-comment-btn"
            color="primary"
            :disabled="!$_.trim(body)"
            @click="create"
          >
            <font-awesome-icon class="mr-2" icon="comment" />
            Comment
          </v-btn>
        </div>
      </div>
    </div>
    <v-container fluid>
      <v-row>
        <v-col cols="2" />
        <v-col>
          <h3 id="comments-count">{{ pluralize('comment', comments.length, {0: 'No'}) }}</h3>
        </v-col>
      </v-row>
      <v-row v-for="comment in comments" :key="comment.id">
        <v-col cols="2" />
        <v-col>
          <v-row>
            <v-col>
              <div class="d-flex justify-space-between">
                <div class="align-center d-flex">
                  <div class="pr-4">
                    <Avatar :user="comment.user" />
                  </div>
                  <div>
                    {{ comment.user.canvasFullName }} on {{ comment.createdAt | moment('LL') }}
                  </div>
                </div>
                <div>
                  <div class="d-flex">
                    <div>
                      <v-btn
                        :id="`reply-to-comment-${comment.id}-btn`"
                        icon
                        @click="replyTo(comment.id)"
                        @keypress.enter="replyTo(comment.id)"
                      >
                        <span class="sr-only">Reply</span>
                        <font-awesome-icon icon="reply" />
                      </v-btn>
                    </div>
                    <div v-if="$currentUser.isAdmin || $currentUser.isTeaching || (comment.userId === $currentUser.id)">
                      <DeleteCommentDialog
                        :after-delete="refresh"
                        :comment="comment"
                      />
                    </div>
                    <div v-if="$currentUser.isAdmin || (comment.userId === $currentUser.id)">
                      <v-btn
                        :id="`edit-comment-${comment.id}-btn`"
                        icon
                        @click="edit(comment.id)"
                        @keypress.enter="edit(comment.id)"
                      >
                        <span class="sr-only">Edit</span>
                        <font-awesome-icon icon="pencil-alt" />
                      </v-btn>
                    </div>
                  </div>
                </div>
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              {{ comment.body }}
              <div v-if="comment.replies.length">
                <div
                  v-for="reply in comment.replies"
                  :key="reply.id"
                  class="pa-5"
                >
                  {{ reply.body }}
                </div>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import DeleteCommentDialog from '@/components/assets/comments/DeleteCommentDialog'
import Utils from '@/mixins/Utils'
import {createComment, getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
  components: {Avatar, DeleteCommentDialog},
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
    body: undefined,
    comments: undefined
  }),
  created() {
    this.refresh()
  },
  methods: {
    create() {
      createComment(this.assetId, this.body, this.parentId).then(() => {
        this.$announcer.polite('Comment posted')
        getComments(this.assetId).then(data => {
          this.comments = data
          this.body = null
        })
      })
    },
    edit(commentId) {
      console.log(`TODO: edit comment ${commentId}`)
    },
    refresh() {
      getComments(this.assetId).then(data => {
        this.comments = data
      })
    },
    replyTo(commentId) {
      console.log(`TODO: reply to comment ${commentId}`)
    }
  }
}
</script>
