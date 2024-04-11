<template>
    <Card>
        <template  #actions-left>
            <FossClubLogo v-if="props.chapter.chapter_type == 'FOSS Club'" class="w-7 h-7 "></FossClubLogo>
            <div v-else class="w-fit font-fff text-xs bg-gray-900 text-white p-2 rounded-sm flex text-center">{{ props.chapter.chapter_type.toUpperCase() }}</div>
        </template>
        <div class="flex justify-between items-baseline">
            <div class="text-lg font-medium">{{ props.chapter.chapter_name }}</div>
            <Button
                :variant="'ghost'"
                :size="'sm'"
                label="Manage"
                iconRight="chevron-right"
            >
            </Button>
        </div>
    </Card>
</template>

<script setup>
import Button from 'frappe-ui/src/components/Button.vue';
import FossClubLogo from '@/components/FossClubLogo.vue';

const props = defineProps({
    chapter: {
        type: Object,
        default: {},
    }
})
</script>
