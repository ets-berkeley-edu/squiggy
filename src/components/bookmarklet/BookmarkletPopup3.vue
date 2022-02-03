<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col class="header-section">
        <h1>Select the item{{ targetPage.images.length > 1 ? 's' : '' }} you'd like to add</h1>
        <div class="pb-3 text--secondary">
          {{ pluralize('image', selected.length, {0: 'No', 1: 'One'}) }} selected
          <span v-if="targetPage.images.length > 1">
            (<v-btn
              id="select-all-images-btn"
              class="pb-1 px-0 text-lowercase"
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
        v-for="(image, index) in targetPage.images"
        :key="index"
        class="d-flex child-flex"
        cols="4"
      >
        <v-img
          :alt="image.title"
          aspect-ratio="1"
          class="grey lighten-2"
          :src="image.src"
          :lazy-src="image.src"
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
              ></v-progress-circular>
            </v-row>
          </template>
        </v-img>
        <!--
        <div>
          <ul id="collabosphere-items-list" class="list-inline clearfix collabosphere-items-list"><!- -></ul>
          <div class="alert alert-info collabosphere-items-empty">No items are available on this page</div>
        </div>
        <div id="collabosphere-done" class="hide collabosphere-pane"><!- -></div>
        -->
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col class="pt-5">
        <BookmarkletButtons :disable-next="!selected.length" :next-step="4" :previous-step="1" />
      </v-col>
    </v-row>
  </v-container>
  <!--
  <script id="collabosphere-categories-template" type="text/template">
    <option value="" selected>Which assignment or topic is this related to</option>
    <% _.each(categories, function(category) { %>
      <option value="<%= category.id %>"><%= category.title %></option>
    <% }); %>
  </script>
  <script id="collabosphere-item-template" type="text/template">
    <li class="collabosphere-item-container">
      <label>
        <div class="collabosphere-item" style="background-image: url('<%= url %>')"></div>
        <div>
          <input type="checkbox" data-collabosphere-url="<%= url %>" />
        </div>
      </label>
    </li>
  </script>
  <script id="collabosphere-items-metadata-template" type="text/template">
    <% _.each(selectedItems, function(item, index) { %>
      <li class="clearfix">
        <% if (index !== 0) { %>
          <hr />
        <% } %>
        <div class="col-sm-4 col-md-3 text-center">
          <div class="collabosphere-item" style="background-image: url('<%= item.url %>')"></div>
        </div>
        <div class="col-sm-8 col-md-9 collabosphere-items-metadata-column">
          <div class="form-group">
            <label for="collabosphere-item-title" class="control-label">Title</label>
            <input id="collabosphere-item-title" class="form-control" placeholder="Enter a title" value="<%= item.title %>" maxlength="255">
          </div>
          <div class="form-group">
            <label for="collabosphere-item-category" class="control-label">Category</label>
            <select id="collabosphere-item-category" class="form-control collabosphere-item-category" data-value=""><!- -></select>
          </div>
          <div class="form-group">
            <label for="collabosphere-item-description" class="control-label">Description</label>
            <textarea You can use plain text or #keyworid="collabosphere-item-description" class="form-control" placeholder="Add some more context to this item. You can use plain text or #keywords" rows="3"></textarea>
          </div>
        </div>
      </li>
    <% }); %>
  </script>
  -->
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons},
  computed: {
    selected: {
      get() {
        return this.selectedImages
      },
      set(value) {
        this.setSelectedImages(value)
      }
    },
    toggleLabel() {
      return this.selected.length < this.targetPage.images.length ? 'select all' : 'deselect all'
    }
  },
  created() {
    this.selected = []
  },
  destroyed() {
    getCasLogoutUrl().then(this.$_.noop)
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
