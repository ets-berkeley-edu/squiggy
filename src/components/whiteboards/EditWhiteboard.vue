<template>
  <v-form v-model="isInputValid" @submit="save">
    <v-container fluid>
      <v-row no-gutters>
        <v-col class="pb-3">
          <PageTitle :text="whiteboard ? 'Update whiteboard' : 'Create a new whiteboard'" />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-5" cols="2">
          <label class="float-right" for="whiteboard-title-input">
            Title
            <font-awesome-icon
              aria-label="Icon indicates required field"
              class="deep-orange--text icon-denotes-required"
              icon="asterisk"
              size="xs"
            />
          </label>
        </v-col>
        <v-col cols="10">
          <v-text-field
            id="whiteboard-title-input"
            v-model="title"
            outlined
            required
            :rules="titleRules"
            @keydown.enter="submit"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-5" cols="2">
          <label class="float-right" for="whiteboard-users-select">Collaborators</label>
        </v-col>
        <v-col cols="10">
          <v-autocomplete
            id="whiteboard-users-select"
            v-model="selectedUserIds"
            chips
            clearable
            color="blue-grey lighten-2"
            :disabled="isSaving"
            :error="!selectedUserIds.length"
            filled
            item-text="canvasFullName"
            item-value="id"
            :items="users"
            :loading="isFetchingUsers"
            :menu-props="{
              closeOnClick: true,
              closeOnContentClick: true
            }"
            multiple
          >
            <template #selection="data">
              <v-chip
                v-bind="data.attrs"
                :input-value="data.selected"
                close
                @click="data.select"
                @click:close="remove(data.item)"
              >
                <v-avatar left>
                  <v-img :src="data.item.canvasImage"></v-img>
                </v-avatar>
                {{ data.item.canvasFullName }}
              </v-chip>
            </template>
            <template #item="data">
              <template v-if="typeof data.item !== 'object'">
                <v-list-item-content v-text="data.item"></v-list-item-content>
              </template>
              <template v-else>
                <v-list-item-avatar>
                  <img :aria-label="`Photo of ${data.item.canvasFullName}`" :src="data.item.canvasImage" />
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-html="data.item.canvasFullName"></v-list-item-title>
                  <v-list-item-subtitle v-html="data.item.group"></v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </template>
            <template #no-data>
              <div class="grey--text pl-5 py-2">
                {{ selectedUserIds.length ? 'No more eligible users.' : 'No eligible users.' }}
              </div>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
      <v-row v-if="whiteboard && !$currentUser.isAdmin && !$currentUser.isTeaching && !$_.includes(selectedUserIds, $currentUser.id)" no-gutters>
        <v-col>
          <v-alert
            aria-live="assertive"
            dense
            :icon="false"
            role="alert"
            type="warning"
          >
            <font-awesome-icon icon="exclamation-triangle" class="pr-2" />
            <span class="font-weight-bold">Warning!</span>
            If you remove yourself from the list of collaborators then this
            window will close and you will lose access to this whiteboard.
          </v-alert>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col>
          <div class="d-flex justify-end pt-3 w-100">
            <div class="pr-2">
              <v-btn
                id="save-btn"
                color="primary"
                :disabled="disableSave"
                @click="save"
                @keypress.enter="save"
              >
                <font-awesome-icon
                  v-if="isSaving"
                  class="mr-2"
                  icon="spinner"
                  :spin="true"
                />
                <span v-if="isSaving">Saving...</span>
                <span v-if="!isSaving && whiteboard">Update</span>
                <span v-if="!isSaving && !whiteboard">Create</span>
              </v-btn>
            </div>
            <div v-if="canDelete">
              <v-btn
                id="delete-whiteboard-btn"
                color="error"
                :disabled="isSaving"
                @click="openDeleteDialog"
                @keypress.enter="openDeleteDialog"
              >
                Delete whiteboard
              </v-btn>
            </div>
            <div>
              <v-btn
                id="cancel-btn"
                :disabled="isSaving"
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
  </v-form>
</template>

<script>
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'
import {createWhiteboard, updateWhiteboard} from '@/api/whiteboards'
import {getStudentsBySection} from '@/api/users'

export default {
  name: 'EditWhiteboard',
  components: {PageTitle},
  mixins: [Context, Utils],
  props: {
    afterSave: {
      required: true,
      type: Function
    },
    onCancel: {
      required: true,
      type: Function
    },
    onClickDelete: {
      default: undefined,
      required: false,
      type: Function
    },
    onReady: {
      required: true,
      type: Function
    },
    reset: {
      required: false,
      type: Boolean
    },
    whiteboard: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    canDelete: false,
    isFetchingUsers: true,
    isInputValid: false,
    isSaving: false,
    selectedUserIds: [],
    title: undefined,
    titleRules: [
      v => !!v || 'Please enter a title',
      v => (!v || v.length <= 255) || 'Title must be 255 characters or less',
    ],
    users: undefined
  }),
  computed: {
    disableSave() {
      return this.isSaving
        || !this.$_.trim(this.title || '')
        || this.$_.size(this.title) > 255
        || (!this.whiteboard && !this.$_.size(this.selectedUserIds))
    }
  },
  watch: {
    reset(value) {
      if (value) {
        this.resetData()
      }
    }
  },
  created() {
    this.init()
  },
  methods: {
    openDeleteDialog() {
      this.onClickDelete()
      this.resetData()
    },
    init() {
      this.resetData()
      getStudentsBySection().then(users => {
        this.users = users
        const addCurrentUser = !this.whiteboard && !this.$_.includes(this.$_.map(this.users, 'id'), this.$currentUser.id)
        if (addCurrentUser) {
          this.users.push(this.$currentUser)
          this.users = this.$_.sortBy(this.users, ['canvasFullName', 'id'])
        }
        this.isFetchingUsers = false
      })
    },
    remove(user) {
      const index = this.selectedUserIds.indexOf(user.id)
      if (index >= 0) {
        this.selectedUserIds.splice(index, 1)
      }
    },
    resetData() {
      if (this.whiteboard) {
        this.selectedUserIds = this.$_.map(this.whiteboard.users, 'id')
        this.title = this.whiteboard.title
        this.canDelete = !this.whiteboard.deletedAt
          && this.onClickDelete
          && (this.$currentUser.isAdmin || this.$currentUser.isTeaching)
      } else {
        this.selectedUserIds = [this.$currentUser.id]
        this.title = undefined
      }
      this.isFetchingUsers = true
      this.isInputValid = false
      this.isSaving = false
    },
    save() {
      this.isSaving = true
      const done = whiteboard => {
        this.$announcer.polite(`Whiteboard ${this.whiteboard ? 'updated' : 'created'}.`)
        this.isSaving = false
        this.afterSave(whiteboard)
      }
      if (this.whiteboard) {
        updateWhiteboard(
          this.title,
          this.selectedUserIds,
          this.whiteboard.id
        ).then(done)
      } else {
        createWhiteboard(this.title, this.selectedUserIds).then(done)
      }
    }
  }
}
</script>
