<template>
  <div v-if="isAuthorized">
    <v-app-bar fixed>
      <v-app-bar-title>
        <PageTitle :text="`Select the item${targetPage.images.length > 1 ? 's' : ''} you'd like to add`" />
      </v-app-bar-title>
      <template #extension>
        <div class="text--secondary">
          {{ pluralize('image', selected.length, {0: 'No', 1: 'One'}) }} selected
          <span v-if="targetPage.images.length > 1">
            (<v-btn
              id="select-all-images-btn"
              class="pb-1 px-0 text-lowercase"
              :disabled="isLoading"
              text
              @click="toggleSelectAll"
            ><!--
            -->{{ toggleLabel }}<!--
            --></v-btn>)
          </span>
        </div>
      </template>
    </v-app-bar>
    <v-container v-if="isAuthorized" class="mt-16 pt-8" fluid>
      <v-row no-gutters>
        <v-col
          v-for="(image, index) in images"
          :key="index"
          class="d-flex child-flex"
          cols="4"
        >
          <v-img
            :id="`image-${index}`"
            :alt="image.title"
            aspect-ratio="1"
            class="grey lighten-2"
            :src="image.src"
          >
            <div class="bg-image-label pt-2 px-7">
              <v-checkbox
                :id="`image-checkbox-${index}`"
                v-model="selected"
                color="orange"
                dark
                :multiple="true"
                :value="image"
              >
                <template #label>
                  <span class="image-label">Image {{ index + 1 }}<span v-if="image.title">: {{ image.title }}</span></span>
                </template>
              </v-checkbox>
            </div>
            <template #placeholder>
              <v-row
                class="fill-height ma-0"
                align="center"
                justify="center"
              >
                <v-progress-circular
                  indeterminate
                  color="grey lighten-5"
                />
              </v-row>
            </template>
          </v-img>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col class="pt-5">
          <BookmarkletButtons :disable-next="!selected.length" :next-step="4" :previous-step="1" />
        </v-col>
      </v-row>
    </v-container>
    <InfiniteLoading spinner="spiral" @infinite="infiniteHandler">
      <span slot="spinner" class="sr-only">Loading...</span>
    </InfiniteLoading>
  </div>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletPopup3',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons, InfiniteLoading, PageTitle},
  computed: {
    selected: {
      get() {
        return this.selectedImages
      },
      set(value) {
        this.setSelectedImages(this.$_.cloneDeep(value))
      }
    },
    toggleLabel() {
      return this.selected.length < this.targetPage.images.length ? 'select all' : 'deselect all'
    }
  },
  data: () => ({
    images: []
  }),
  created() {
    this.$ready('Bookmarklet ready')
  },
  methods: {
    infiniteHandler($state) {
      if (this.images.length < this.targetPage.images.length) {
        this.images = this.targetPage.images.slice(0, this.images.length + this.scrollChunkSize)
        $state.loaded()
      } else {
        $state.complete()
      }
    },
    toggleSelectAll() {
      this.selected = this.selected.length !== this.targetPage.images.length ? this.targetPage.images : []
    }
  }
}
</script>

<style scoped>
.bg-image-label {
  background-color: rgba(96, 125, 139, 0.8);
}
.image-label {
  color: white;
  font-size: 18px;
  font-weight: 700;
}
</style>
