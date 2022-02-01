<template>
  <div>
    <v-textarea
      :id="parent ? `reply-to-comment-${parent.id}-body-textarea` : (comment ? `comment-${comment.id}-body-textarea` : 'comment-body-textarea')"
      v-model="body"
      :autofocus="!!(parent || comment)"
      auto-grow
      dense
      :disabled="disable || isSaving"
      maxlength="10000"
      outlined
      :placeholder="parent ? 'Reply to comment' : 'Add a comment'"
    />
    <div class="align-start d-flex text-right">
      <div class="pr-1">
        <v-btn
          :id="parent ? 'save-reply-btn' : (comment ? 'save-comment-btn' : 'create-comment-btn')"
          color="primary"
          :disabled="!$_.trim(body) || disable || isSaving"
          small
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
      <div v-if="comment || parent">
        <v-btn
          :id="parent ? 'cancel-reply-btn' : (comment ? 'cancel-comment-edit-btn' : 'cancel-comment-create-btn')"
          :disabled="isSaving"
          small
          text
          @click="cancel"
          @keypress.enter="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {createComment, updateComment} from '@/api/comments'

export default {
  name: 'EditCommentForm',
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
      this.$announcer.polite(`${action} ${this.getPossessive(this.comment || this.parent)} comment`)
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
    }
  }
}
</script>
