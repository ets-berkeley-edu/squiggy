<template>
  <div>
    <BackToWhiteboards />

    <v-container v-if="!isLoading" fluid>
      <v-row no-gutters>
        <v-col>
          <PageTitle text="Create a new whiteboard" />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2">
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
            maxlength="255"
            outlined
            required
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="2">
          <label class="float-right" for="whiteboard-description-textarea">Collaborators</label>
        </v-col>
        <v-col cols="10">
          <v-autocomplete
            v-model="collaborators"
            :disabled="isUpdating"
            :items="people"
            filled
            chips
            color="blue-grey lighten-2"
            label="Select"
            item-text="name"
            item-value="name"
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
                  <img :src="data.item.avatar">
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
          <div class="d-flex justify-end pt-5 w-100">
            <div class="pr-2">
              <v-btn
                id="save-btn"
                color="primary"
                :disabled="disableSave || isSaving"
                @click="save"
                @keypress.enter="save"
              >
                Create Whiteboard
              </v-btn>
            </div>
            <div>
              <v-btn
                id="cancel-btn"
                :disabled="isSaving"
                text
                @click="cancel"
                @keypress.enter="cancel"
              >
                Cancel
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>

    <!--
    <a data-ng-href="/whiteboards" class="col-back"><i class="fa fa-angle-left"></i> Back to Whiteboards</a>
    <form
      name="whiteboardsCreateForm"
      id="whiteboards-create-form"
      data-ng-submit="whiteboardsCreateForm.$valid && createWhiteboard()"
    >
      <div class="form-group" data-ng-class="{'has-error': whiteboardsCreateForm.$submitted && whiteboardsCreateForm.whiteboardsCreateTitle.$invalid}">
        <label for="whiteboards-create-title" class="col-sm-2 control-label">Title</label>
        <div class="col-sm-10">
          <input type="text" id="whiteboards-create-title" name="whiteboardsCreateTitle" class="form-control" placeholder="Enter a title" data-ng-model="whiteboard.title" data-ng-maxlength="255" required>
          <div class="help-block" data-ng-messages="whiteboardsCreateForm.whiteboardsCreateTitle.$error">
            <div data-ng-message="required">Please enter a title</div>
            <div data-ng-message="maxlength">A title can only be 255 characters long</div>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label for="whiteboards-create-collaborators" class="col-sm-2 control-label">Collaborators</label>
        <div class="col-sm-10">
          <oi-select
            class="cleanMode"
            oi-options="user.id as user.canvas_full_name for user in users track by user.id | orderBy: 'canvas_full_name.toLowerCase()'"
            oi-select-options="{'searchFilter': 'usersSearch', 'dropdownFilter': 'usersDropdown'}"
            ng-model="whiteboard.members" multiple placeholder="Enter the names of the people you want to add to this whiteboard" tabindex="-1">
          </oi-select>
        </div>
      </div>
      <div class="form-group text-right">
        <div class="col-sm-offset-2 col-sm-10 btn-row-reversed">
          <button type="submit" class="btn btn-primary">Create whiteboard</button>
          <a data-ng-href="/whiteboards" class="btn btn-default">Cancel</a>
        </div>
      </div>
    </form>
    -->
  </div>
</template>

<script>
import BackToWhiteboards from '@/components/util/BackToWhiteboards'
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'
import {createWhiteboard} from '@/api/whiteboards'

export default {
  name: 'WhiteboardCreate',
  components: {BackToWhiteboards, PageTitle},
  mixins: [Context, Utils],
  computed: {
    disableSave() {
      return !this.$_.trim(this.title || '')
    }
  },
  data: () => ({
    collaborators: ['Sandra Adams', 'Britta Holt'],
    isSaving: false,
    isUpdating: false,
    people: [
      {header: 'Group 1'},
      {name: 'Sandra Adams', group: 'Group 1', avatar: 'https://cdn.vuetifyjs.com/images/lists/1.jpg'},
      {name: 'Ali Connors', group: 'Group 1', avatar: 'https://cdn.vuetifyjs.com/images/lists/2.jpg'},
      {name: 'Trevor Hansen', group: 'Group 1', avatar: 'https://cdn.vuetifyjs.com/images/lists/3.jpg'},
      {name: 'Tucker Smith', group: 'Group 1', avatar: 'https://cdn.vuetifyjs.com/images/lists/2.jpg'},
      {divider: true},
      {header: 'Group 2'},
      {name: 'Britta Holt', group: 'Group 2', avatar: 'https://cdn.vuetifyjs.com/images/lists/4.jpg'},
      {name: 'Jane Smith ', group: 'Group 2', avatar: 'https://cdn.vuetifyjs.com/images/lists/5.jpg'},
      {name: 'John Smith', group: 'Group 2', avatar: 'https://cdn.vuetifyjs.com/images/lists/1.jpg'},
      {name: 'Sandra Williams', group: 'Group 2', avatar: 'https://cdn.vuetifyjs.com/images/lists/3.jpg'},
    ],
    title: undefined,
  }),
  watch: {
    isUpdating(val) {
      if (val) {
        setTimeout(() => (this.isUpdating = false), 3000)
      }
    }
  },
  created() {
    this.$ready('Create Whiteboard')
  },
  methods: {
    cancel() {
      this.$announcer.polite(this.cancelButtonLabel === 'Close' ? 'Closed' : 'Canceled')
      this.go('/whiteboards')
    },
    remove(collaborator) {
      const index = this.collaborators.indexOf(collaborator.name)
      if (index >= 0) this.collaborators.splice(index, 1)
    },
    save() {
      this.isSaving = true
      this.$announcer.polite('Saving...')
      createWhiteboard(this.title).then(() => {
        this.$announcer.polite('Whiteboard created.')
        this.go('/whiteboards')
      })
    }
  }
}
</script>

<style scoped>

</style>