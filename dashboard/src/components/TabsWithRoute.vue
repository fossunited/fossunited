<template>
    <div class="flex gap-3 border-b px-8">
        <router-link
            v-for="(tab, index) in tabs"
            :key="index"
            :to="tab.route"
            class="px-4 py-2 text-base text-gray-600 transition-all hover:border-gray-400 hover:text-gray-900"
            :class="{'font-semibold border-b-2 border-black text-black hover:border-gray-900 hover:text-gray-900': tab.route === route.path}"
        >
            {{ tab.label }}
        </router-link>
    </div>
</template>
<script setup>
import { defineProps } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
defineProps({
  tabs: {
    type: Object,
    required: true,
  },
})
</script>
