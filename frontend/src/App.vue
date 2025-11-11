<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { ref } from 'vue'

const heartbeat = ref("</3");
const items = ref([]);
const itemFormName = ref("");

async function check_heartbeat() {
  const response = await fetch("http://127.0.0.1:5000/heartbeat");
  if (response.status === 200) {
    heartbeat.value = "<3";
  } else {
    hearbeat.value = "</3";
  }
}

async function get_items() {
  const response = await fetch(
    "/api/items/",
    {
      credentials: "include",
      mode: "cors",
    }
  );
  items.value = await response.json();
}

async function onSubmitCreateItem() {
  const body = {
    name: itemFormName.value
  };
  const response = await fetch(
    "/api/items/",
    {
      credentials: "include",
      mode: "cors",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );
}

</script>

<template>
  <!--// TODO pluralize route..?-->
  <form action="/api/auth/login" method="post">
    <label for="username">User</label>
    <input type="text" name="username" required />
    <label for="password">Password</label>
    <input type="password" name="password" required />
    <input type="submit" value="Submit"/>
  </form>
  <br>
  <button @click=check_heartbeat>Check Heartbeat</button>
  <br>
  <button @click=get_items>Get Items</button>
  <br>
  <form @submit.prevent="onSubmitCreateItem" action="/api/items/" method="post">
    <label for="name">Name</label>
    <input v-model="itemFormName" name="name" required />
    <input type="submit" value="Create"/>
  </form>

  <div>
    {{ heartbeat }}
  </div>
  <div>
    {{ items }}
  </div>
</template>

<style scoped>
</style>
