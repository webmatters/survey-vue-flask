<template>
  <div id="app">
    <div id="nav"></div>
    <app-header />
    <router-view />
  </div>
</template>

<script>
import AppHeader from "@/components/Header.vue";
export default {
  components: {
    AppHeader
  }
};
</script>

<style lang="scss">
@import "~bulma/bulma";
</style>
