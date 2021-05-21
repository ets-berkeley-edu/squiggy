<template>
  <div>
    <h3 class="mb-3">Assignments</h3>
    <div v-if="!categories.length">
      No assignments found.
    </div>
    <div v-if="categories.length">
      <div class="mb-3">
        Check the box next to the name of an Assignment in order to sync student submissions for that Assignment to
        the Asset Library. Each checked Assignment will appear as a category in the Asset Library, with all submissions
        shared for review and commenting by other students. Assignments must use the "Online" Submission Type and
        "File Uploads" or "Website URL" Entry Options to be synced to the Asset Library. There may be a short delay
        before submissions appear for a checked Assignment.
      </div>
      <v-card rounded tile>
        <v-list>
          <v-list-item-group class="assignments-list">
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
                      {{ pluralize('submission', category.assetCount, {0: 'No', 1: 'One'}) }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action class="pt-2">
                    <label class="sr-only" :for="`category-${category.id}-sync-checkbox`">
                      Sync student submissions:
                    </label>
                    <v-checkbox
                      v-if="!$_.isNil(selected)"
                      :id="`category-${category.id}-sync-checkbox`"
                      v-model="selected"
                      :dense="true"
                      :value="category.id"
                      @change="toggle(category)"
                    />
                  </v-list-item-action>
                </template>
              </v-list-item>
              <v-divider v-if="index < categories.length - 1" :key="index" />
            </template>
          </v-list-item-group>
        </v-list>
      </v-card>
    </div>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {updateCategory} from '@/api/categories'

export default {
  name: 'ManageAssignments',
  mixins: [Utils],
  props: {
    categories: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    selected: undefined
  }),
  created() {
    this.selected = this.$_.map(this.$_.filter(this.categories, c => c.visible), 'id')
  },
  methods: {
    toggle(category) {
      const visible = !category.visible
      updateCategory(category.id, category.title, visible).then(() => {
        this.$announcer.polite(`${category.title} will ${visible ? '' : 'not'} sync.`)
      })
    }
  }
}
</script>

<style>
.assignments-list .v-list-item:nth-of-type(even) {
  background-color: rgba(0, 0, 0, .03) !important;
}
</style>
