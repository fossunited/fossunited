<template>
    <div class="flex flex-col gap-3 mt-5 md:mt-0">
        <div v-if="chapter.doc">
            <FossClubBranding v-if="chapter.doc.chapter_type == 'FOSS Club'">{{ chapter.doc.chapter_name }}</FossClubBranding>
            <CityCommunityBranding v-else >{{ chapter.doc.chapter_name }}</CityCommunityBranding>
        </div>
        <div class="flex gap-3">
            <div class="text-3xl font-semibold">{{ event.doc.event_name }}</div>
            <Badge
            v-if="form_exists && form.data"
            :theme="form.data.is_published ? 'green' : 'gray'"
            size='md'
            >
            <div class="font-medium">
                <div v-if="form.data.is_published" class="flex items-center">
                    <span class="relative flex h-3 w-3 mr-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <span>{{form.data.doctype.split(" ").pop()}} Live</span>
                </div>
                <div v-else>
                    <span>{{form.data.doctype.split(" ").pop()}} Unpublished</span>
                </div>
            </div>
            </Badge>
            <Badge
                v-if="!form_exists"
                :theme="'gray'"
                size='md'
            >
            <div class="font-medium">
                <span>
                    Form Not Created
                </span>
            </div>
            </Badge>
        </div>
        <div class="flex gap-2 items-center text-base text-gray-700">
            <div>
                {{ event.doc.event_type }}
            </div>
            <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="currentColor"  class="fill-gray-600 w-2 h-2 icon icon-tabler icons-tabler-filled icon-tabler-circle"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M7 3.34a10 10 0 1 1 -4.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 4.995 -8.336z" /></svg>
            <div>
                <span>
                    {{ getFormattedDate(event.doc.event_start_date) }}
                </span>
                <span v-if="event.doc.event_start_date != event.doc.event_end_date">
                    - {{ getFormattedDate(event.doc.event_end_date) }}
                </span>
            </div>
        </div>
    </div>
</template>
<script setup>
import { defineProps } from 'vue';
import { createDocumentResource, Badge } from 'frappe-ui';

import CityCommunityBranding from '@/components/CityCommunityBranding.vue'
import FossClubBranding from '@/components/FossClubBranding.vue'

const props = defineProps({
    event: {
        type: Object,
        default: null
    },
    form_exists: {
        type: Boolean,
        default: false
    },
    form: {
        type: Object,
        default: null
    }
})

function getFormattedDate(date) {
    return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month:'long', year: 'numeric'});
}

const chapter = createDocumentResource({
    doctype: 'FOSS Chapter',
    name: props.event.doc.chapter,
    fields: ['*'],
    auto: true,
})

</script>
