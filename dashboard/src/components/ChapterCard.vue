<template>
  <Card
    role="button"
    tabindex="0"
    @click="goToChapter"
    @keyup.enter="goToChapter"
    @keyup.space.prevent="goToChapter"
    class="border-2 border-transparent rounded-[8px] hover:border-outline-gray-4 transition-colors hover:cursor-pointer"
  >
    <template #actions-left>
      <FossClubLogo
        v-if="props.chapter.chapter_type == 'FOSS Club'"
        class="w-7 h-7"
      ></FossClubLogo>
      <CityComunityBranding v-else>{{ props.chapter.chapter_type }}</CityComunityBranding>
    </template>

    <div class="flex justify-between items-baseline">
      <div class="text-lg font-medium">{{ props.chapter.chapter_name }}</div>
    </div>
  </Card>
</template>
<script setup>
import { useRouter } from 'vue-router'
import FossClubLogo from '@/components/FossClubLogo.vue'
import CityComunityBranding from '@/components/CityCommunityBranding.vue'

const props = defineProps({
  chapter: {
    type: Object,
    required: true,
  },
})
const emit = defineEmits(['selected']) //helps to communicate with parent component
const router = useRouter()
const goToChapter = () => {
  emit('selected', props.chapter.chapter_name)
  router.push(`/chapter/${props.chapter.name}`)
}
</script>
