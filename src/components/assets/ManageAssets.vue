<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />
    <div class="mt-5 mb-5 pl-4 pr-4">
      <h2>Manage Assets</h2>
    </div>
    <div class="mt-8 pl-4 pr-4">
      <h3 class="mb-3">Section Restrictions</h3>
      <div v-if="protectsAssetsPerSection">
        Students can only access assets created by others enrolled in the same sections.
      </div>
      <div v-if="!protectsAssetsPerSection">
        None.
      </div>
    </div>
    <div class="mt-8 pl-4 pr-4">
      <ManageCategories :categories="categories" :refresh="refresh" />
    </div>
    <div class="mt-8 pl-4 pr-4">
      <ManageAssignments :categories="assignments" />
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import ManageAssignments from '@/components/assets/ManageAssignments'
import ManageCategories from '@/components/assets/ManageCategories'
import Utils from '@/mixins/Utils'
import {getCategories} from '@/api/categories'
import {getCourse} from '@/api/courses'

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary, ManageAssignments, ManageCategories},
  mixins: [Context, Utils],
  data: () => ({
    assignments: [],
    categories: [],
    protectsAssetsPerSection: undefined
  }),
  created() {
    this.$loading()
    getCourse(this.$currentUser.courseId).then(data => {
      // TODO: replace expensive getCourse call with a lighter weight API call
      this.protectsAssetsPerSection = data.protectsAssetsPerSection
      this.refresh().then(() => {
        this.$ready('Manage assets')
      })
    })
  },
  methods: {
    refresh() {
      return getCategories(true).then(data => {
        this.assignments = this.$_.filter(data, c => !!c.canvasAssignmentId)
        this.categories = this.$_.filter(data, c => !c.canvasAssignmentId)
      })
    }
  }
}
</script>
