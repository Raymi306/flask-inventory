<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { ref } from 'vue'

const heartbeat = ref("</3")

async function check_heartbeat() {
  const response = await fetch("http://127.0.0.1:5000/heartbeat");
  console.log(heartbeat)
  heartbeat.value = await response.text();
}

async function get_items() {
  const response = await fetch(
    "/api/item/",
    {
      credentials: "include",
      mode: "cors",
    }
  );
  heartbeat.value = await response.text();
}

</script>

<template>
  <form action="/api/auth/login" method="post">
    <label for="username">User</label>
    <input type="text" name="username" required />
    <label for="password">Password</label>
    <input type="password" name="password" required />
    <input type="submit" value="Submit"/>
  </form>
  <button @click=get_items>Items</button>
</template>

<style scoped>
</style>
