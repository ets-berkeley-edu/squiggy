<template>
  <v-container v-if="!isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>Select the item{{ images.length > 1 ? 's' : '' }} you'd like to add</h1>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col
        v-for="(image, index) in images"
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
          <div class="body-1 font-weight-bold image-title pa-3">{{ image.title }}</div>
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
        <BookmarkletButtons :next-step="4" :previous-step="1" />
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
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context],
  components: {BookmarkletButtons},
  created() {
    this.init(JSON.parse(window.name)).then(() => {
      this.$ready('Bookmarklet is ready!')
    })
  },
  destroyed() {
    getCasLogoutUrl().then(this.$_.noop)
  }
}
</script>

<style scoped>
.image-title {
  background-color: rgba(0, 0, 0, 0.3);
}
</style>
