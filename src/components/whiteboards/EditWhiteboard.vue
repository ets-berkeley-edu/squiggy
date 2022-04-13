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
          <label class="float-right" for="whiteboard-description-textarea">Collaborators</label>
        </v-col>
        <v-col cols="10">
          <v-autocomplete
            id="selectedUserIds-select"
            v-model="selectedUserIds"
            chips
            color="blue-grey lighten-2"
            :disabled="isSaving"
            filled
            item-text="name"
            item-value="id"
            :items="users"
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
                  <v-img :src="data.item.avatar"></v-img>
                </v-avatar>
                {{ data.item.name }}
              </v-chip>
            </template>
            <template #item="data">
              <template v-if="typeof data.item !== 'object'">
                <v-list-item-content v-text="data.item"></v-list-item-content>
              </template>
              <template v-else>
                <v-list-item-avatar>
                  <img :aria-label="`Photo of ${data.item.name}`" :src="data.item.avatar" />
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-html="data.item.name"></v-list-item-title>
                  <v-list-item-subtitle v-html="data.item.group"></v-list-item-subtitle>
                </v-list-item-content>
              </template>
            </template>
          </v-autocomplete>
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
            <div>
              <v-btn
                id="cancel-btn"
                :disabled="isSaving"
                text
                @click="onCancel"
                @keypress.enter="cancel"
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
import {getUsers} from '@/api/users'

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
    onReady: {
      required: true,
      type: Function
    },
    whiteboard: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    isInputValid: false,
    isSaving: false,
    selectedUserIds: undefined,
    title: undefined,
    titleRules: [
      v => !!v || 'Please enter a title',
      v => (!v || v.length <= 255) || 'Title must be 255 characters or less',
    ],
    users: undefined
  }),
  computed: {
    disableSave() {
      return this.isSaving || !this.$_.trim(this.title || '') || this.$_.size(this.title) > 255 || !this.$_.size(this.selectedUserIds)
    }
  },
  created() {
    if (this.whiteboard) {
      this.selectedUserIds = this.$_.map(this.whiteboard.users, 'id')
      this.title = this.whiteboard.title
    } else {
      this.selectedUserIds = [this.$currentUser.id]
    }
    getUsers().then(this.init)
  },
  methods: {
    init(data) {
      const usersBySection = {}
      const usersOther = []
      const getUserJson = u => ({
        avatar: u.canvasImage,
        id: u.id,
        name: u.canvasFullName
      })
      this.$_.each(data, user => {
        const sections = user.canvasCourseSections
        const userJson = getUserJson(user)
        if (this.$_.size(sections)) {
          this.$_.each(sections, section => {
            if (!usersBySection[section]) {
              usersBySection[section] = []
            }
            usersBySection[section] = userJson
          })
        } else if (user.canvasCourseRole) {
          usersOther.push(userJson)
        }
      })
      this.users = []
      this.$_.each(usersBySection, (userList, section) => {
        this.users.push({header: section})
        this.users.concat(userList)
      })
      this.users = this.users.concat(usersOther)
      this.onReady()
    },
    remove(user) {
      const index = this.selectedUserIds.indexOf(user.id)
      if (index >= 0) {
        this.selectedUserIds.splice(index, 1)
      }
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
          this.$_.map(this.selectedUserIds, 'id'),
          this.whiteboard.id
        ).then(done)
      } else {
        createWhiteboard(this.title, this.selectedUserIds).then(done)
      }
    }
  }
}
</script>
