<template>
  <div id="create-or-edit-comment" class="d-flex justify-center my-5 px-5 w-100">
    <div class="pr-5 pt-3">
      <Avatar :size="avatarSize" :user="comment ? comment.user : $currentUser" />
    </div>
    <div class="w-75">
      <div class="pb-2">
        <font-awesome-icon class="primary--text" icon="graduation-cap" />
        <span v-if="comment">
          {{ comment.user.canvasFullName }}<span v-if="comment.user.id === $currentUser.id"> (me)</span>
        </span>
        <span v-if="!comment">
          {{ $currentUser.canvasFullName }} (me)
        </span>
      </div>
      <div>
        <v-textarea
          :id="parent ? `reply-to-comment-${comment.id}-body-textarea` : (comment ? `comment-${comment.id}-body-textarea` : 'comment-body-textarea')"
          v-model="body"
          :autofocus="!!(parent || comment)"
          auto-grow
          dense
          :disabled="disable || isSaving"
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
              :disabled="!$_.trim(body) || disable || isSaving"
              @click="create"
            >
              <font-awesome-icon
                v-if="parent || !comment"
                class="mr-2"
                :icon="isSaving ? 'spinner' : (parent ? 'reply' : 'comment')"
                :spin="isSaving"
              />
              <span v-if="isSaving">Saving</span>
              <span v-if="!isSaving">{{ parent ? 'Reply' : (comment ? 'Save' : 'Comment') }}</span>
            </v-btn>
          </div>
          <div v-if="comment">
            <v-btn
              :disabled="isSaving"
              text
              @click="cancel"
              @keypress.enter="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Utils from '@/mixins/Utils'
import {createComment, updateComment} from '@/api/comments'

export default {
  name: 'EditCommentForm',
  components: {Avatar},
  mixins: [Utils],
  props: {
    afterCancel: {
      default: () => {},
      required: false,
      type: Function
    },
    afterSave: {
      required: true,
      type: Function
    },
    assetId: {
      required: true,
      type: Number
    },
    avatarSize: {
      default: 'small',
      required: false,
      type: String
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
    body: undefined,
    isSaving: false
  }),
  created() {
    this.body = this.comment && this.comment.body
    if (this.comment || this.parent) {
      const action = this.comment ? 'Editing' : 'Replying'
      this.$announcer.polite(`${action} ${this.getPossessive(this.comment)} comment`)
      this.scrollTo('#create-or-edit-comment', 0)
    }
  },
  methods: {
    cancel() {
      this.body = null
      this.$announcer.polite('Canceled')
      this.afterCancel()
    },
    create() {
      if (this.comment) {
        this.isSaving = true
        updateComment(this.comment.id, this.body).then(comment => {
          this.body = null
          this.$announcer.polite('Comment updated')
          this.afterSave(comment.id)
          this.isSaving = false
        })
      } else {
        this.isSaving = true
        createComment(this.assetId, this.body, this.parent && this.parent.id).then(comment => {
          this.body = null
          this.$announcer.polite('Comment posted')
          this.afterSave(comment)
          this.isSaving = false
        })
      }
    },
    getPossessive(comment) {
      return comment.userId === this.$currentUser.id ? 'your' : `${comment.user.canvasFullName}'s`
    }
  }
}
</script>
