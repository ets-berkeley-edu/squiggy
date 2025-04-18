<template>
  <div>
    <h3 class="mb-3">Assignments</h3>
    <div v-if="!categories.length">
      No assignments found.
    </div>
    <div v-if="categories.length">
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

export default {
  name: 'ManageAssignments',
  mixins: [Utils],
  props: {
    categories: {
      required: true,
      type: Array
    }
  }
}
</script>

<style>
.assignments-list .v-list-item:nth-of-type(even) {
  background-color: rgba(0, 0, 0, .03) !important;
}
</style>
