<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Delete whiteboard?</v-card-title>
      <v-card-text class="pt-3">
        Are you sure?
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <div class="d-flex pa-2">
          <div class="mr-2">
            <v-btn
              id="confirm-delete-btn"
              color="primary"
              @click="confirm"
              @keypress.enter.prevent="confirm"
            >
              Confirm
            </v-btn>
          </div>
          <div>
            <v-btn
              id="cancel-delete-btn"
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
export default {
  name: 'DeleteWhiteboardDialog',
  props: {
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
    dialog: false
  }),
  watch: {
    open(value) {
      this.dialog = value
    }
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
