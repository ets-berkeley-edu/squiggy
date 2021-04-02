<template>
  <v-footer id="footer">
    <v-container fluid class="pa-1">
      <div>
        &copy; {{ new Date().getFullYear() }} Regents of the University of California. All Rights Reserved.
      </div>
    </v-container>
  </v-footer>
</template>

<script>
export default {
  name: 'FooterIFrame'
}
</script>
