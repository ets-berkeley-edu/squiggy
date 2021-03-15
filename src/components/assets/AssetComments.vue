<template>
  <div v-if="comments">
    <h3 id="comments-count">{{ comments.length || 'No' }} Comments</h3>
    <div class="d-flex justify-center my-3 px-5 w-100">
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
    <div v-for="comment in comments" :key="comment.id">
      <div class="align-center d-flex">
        <div>
          <Avatar :user="comment.user" />
        </div>
        <div>
          {{ comment.user.canvasFullName }}
        </div>
        <div>
          on {{ comment.createdAt | moment('LL') }}
        </div>
      </div>
      <div class="pa-5">
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
      </div>
    </div>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import {createComment, getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
  components: {Avatar},
  props: {
    asset: {
      required: true,
      type: Object
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
    getComments(this.asset.id).then(data => {
      this.comments = data
    })
  },
  methods: {
    create() {
      createComment(this.asset.id, this.body, this.parentId).then(() => {
        getComments(this.asset.id).then(data => {
          this.comments = data
        })
      })
    }
  }
}
</script>
