<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />

    <h2>Manage Assets</h2>
    <div class="pt-2">
      <h3>Custom Categories</h3>
    </div>
    <div class="pt-2">
      Categories can be used to tag items and are a great way of classifying items within the Asset Library.
      The Asset Library can also be filtered by category.
    </div>
    <div class="align-start d-flex pt-2">
      <div class="pr-1 w-100">
        <v-text-field
          id="add-category-input"
          v-model="model"
          clearable
          dense
          filled
          label="Add new category"
          solo
          type="text"
          @click="addCategory"
          @keypress.enter="addCategory"
        />
      </div>
      <div>
        <v-btn
          id="add-category-btn"
          class="mt-1"
          @click="addCategory"
          @keypress.enter="addCategory"
        >
          Add
        </v-btn>
      </div>
    </div>
    <v-card rounded tile>
      <v-list>
        <v-list-item-group>
          <template v-for="(category, index) in categories">
            <v-list-item :key="category.id">
              <template #default="{}">
                <v-list-item-content>
                  <v-list-item-title :id="`category-${category.id}-title`">{{ category.title }}</v-list-item-title>
                  <v-list-item-subtitle
                    v-if="category.description"
                    :id="`category-${category.id}-description`"
                  >
                    {{ category.description }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle :id="`category-${category.id}-asset-count`">
                    {{ pluralize('asset', category.assetCount, {0: 'No', 1: 'Used by one', 'other': `Used by ${category.assetCount}`}) }}
                  </v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <div class="d-flex">
                    <div class="mr-2">
                      <v-btn
                        :id="`edit-category-${category.id}-btn`"
                        class="text-no-wrap"
                        icon
                        @click="edit(category)"
                        @keypress.enter="edit(category)"
                      >
                        <font-awesome-icon class="mr-2" icon="pencil-alt" />
                        <span class="sr-only">Edit category {{ category.title }}</span>
                      </v-btn>
                    </div>
                    <div>
                      <v-btn
                        :id="`delete-category-${category.id}-btn`"
                        class="mr-3"
                        icon
                        @click="confirmDelete(category)"
                        @keypress.enter="confirmDelete(category)"
                      >
                        <font-awesome-icon class="mr-2" icon="trash" />
                        <span class="sr-only">Delete category {{ $_.get(selected, 'title') }}</span>
                      </v-btn>
                    </div>
                  </div>
                </v-list-item-action>
              </template>
            </v-list-item>
            <v-divider v-if="index < categories.length - 1" :key="index" />
          </template>
        </v-list-item-group>
      </v-list>
    </v-card>

    <v-dialog v-model="isDialogOpen" width="800">
      <v-card>
        <v-card-title id="delete-dialog-title" tabindex="-1">Delete Category?</v-card-title>
        <v-card-text class="pt-3">
          Are you sure you want to delete
          <span :id="`category-title-confirm-delete`" class="font-weight-bold text-no-wrap">{{ $_.get(selected, 'title') }}</span>?
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <div class="d-flex flex-row-reverse pa-2">
            <div>
              <v-btn
                id="confirm-delete-btn"
                color="primary"
                @click="deleteConfirmed"
                @keypress.enter="deleteConfirmed"
              >
                Confirm
              </v-btn>
            </div>
            <div class="mr-2">
              <v-btn
                id="cancel-delete-btn"
                @click="cancelDelete"
                @keypress.enter="cancelDelete"
              >
                Cancel
              </v-btn>
            </div>
          </div>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div class="mt-4">
      <h3>Assignments</h3>
    </div>
    <div>
      Check the box next to the name of an Assignment in order to sync student submissions for that Assignment to
      the Asset Library. Each checked Assignment will appear as a category in the Asset Library, with all submissions
      shared for review and commenting by other students. Assignments must use the "Online" Submission Type and
      "File Uploads" or "Website URL" Entry Options to be synced to the Asset Library. There may be a short delay
      before submissions appear for a checked Assignment.
    </div>
    <div>
      TODO
    </div>
    <h3>Migrate Assets</h3>
    <div>
      If you have instructor privileges in another course site using the Asset Library, you can copy all of your assets
      into that site's Asset Library. Only assets that you have submitted yourself will be copied, not assets submitted
      by other instructors or by students.
    </div>
    <div>
      TODO
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {createCategory, deleteCategory, getCategories} from '@/api/categories'

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    assignments: undefined,
    categories: undefined,
    isDialogOpen: undefined,
    model: undefined,
    selected: undefined
  }),
  watch: {
    isDialogOpen(value) {
      if (!value) {
        this.selected = null
      }
    }
  },
  created() {
    this.$loading()
    this.refresh().then(() => {
      this.$ready('Manage categories')
    })
  },
  methods: {
    addCategory() {
      if (this.model) {
        createCategory(this.model).then(this.refresh)
      }
    },
    cancelDelete() {
      this.$putFocusNextTick(`category-${this.selected.id}-title`)
      this.isDialogOpen = false
      this.$announcer.polite('Canceled')
    },
    confirmDelete(category) {
      this.selected = category
      this.isDialogOpen = true
      this.$announcer.polite('Confirm delete')
      this.$putFocusNextTick('delete-dialog-title')
    },
    deleteConfirmed() {
      let categoryId = this.selected.id
      this.isDialogOpen = false
      deleteCategory(categoryId).then(() => {
        this.selected = null
        this.$announcer.polite('Deleted')
      }).then(this.refresh)
    },
    edit(category) {
      this.selected = category
      this.$announcer.polite(`Edit category ${this.selected.title}`)
    },
    refresh() {
      return getCategories(true).then(data => {
        this.categories = data
      })
    }
  }
}
</script>
