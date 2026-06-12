<script setup lang="ts">
// App-Shell (Sidenav + Header) folgt im nächsten Schritt —
// der Scaffold rendert die Views direkt.
</script>

<template>
  <div class="bx-root">
    <nav class="bx-nav" />
    <div class="bx-main">
      <main class="bx-page">
        <router-view />
      </main>
    </div>
  </div>
</template>
