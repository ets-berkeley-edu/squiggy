<template>
  <div>
    <div v-if="!expanded" class="d-flex justify-space-between pt-2">
      <div class="w-50">
        <v-text-field
          id="basic-search-input"
          v-model="keywords"
          class="mb-0"
          clearable
          label="Search"
          solo
          type="search"
          @click:append-outer="search"
        >
          <template #append>
            <v-btn
              id="show-advanced-search"
              class="ml-2"
              icon
              @click="toggle"
            >
              <font-awesome-icon icon="caret-down" />
            </v-btn>
          </template>
          <template #append-outer>
            <div class="ml-2 mt-1">
              <font-awesome-icon icon="search" />
            </div>
          </template>
        </v-text-field>
      </div>
      <div>
        <v-btn
          elevation="2"
          large
          @click="go('/assets/manage')"
          @keypress.enter="go('/assets/manage')"
        >
          <span class="pr-2">
            <font-awesome-icon icon="cog" />
          </span>
          Manage Assets
        </v-btn>
      </div>
    </div>
    <v-expand-transition>
      <v-container v-if="expanded" fluid>
        <v-row>
          <v-col cols="2">Search</v-col>
          <v-col>
            <v-text-field
              id="adv-search-keywords-input"
              v-model="keywords"
              placeholder="Keyword"
              type="search"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">Filter by</v-col>
          <v-col>
            <v-row>
              <v-col>
                <v-select
                  v-model="categoryId"
                  :items="categories"
                  label="Category"
                  item-text="title"
                  item-value="id"
                  outlined
                />
              </v-col>
              <v-col>
                <v-select
                  v-model="assetType"
                  :items="$_.map($config.assetTypes, t => ({text: $_.capitalize(t), value: t}))"
                  label="Asset type"
                  outlined
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-select
                  v-model="userId"
                  :items="users"
                  label="User"
                  item-text="canvasFullName"
                  item-value="id"
                  outlined
                />
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="2">
            Sort by
          </v-col>
          <v-col>
            <v-select
              v-model="sortBy"
              :items="$_.map($config.sortByOptions, (text, value) => ({text, value}))"
              outlined
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col class="text-right" cols="8">
            <div class="d-flex flex-row-reverse">
              <div>
                <v-btn
                  color="primary"
                  :disabled="disable"
                  elevation="1"
                  @click="search"
                >
                  Search
                </v-btn>
              </div>
              <div class="pr-2">
                <v-btn elevation="1" @click="toggle">Cancel</v-btn>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-expand-transition>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetsHeader',
  mixins: [Context, Utils],
  props: {
    categories: {
      required: true,
      type: Array
    },
    onSubmit: {
      required: true,
      type: Function
    },
    users: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    assetType: undefined,
    categoryId: undefined,
    disable: false,
    expanded: false,
    keywords: undefined,
    sortBy: 'recent',
    userId: undefined
  }),
  methods: {
    toggle() {
      this.expanded = !this.expanded
      this.$announcer.polite(`Advanced search form is ${this.expanded ? 'open' : 'closed'}.`)
      this.$putFocusNextTick(this.expanded ? 'keywords-input' : 'basic-search-input')
    },
    search() {
      this.onSubmit()
    }
  }
}
</script>
