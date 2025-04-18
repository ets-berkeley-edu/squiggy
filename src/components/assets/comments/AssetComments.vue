<template>
  <div v-if="comments">
    <div class="pb-4 pt-2">
      <h3 id="comments-count" class="font-weight-light">{{ pluralize('comment', comments.length, {0: 'No'}) }}</h3>
    </div>
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
          />
          <div>
            <div
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
                    />
                  </div>
                  <div class="pl-10">
                    <div
                      :id="`comment-${reply.id}-body`"
                      v-linkified
                      v-html="reply.body"
                    />
                  </div>
                </li>
              </ol>
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
import Utils from '@/mixins/Utils'
import {getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
  components: {Avatar, CommentToolbar},
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
  }),
  created() {
    this.refresh()
  },
  methods: {
    refresh(comment=undefined) {
      getComments(this.assetId).then(data => {
        this.comments = data
        this.updateCommentCount(data.length + this.$_.sumBy(data, c => c.replies.length))
        if (comment) {
          this.scrollTo(`#comment-${comment.id}`, 0)
        }
      })
    },
  }
}
</script>

<style scoped>
  .comment-list {
    list-style: none;
  }
</style>
