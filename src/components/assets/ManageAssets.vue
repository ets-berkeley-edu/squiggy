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
          v-model="category"
          clearable
          dense
          filled
          label="Add new category"
          solo
          type="text"
          @keypress.enter="addCategory"
        />
      </div>
      <div>
        <v-btn id="add-category-btn" class="mt-1">
          Add
        </v-btn>
      </div>
    </div>
    <v-card rounded tile>
      <v-list-item
        v-for="(category, index) in categories"
        :key="index"
        :class="{'grey lighten-4': index % 2 === 0}"
        two-line
      >
        <v-list-item-content>
          <v-list-item-title>{{ category.title }}</v-list-item-title>
          <v-list-item-subtitle>Used by N items</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-card>
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
import {createCategory, getCategories} from '@/api/categories'

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary},
  mixins: [Context],
  data: () => ({
    assignments: undefined,
    categories: undefined,
    category: undefined
  }),
  created() {
    this.$loading()
    this.refresh().then(() => {
      this.$ready('Add a link asset')
    })
  },
  methods: {
    addCategory() {
      if (this.category) {
        createCategory(this.category).then(this.refresh)
      }
    },
    refresh() {
      return getCategories().then(data => {
        this.categories = data
      })
    }
  }
}
</script>
