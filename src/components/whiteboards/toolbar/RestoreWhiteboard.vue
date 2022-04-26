<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col class="mt-3 py-3">
        <PageTitle text="Restore whiteboard" />
        <div class="deep-orange--text font-weight-bold pt-2">
          Deleted on {{ whiteboard.deletedAt | moment('MMM DD, YYYY') }}.
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="align-center" cols="2">
        <label class="float-right font-weight-bold">
          Title
        </label>
      </v-col>
      <v-col id="whiteboard-title" class="align-center" cols="10">
        {{ whiteboard.title }}
      </v-col>
    </v-row>
    <v-row v-if="whiteboard.description">
      <v-col class="align-center" cols="2">
        <label class="float-right font-weight-bold">
          Description
        </label>
      </v-col>
      <v-col id="whiteboard-description" class="align-start" cols="10">
        {{ whiteboard.description }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="align-center" cols="2">
        <label class="float-right font-weight-bold">Collaborators</label>
      </v-col>
      <v-col cols="10">
        <OxfordJoin v-slot="{item}" :items="whiteboard.users">
          <span :id="`collaborator-canvas-user-${item.canvasUserId}`">{{ item.canvasFullName }}</span>
        </OxfordJoin>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="pt-5">
        <div class="d-flex justify-end w-100">
          <div v-if="canRestore">
            <v-btn
              id="restore-whiteboard-btn"
              color="warning"
              :disabled="isRestoring"
              @click="restore"
              @keypress.enter="restore"
            >
              Restore whiteboard
            </v-btn>
          </div>
          <div>
            <v-btn
              id="cancel-btn"
              :disabled="isRestoring"
              text
              @click="onCancel"
              @keypress.enter="onCancel"
            >
              Cancel
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import OxfordJoin from '@/components/util/OxfordJoin'
import PageTitle from '@/components/util/PageTitle'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'RestoreWhiteboard',
  mixins: [Whiteboarding],
  components: {OxfordJoin, PageTitle},
  props: {
    afterRestore: {
      required: true,
      type: Function
    },
    onCancel: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    canRestore: false,
    isRestoring: false
  }),
  created() {
    this.canRestore = this.whiteboard.deletedAt && (this.$currentUser.isAdmin || this.$currentUser.isTeaching)
  },
  methods: {
    restore() {
      this.isRestoring = true
      this.restoreWhiteboard().then(() => {
        this.$announcer.polite('Whiteboard restored.')
        this.isRestoring = false
        this.afterRestore()
      })
    }
  }
}
</script>
