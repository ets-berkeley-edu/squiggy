<template>
  <div v-if="!isLoading">
    <div id="modal-header">
      <h4 class="modal-title">
        <span id="collabosphere-title-items-metadata">Add more information about the selected items</span>
      </h4>
    </div>
    <div>
      <div id="collabosphere-items-metadata" class="hide collabosphere-pane">
        <ul id="collabosphere-items-metadata-container" class="list-unstyled collabosphere-items-metadata-container"><!-- --></ul>
        <div class="modal-footer">
          <button id="collabosphere-items-metadata-back" type="button" class="btn btn-default">Back</button>
          <button id="collabosphere-items-add" type="button" class="btn btn-primary">Add items</button>
        </div>
      </div>
      <div id="collabosphere-done" class="hide collabosphere-pane"><!-- --></div>
    </div>
  </div>
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
import Context from '@/mixins/Context'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'BookmarkletPopup',
  mixins: [Bookmarklet, Context],
  destroyed() {
    getCasLogoutUrl().then(this.$_.noop)
  }
}
</script>
