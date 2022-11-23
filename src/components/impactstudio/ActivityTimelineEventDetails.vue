<template>
  <div class="event-details-popover-container">
    <img
      v-if="asset.thumbnailUrl"
      class="event-details-popover-thumbnail"
      :src="asset.thumbnailUrl"
      :alt="asset.title"
      :title="asset.title"
    />
    <div v-if="!asset.thumbnailUrl" class="event-details-popover-thumbnail event-details-popover-thumbnail-default">
      <i class="fa fa-file"></i>
    </div>
    <div class="event-details-popover-avatar event-details-popover-avatar-small">
      <img
        :src="user.image"
        :alt="user.name"
        :title="user.name"
      />
    </div>
    <div class="text-truncate">
      <h3 class="event-details-popover-title">
        <router-link
          :id="`event-details-popover-${activityId}-asset-link`"
          class="d-block text-truncate"
          :to="`/asset/${asset.id}?from=impactStudio`"
        >
          {{ title }}
        </router-link>
      </h3>
      <p class="event-details-popover-description text-wrap">
        <a :id="`event-details-popover-${activityId}-profile-link`" :href="`/impact_studio/profile/${user.id}`">{{ user.name }}</a>
        {{ $_.get(eventDescriptions, activityType) }}
        <span v-if="comment">
          <span
            v-if="!snippet"
            :id="`event-details-popover-${activityId}-comment`"
            class="event-details-popover-comment"
            v-html="comment.body"
          />
          <span v-if="snippet">
            <span
              :id="`event-details-popover-${activityId}-comment`"
              class="event-details-popover-comment"
              v-html="snippet"
            />
            <btn :id="`event-details-popover-${activityId}-asset-btn`" @click="go(`/asset/${asset.id}`, {from: 'impactStudio'})">Read more &raquo;</btn>
          </span>
        </span>
      </p>
      <p :id="`event-details-popover-${activityId}-timestamp`" class="event-details-popover-timestamp">{{ date }}</p>
    </div>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'ActivityNetworkTooltip',
  mixins: [Utils],
  props: {
    activityId: {
      required: true,
      type: Number
    },
    activityType: {
      required: true,
      type: String
    },
    asset: {
      required: false,
      type: Object,
      default: () => ({})
    },
    comment: {
      required: false,
      type: Object,
      default: () => null
    },
    date: {
      required: true,
      type: String
    },
    snippet: {
      required: false,
      type: String,
      default: null
    },
    title: {
      required: true,
      type: String
    },
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    assetUrl: undefined,
    eventDescriptions: {
      'asset_add': 'added this asset.',
      'asset_comment': 'commented on this asset, ',
      'asset_like': 'liked this asset.',
      'asset_view': 'viewed this asset.',
      'discussion_entry': 'posted to a discussion.',
      'discussion_topic': 'posted to a discussion.',
      'get_asset_comment': 'commented on this asset, ',
      'get_asset_comment_reply': 'commented on this asset, ',
      'get_asset_like': 'liked this asset.',
      'get_asset_view': 'viewed this asset.',
      'get_discussion_entry_reply': 'posted to a discussion.',
      'get_whiteboard_add_asset': 'used this asset in a whiteboard.',
      'get_whiteboard_remix': 'remixed this asset in a whiteboard.',
      'whiteboard_add_asset': 'used this asset in a whiteboard.',
      'whiteboard_export': 'exported a whiteboard.',
      'whiteboard_remix': 'remixed this asset in a whiteboard.',
    }
  }),
  created() {
    const suffix = `?from=impactStudio#suitec_assetId=${this.asset.id}`
    this.assetUrl = this.$isInIframe ? `${this.$currentUser.assetLibraryUrl}${suffix}` : `/assets${suffix}`
  }
}
</script>

<style>
.event-details-popover-avatar {
  background: #fff;
  border: 1px solid #c2c8d0;
  border-radius: 100%;
  overflow: hidden;
}

.event-details-popover-avatar img {
  height: 100%;
  width: 100%;
}

.event-details-popover-avatar-large {
  flex: 0 0 100px;
  height: 100px;
  margin-right: 15px;
  width: 100px;
}

.event-details-popover-avatar-small {
  height: 50px;
  left: 65px;
  position: absolute;
  top: 65px;
  width: 50px;
}

.event-details-popover-comment {
  font-style: italic;
}

.event-details-popover-container {
  display: flex;
  flex-direction: row;
  position: relative;
  z-index: 2;
}

.event-details-popover-description {
  color: #777;
  font-size: 13px;
}

.event-details-popover-strong {
  font-size: 14px;
  font-weight: 600;
}

.event-details-popover-thumbnail {
  border: 1px solid #c2c8d0;
  height: 100px;
  margin: 1px 25px 15px 1px;
  min-width: 100px;
  width: 100px;
}

.event-details-popover-thumbnail-default {
  align-items: center;
  background-color: #E8E8E8;
  display: flex;
  justify-content: center;
}

.event-details-popover-thumbnail-default i {
  color: #ADABAA;
  font-size: 50px;
}

.event-details-popover-timestamp {
  color: #777;
  font-size: 12px;
}

.event-details-popover-title {
  font-size: 15px;
  margin-bottom: 10px;
}
</style>
