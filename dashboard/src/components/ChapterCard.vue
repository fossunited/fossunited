<template>
    <Card
        class="border-2 border-transparent hover:border-gray-500 transition-all hover:cursor-pointer"
        @click="() => $router.push(`/chapter/${props.chapter.name}`)"
    >
        <template #actions-left>
            <FossClubLogo v-if="props.chapter.chapter_type == 'FOSS Club'" class="w-7 h-7 "></FossClubLogo>
            <CityComunityBranding v-else>{{ props.chapter.chapter_type }}</CityComunityBranding>
        </template>
        <div class="flex justify-between items-baseline">
            <div class="text-lg font-medium">{{ props.chapter.chapter_name }}</div>
        </div>
    </Card>
</template>

<script setup>
import FossClubLogo from '@/components/FossClubLogo.vue';
import CityComunityBranding from '@/components/CityCommunityBranding.vue';

const props = defineProps({
    chapter: {
        type: Object,
        default: {},
    }
})
</script>
