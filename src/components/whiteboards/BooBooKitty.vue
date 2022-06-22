<template>
  <div>
    <div class="align-center d-flex flex-column mt-2 pt-2">
      <v-card
        class="elevation-1"
        outlined
      >
        <v-card-text>
          <div v-if="!isLoading" class="boo-boo-container d-flex">
            <div>
              <v-img
                alt="Laverne and Shirley with stuffed animals"
                aria-label="Laverne and Shirley with stuffed animals"
                src="@/assets/boo-boo-kitty.jpg"
                width="300px"
              />
            </div>
            <v-container class="h-100">
              <v-row>
                <v-col>
                  <h1>Socket Test</h1>
                  <div class="pb-4 pt-2 text-subtitle-1">
                    The Socket.IO client will connect using the initialization parameters below.
                    <div>
                      <a
                        id="socket-io-docs"
                        href="https://socket.io/docs/v4/client-initialization/"
                        target="_blank"
                      >
                        Read the docs
                      </a>
                      to understand each configuration value.
                    </div>
                  </div>
                </v-col>
              </v-row>
              <v-row no-gutters>
                <v-col>
                  <label for="base-url" class="font-weight-bold text-no-wrap">
                    Base URL
                  </label>
                  <v-text-field
                    id="base-url"
                    v-model="baseUrl"
                    :disabled="isConnected"
                    hide-details
                    outlined
                    required
                  />
                </v-col>
              </v-row>
              <v-row class="pt-3" no-gutters>
                <v-col>
                  <label for="message" class="font-weight-bold text-no-wrap">
                    Message to emit
                  </label>
                  <v-text-field
                    id="message"
                    v-model="message"
                    :disabled="!isConnected"
                    hide-details
                    outlined
                    required
                  />
                </v-col>
              </v-row>
              <v-row class="pt-3" no-gutters>
                <v-col>
                  <label for="transports" class="font-weight-bold text-no-wrap">
                    Transports (order matters)
                  </label>
                  <v-combobox
                    id="transports"
                    v-model="transports"
                    chips
                    class="mt-0 pt-0"
                    :disabled="isConnected"
                    hide-details
                    :items="['websocket', 'polling']"
                    multiple
                  >
                    <template #selection="data">
                      <v-chip
                        :key="JSON.stringify(data.item)"
                        v-bind="data.attrs"
                        :disabled="data.disabled"
                        :input-value="data.selected"
                        @click:close="data.parent.selectItem(data.item)"
                      >
                        <v-avatar
                          class="accent white--text"
                          left
                          v-text="data.item.slice(0, 1).toUpperCase()"
                        ></v-avatar>
                        {{ data.item }}
                      </v-chip>
                    </template>
                  </v-combobox>
                </v-col>
              </v-row>
              <v-row class="pt-3" no-gutters>
                <v-col cols="12">
                  <div class="d-flex justify-end pt-3 w-100">
                    <div class="pr-2">
                      <v-btn
                        id="connect-btn"
                        class="white--text"
                        color="green"
                        :disabled="disableConnectButton"
                        @click="connect"
                        @keypress.enter="connect"
                      >
                        <font-awesome-icon
                          v-if="isConnecting"
                          class="mr-2"
                          icon="spinner"
                          :spin="true"
                        />
                        <span v-if="isConnecting">Connecting...</span>
                        <span v-if="isConnected">Connected</span>
                        <span v-if="!isConnecting && !isConnected">Connect</span>
                      </v-btn>
                    </div>
                    <div class="pr-2">
                      <v-btn
                        id="disconnect-btn"
                        color="error"
                        :disabled="!isConnected && !isConnecting"
                        @click="disconnect"
                        @keypress.enter="disconnect"
                      >
                        Disconnect
                      </v-btn>
                    </div>
                    <div>
                      <v-btn
                        id="cancel-btn"
                        :color="isConnected ? 'green' : 'grey'"
                        :disabled="!isConnected"
                        @click="emit"
                        @keypress.enter="emit"
                      >
                        Emit
                      </v-btn>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </div>
          <div class="pt-5">
            <v-divider />
            <div class="pt-10">
              <h2>The latest reply from server-side</h2>
              <div class="pt-3">
                <label for="server-message" class="font-weight-bold text-no-wrap">
                  Most recent 'boo-boo-kitty' message emitted by the server since page load.
                </label>
                <div class="pt-3">
                  <v-textarea
                    id="server-message"
                    v-model="serverMessage"
                    hide-details
                    outlined
                    readonly
                    rows="2"
                  />
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import apiUtils from '@/api/api-utils'
import {io} from 'socket.io-client'

export default {
  name: 'BooBooKitty',
  mixins: [Context, Utils],
  data: () => ({
    baseUrl: undefined,
    isConnected: false,
    isConnecting: false,
    message: 'Boo Boo Kitty',
    serverMessage: undefined,
    socket: undefined,
    transports: ['websocket', 'polling'],
  }),
  computed: {
    disableConnectButton() {
      return this.isConnected || this.isConnecting || !this.$_.trim(this.baseUrl) || !this.transports.length
    }
  },
  created() {
    this.baseUrl = apiUtils.apiBaseUrl() || this.$config.baseUrl
    this.$ready('Web socket testing')
  },
  methods: {
    connect() {
      this.isConnecting = true
      this.socket = io(this.baseUrl, {
        forceNew: true,
        transports: this.transports,
        withCredentials: true
      })
      this.socket.on('boo-boo-kitty', data => {
        this.serverMessage = data.message
        console.log(this.serverMessage)
      })
      this.socket.on('connect_error', data => {
        console.log(`connect_error: ${data}`)
        this.isConnected = false
        this.isConnecting = false
      })
      this.socket.on('connect', () => {
        this.isConnected = true
        this.isConnecting = false
      })
      this.socket.on('disconnect', data => {
        console.log(`disconnect: ${data}`)
        this.isConnected = false
        this.isConnecting = false
      })
      this.socket.on('close', data => {
        console.log(`close: ${data}`)
        this.isConnected = false
        this.isConnecting = false
      })
    },
    disconnect() {
      this.socket.disconnect()
      this.socket.close()
      this.isConnected = false
      this.isConnecting = false
    },
    emit() {
      this.socket.emit('boo-boo-kitty', {
        message: this.message
      })
    }
  }
}
</script>

<style scoped>
.boo-boo-container {
  min-width: 800px !important;
}
</style>
