<template>
  <v-container v-if="isAuthorized" fluid>
    <v-row no-gutters>
      <v-col>
        <div>
          <PageTitle :text="`Select the item${targetPage.images.length > 1 ? 's' : ''} you'd like to add`" />
        </div>
        <div class="pb-3 text--secondary">
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
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col
        v-for="(image, index) in showAll ? targetPage.images : targetPage.images.slice(0, 20)"
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
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletPopup3',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons, PageTitle},
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
    showAll: false
  }),
  created() {
    this.$ready('Bookmarklet ready')
    setTimeout(() => {
      this.showAll = true
    }, 50)
  },
  methods: {
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
