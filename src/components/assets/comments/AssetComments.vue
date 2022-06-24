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
    </v-container>
    <v-container role="list" fluid>
      <v-row
        v-for="comment in comments"
        :id="`comment-${comment.id}`"
        :key="comment.id"
        role="listitem"
      >
        <v-col cols="2">
          <Avatar
            :id="`comment-${comment.id}-user-${comment.user.id}-avatar`"
            class="float-right"
            :user="comment.user"
          />
        </v-col>
        <v-col cols="8">
          <CommentToolbar
            :comment="comment"
            :disable-actions="disableActions"
            :edit="edit"
            :refresh="refresh"
            :reply-to="replyTo"
          />
          <div>
            <div v-if="comment.id === editCommentId">
              <EditCommentForm
                :after-cancel="() => editCommentId = null"
                :after-save="refresh"
                :asset-id="assetId"
                :comment="comment"
              />
            </div>
            <div
              v-if="editCommentId !== comment.id"
              :id="`comment-${comment.id}-body`"
              v-linkified
              v-html="comment.body"
            />
            <div v-if="comment.replies.length">
              <h4 class="sr-only">Replies</h4>
              <ol class="pt-5 px-5 w-100 pl-0">
                <li
                  v-for="(reply, index) in comment.replies"
                  :key="reply.id"
                  class="comment-list"
                  :class="{'pt-2': index > 0}"
                >
                  <div class="align-center d-flex mb-2">
                    <div class="pr-2">
                      <Avatar
                        :id="`comment-${reply.id}-user-${comment.user.id}-avatar`"
                        class="float-right"
                        :user="reply.user"
                      />
                    </div>
                    <CommentToolbar
                      :comment="reply"
                      :disable-actions="disableActions"
                      :edit="edit"
                      :refresh="refresh"
                    />
                  </div>
                  <div class="pl-10">
                    <div v-if="reply.id === editCommentId">
                      <EditCommentForm
                        :after-cancel="() => editCommentId = null"
                        :after-save="refresh"
                        :asset-id="assetId"
                        :comment="reply"
                      />
                    </div>
                    <div
                      v-if="editCommentId !== reply.id"
                      :id="`comment-${reply.id}-body`"
                      v-linkified
                      v-html="reply.body"
                    />
                  </div>
                </li>
              </ol>
            </div>
            <div v-if="replyToCommentId === comment.id" class="pl-6 pt-5">
              <div class="d-flex">
                <div class="pr-3">
                  <Avatar class="float-right" :user="$currentUser" />
                </div>
                <div class="pb-2">
                  <font-awesome-icon class="primary--text mr-1" icon="graduation-cap" />
                  {{ $currentUser.canvasFullName }} (me)
                </div>
              </div>
              <div class="pl-10">
                <EditCommentForm
                  :after-cancel="() => replyToCommentId = null"
                  :after-save="refresh"
                  :asset-id="assetId"
                  :parent="comment"
                />
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
import CommentToolbar from '@/components/assets/comments/CommentToolbar'
import EditCommentForm from '@/components/assets/comments/EditCommentForm'
import Utils from '@/mixins/Utils'
import {getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
  components: {Avatar, CommentToolbar, EditCommentForm},
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
    },
    updateCommentCount: {
      required: true,
      type: Function
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
    edit(comment) {
      this.editCommentId = comment.id
      this.$announcer.polite(`Editing to ${this.getPossessive(comment)} comment`)
    },
    refresh(comment=undefined) {
      this.editCommentId = null
      this.replyToCommentId = null
      getComments(this.assetId).then(data => {
        this.comments = data
        this.updateCommentCount(data.length + this.$_.sumBy(data, c => c.replies.length))
        if (comment) {
          this.scrollTo(`#comment-${comment.id}`, 0)
        }
      })
    },
    replyTo(comment) {
      this.replyToCommentId = comment.id
      this.$announcer.polite(`Replying to ${this.getPossessive(comment)} comment`)
    }
  }
}
</script>

<style scoped>
  .comment-list {
    list-style: none;
  }
</style>
