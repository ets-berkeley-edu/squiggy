<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary anchor="assets-container" />
    <div class="mt-5 mb-5 pl-4 pr-4">
      <h2>Manage Assets</h2>
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

export default {
  name: 'ManageAssets',
  components: {BackToAssetLibrary, ManageAssignments, ManageCategories},
  mixins: [Context, Utils],
  data: () => ({
    assignments: undefined,
    categories: undefined
  }),
  created() {
    this.$loading()
    this.refresh().then(() => {
      this.$ready('Manage categories')
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
