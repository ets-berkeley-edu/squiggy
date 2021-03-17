<template>
  <div class="d-flex justify-center my-5 px-5 w-100">
    <div class="pr-5 pt-3">
      <Avatar size="medium" :user="comment ? comment.user : $currentUser" />
    </div>
    <div class="w-75">
      <div class="pb-2">
        <font-awesome-icon class="primary--text" icon="graduation-cap" />
        <span v-if="comment">
          {{ comment.user.canvasFullName }}
        </span>
        <span v-if="!comment">
          {{ $currentUser.canvasFullName }} (me)
        </span>
      </div>
      <div>
        <v-textarea
          :id="parent ? `reply-to-comment-${comment.id}-body-textarea` : (comment ? `comment-${comment.id}-body-textarea` : 'comment-body-textarea')"
          v-model="body"
          auto-grow
          dense
          :disabled="disable"
          maxlength="10000"
          outlined
          :placeholder="parent ? 'Reply to comment' : 'Add a comment'"
        />
      </div>
      <div class="text-right">
        <div class="d-flex flex-row-reverse">
          <div>
            <v-btn
              id="save-comment-btn"
              color="primary"
              :disabled="!$_.trim(body) || disable"
              @click="create"
            >
              <font-awesome-icon
                v-if="parent || !comment"
                class="mr-2"
                :icon="parent ? 'reply' : 'comment'"
              />
              {{ parent ? 'Reply' : (comment ? 'Save' : 'Comment') }}
            </v-btn>
          </div>
          <div v-if="comment">
            Cancel
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import {createComment, updateComment} from '@/api/comments'

export default {
  name: 'EditCommentForm',
  components: {Avatar},
  props: {
    afterSave: {
      required: true,
      type: Function
    },
    assetId: {
      required: true,
      type: Number
    },
    comment: {
      default: undefined,
      required: false,
      type: Object
    },
    disable: {
      required: false,
      type: Boolean
    },
    parent: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    body: undefined
  }),
  created() {
    this.body = this.comment && this.comment.body
  },
  methods: {
    create() {
      if (this.comment) {
        updateComment(this.comment.id, this.body).then(() => {
          this.body = null
          this.$announcer.polite('Comment updated')
          this.afterSave()
        })
      } else {
        createComment(this.assetId, this.body, this.parent && this.parent.id).then(() => {
          this.body = null
          this.$announcer.polite('Comment posted')
          this.afterSave()
        })
      }
    },
  }
}
</script>
