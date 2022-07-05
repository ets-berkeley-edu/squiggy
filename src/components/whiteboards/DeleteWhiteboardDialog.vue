<template>
  <v-dialog v-model="dialog" width="500">
    <v-card class="pt-4">
      <v-card-title>Are you sure?</v-card-title>
      <v-card-text class="pt-2">
        Please confirm that you want to delete the "<span class="font-weight-bold">{{ whiteboard.title }}</span>"
        Whiteboard<span v-if="showCollaborators">, owned by
          <span v-if="whiteboard.users.length === 1">{{ whiteboard.users[0].canvasFullName }}</span>
          <span v-if="whiteboard.users.length > 1">{{ oxfordJoin($_.map(whiteboard.users, 'canvasFullName')) }}?</span>
        </span><span v-if="!showCollaborators">?</span>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <div class="d-flex pa-2">
          <div class="mr-2">
            <v-btn
              id="confirm-delete-btn"
              color="primary"
              :disabled="isDeleting"
              @click="confirm"
              @keypress.enter.prevent="confirm"
            >
              <span v-if="isDeleting">
                <font-awesome-icon
                  class="mr-2"
                  icon="spinner"
                  :spin="true"
                />
                Deleting...
              </span>
              <span v-if="!isDeleting">Confirm</span>
            </v-btn>
          </div>
          <div>
            <v-btn
              id="cancel-delete-btn"
              :disabled="isDeleting"
              @click="cancel"
              @keypress.enter.prevent="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'DeleteWhiteboardDialog',
  mixins: [Utils, Whiteboarding],
  props: {
    isDeleting: {
      required: true,
      type: Boolean
    },
    onCancel: {
      required: true,
      type: Function
    },
    onConfirmDelete: {
      required: true,
      type: Function
    },
    open: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    dialog: false,
    showCollaborators: undefined
  }),
  watch: {
    open(value) {
      this.dialog = value
    }
  },
  created() {
    const userCount = this.whiteboard.users.length
    this.showCollaborators = !!userCount && (userCount > 1 || this.$currentUser.id !== this.whiteboard.users[0].id)
  },
  methods: {
    cancel() {
      this.dialog = false
      this.onCancel()
    },
    confirm() {
      this.dialog = false
      this.onConfirmDelete()
    }
  }
}
</script>
