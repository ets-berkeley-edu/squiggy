<template>
  <div>
    <h3>Custom Categories</h3>
    <div class="mt-2">
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
    <v-card v-if="categories.length" rounded tile>
      <v-list>
        <v-list-item-group>
          <template v-for="(category, index) in categories">
            <v-list-item :key="category.id" :ripple="!isEditing(category)">
              <template #default="{}">
                <v-list-item-content v-if="$_.get(selectedEdit, 'id') !== category.id">
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
                <v-list-item-action :class="{'mr-2 w-100': isEditing(category)}">
                  <div v-if="!isEditing(category)" class="d-flex">
                    <div class="mr-2">
                      <v-btn
                        :id="`edit-category-${category.id}-btn`"
                        class="text-no-wrap"
                        :disabled="!!(selectedEdit || selectedDelete)"
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
                        :disabled="!!(selectedEdit || selectedDelete)"
                        icon
                        @click="confirmDelete(category)"
                        @keypress.enter="confirmDelete(category)"
                      >
                        <font-awesome-icon class="mr-2" icon="trash" />
                        <span class="sr-only">Delete category {{ $_.get(selectedDelete, 'title') }}</span>
                      </v-btn>
                    </div>
                  </div>
                  <div v-if="isEditing(category)" class="pt-3 w-100">
                    <label :for="`edit-category-${selectedEdit.id}-input`" class="sr-only">Edit category title</label>
                    <v-text-field
                      :id="`edit-category-${selectedEdit.id}-input`"
                      v-model="selectedEdit.title"
                      clearable
                      :counter-value="v => v.trim().length"
                      maxlength="255"
                      placeholder="Title"
                      solo
                    />
                    <div class="d-flex flex-row-reverse pb-2">
                      <div>
                        <v-btn
                          :id="`edit-category-${selectedEdit.id}-cancel`"
                          :disabled="isUpdating"
                          small
                          @click="cancelEdit"
                          @keypress.enter="cancelEdit"
                        >
                          Cancel
                        </v-btn>
                      </div>
                      <div class="pr-2">
                        <v-btn
                          :id="`edit-category-${selectedEdit.id}-save`"
                          color="primary"
                          :disabled="isUpdating"
                          small
                          @click="update"
                          @keypress.enter="update"
                        >
                          Save
                        </v-btn>
                      </div>
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
          <span :id="`category-title-confirm-delete`" class="font-weight-bold text-no-wrap">{{ $_.get(selectedDelete, 'title') }}</span>?
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
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {createCategory, deleteCategory, updateCategory} from '@/api/categories'

export default {
  name: 'ManageCategories',
  mixins: [Utils],
  props: {
    categories: {
      required: true,
      type: Array
    },
    refresh: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    isDialogOpen: undefined,
    isUpdating: false,
    model: undefined,
    selectedDelete: undefined,
    selectedEdit: undefined
  }),
  methods: {
    addCategory() {
      if (this.model) {
        createCategory(this.model).then(this.refresh)
      }
    },
    cancelDelete() {
      this.isDialogOpen = false
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick(`delete-category-${this.selectedDelete.id}-btn`)
      this.selectedDelete = null
    },
    cancelEdit() {
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick(`edit-category-${this.selectedEdit.id}-btn`)
      this.selectedEdit = null
    },
    confirmDelete(category) {
      this.selectedDelete = category
      this.isDialogOpen = true
      this.$announcer.polite('Confirm delete')
      this.$putFocusNextTick('delete-dialog-title')
    },
    deleteConfirmed() {
      let categoryId = this.selectedDelete.id
      this.isDialogOpen = false
      deleteCategory(categoryId).then(() => {
        this.selectedDelete = null
        this.$announcer.polite('Deleted')
        this.$putFocusNextTick('add-category-input')
      }).then(this.refresh)
    },
    edit(category) {
      this.selectedEdit = this.$_.clone(category)
      this.$announcer.polite(`Edit ${this.selectedEdit.title}`)
      this.$putFocusNextTick(`edit-category-${this.selectedEdit.id}-input`)
    },
    isEditing(category) {
      return this.$_.get(this.selectedEdit, 'id') === category.id
    },
    update() {
      this.isUpdating = true
      updateCategory(this.selectedEdit.id, this.selectedEdit.title).then(() => {
        this.refresh().then(() => {
          this.isUpdating = false
          this.selectedEdit = null
        })
      })
    }
  }
}
</script>
