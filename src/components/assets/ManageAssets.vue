<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />

    <h2>Manage Assets</h2>
    <h3>Custom Categories</h3>
    <div>
      Categories can be used to tag items and are a great way of classifying items within the Asset Library.
      The Asset Library can also be filtered by category.
    </div>
    <div>
      <ul>
        <li v-for="category in categories" :key="category.id">{{ category.title }}</li>
      </ul>
    </div>
    <h3>Assignments</h3>
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
import {getCategories} from '@/api/categories'

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary},
  mixins: [Context],
  data: () => ({
    assignments: undefined,
    categories: undefined
  }),
  created() {
    this.$loading()
    getCategories().then(data => {
      this.categories = data
      this.$ready('Add a link asset')
    })
  }
}
</script>
