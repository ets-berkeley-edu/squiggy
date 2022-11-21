<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />
    <div class="mt-5 mb-5 pl-4 pr-4">
      <h2>Manage Assets</h2>
    </div>
    <div class="mt-8 pl-4 pr-4">
      <h3 class="mb-3">Section Restrictions</h3>
      <v-checkbox
        id="protect_assets_per_section_checkbox"
        v-model="checkbox"
        label="Students can only access assets created by others enrolled in the same sections."
        @change="toggleSectionCheckbox"
      />
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
import {getCourse, updateProtectAssetsPerSectionCheckbox} from '@/api/courses'

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary, ManageAssignments, ManageCategories},
  mixins: [Context, Utils],
  data: () => ({
    assignments: [],
    categories: [],
    checkbox: undefined
  }),
  created() {
    this.$loading()
    getCourse(this.$currentUser.courseId).then(data => {
      this.checkbox = data.protectsAssetsPerSection
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
    },
    toggleSectionCheckbox(value) {
      updateProtectAssetsPerSectionCheckbox(value).then(() => {
        this.$announcer.polite(`Assets ${value ? '' : 'not'} protected per section.`)
      })
    }
  }
}
</script>
