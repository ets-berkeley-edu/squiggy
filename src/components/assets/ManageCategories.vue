<template>
  <div>
    <h3 class="mb-3">Custom Categories</h3>
    <div class="mb-3">
      Categories can be used to tag items and are a great way of classifying items within the Asset Library.
      The Asset Library can also be filtered by category.
    </div>
    <v-alert v-if="!categories.length" type="info" text>
      There are no custom categories.
    </v-alert>
    <v-card v-if="categories.length" rounded tile>
      <v-list>
        <v-list-item-group class="custom-categories-list">
          <template v-for="(category, index) in categories">
            <v-list-item :key="category.id">
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
              </template>
            </v-list-item>
            <v-divider v-if="index < categories.length - 1" :key="index" />
          </template>
        </v-list-item-group>
      </v-list>
    </v-card>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'

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
  data() {
    return {
      categoryName: '',
      categoryNameValid: false,
      categoryRules: [
        v => !!this.$_.trim(v) || 'Please enter a category name',
        v => (!v || v.length <= 255) || 'Category name must be 255 characters or less',
      ],
      isDialogOpen: undefined,
      isUpdating: false,
      selectedDelete: undefined,
      selectedEdit: undefined
    }
  }
}
</script>

<style>
.v-dialog__content--active {
  height: auto !important;
  margin-top: 100px;
}

.custom-categories-list .v-list-item:nth-of-type(even) {
  background-color: rgba(0, 0, 0, .03) !important;
}
</style>
