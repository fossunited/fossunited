<template>
  <div class="flex flex-col gap-3">
    <FossClubBranding v-if="chapter.doc.chapter_type == 'FOSS Club'">{{
      chapter.doc.chapter_type
    }}</FossClubBranding>
    <CityCommunityBranding v-else>{{ chapter.doc.chapter_type }}</CityCommunityBranding>
    <div class="text-3xl font-semibold">{{ chapter.doc.chapter_name }}</div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import FossClubBranding from '@/components/FossClubBranding.vue'
import CityCommunityBranding from '@/components/CityCommunityBranding.vue'

defineProps(['chapter'])
</script>
