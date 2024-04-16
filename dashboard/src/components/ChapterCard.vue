<template>
    <Card>
        <template #actions-left>
            <FossClubLogo v-if="props.chapter.chapter_type == 'FOSS Club'" class="w-7 h-7 "></FossClubLogo>
            <CityComunityBranding v-else>{{ props.chapter.chapter_type }}</CityComunityBranding>
        </template>
        <div class="flex justify-between items-baseline">
            <div class="text-lg font-medium">{{ props.chapter.chapter_name }}</div>
            <Button
                :variant="'ghost'"
                :size="'sm'"
                label="Manage"
                iconRight="chevron-right"
                :route="'/chapter/' + props.chapter.name"
            >
            </Button>
        </div>
    </Card>
</template>

<script setup>
import Button from 'frappe-ui/src/components/Button.vue';
import FossClubLogo from '@/components/FossClubLogo.vue';
import CityComunityBranding from '@/components/CityCommunityBranding.vue';

const props = defineProps({
    chapter: {
        type: Object,
        default: {},
    }
})
</script>
