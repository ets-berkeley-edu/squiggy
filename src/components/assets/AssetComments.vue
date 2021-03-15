<template>
  <v-container v-if="comments" fluid>
    <v-row>
      <v-col>
        <h3 id="comments-count">{{ comments.length }} Comments</h3>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        Current User Avatar
      </v-col>
      <v-col>
        <div>
          <font-awesome-icon icon="graduation-cap" />
          Name of active user
        </div>
        <v-textarea
          id="comment-body-textarea"
          v-model="body"
          auto-grow
          outlined
          placeholder="Add a comment"
        />
        <v-btn
          id="confirm-delete-btn"
          class="mr-2"
          color="primary"
          :disabled="!$_.trim(body)"
          @click="create"
        >
          <font-awesome-icon icon="comment" />
          Comment
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-for="comment in comments" :key="comment.id">
      <v-col>
        {{ comment.body }}
      </v-col>
      <v-col>
        {{ comment.children }}
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

import {createComment, getComments} from '@/api/comments'

export default {
  name: 'AssetComments',
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
