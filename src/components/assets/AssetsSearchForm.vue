<template>
  <div>
    <v-text-field
      v-model="keywords"
      class="mb-0"
      clearable
      label="Search"
      solo
      type="search"
      @click:append-outer="search"
    >
      <template #append>
        <div class="ml-2">
          <font-awesome-icon icon="caret-down" />
        </div>
      </template>
      <template #append-outer>
        <div class="ml-2 mt-1">
          <font-awesome-icon icon="search" />
        </div>
      </template>
    </v-text-field>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetsSearchForm',
  mixins: [Context, Utils],
  props: {
    onSubmit: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    keywords: undefined
  }),
  methods: {
    search() {
      this.onSubmit()
    }
  }
}
</script>
