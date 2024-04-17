<template>
<div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0">
    <div v-if="showToast" class="z-10 absolute">
        <Toast
            :class="toastTitle == 'Success' ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'"
            :icon="toastTitle == 'Success' ? 'check-circle' : 'x'"
            icon-classes="stroke-2"
            :title="toastTitle"
            :text="toastMessage"
            position="bottom-right"
        ></Toast>
    </div>
    <div class="flex flex-col md:flex-row my-4 gap-4 md:justify-between">
        <div class="flex flex-col gap-3">
            <FossClubBranding v-if="chapter.doc.chapter_type == 'FOSS Club'">{{ chapter.doc.chapter_type }}</FossClubBranding>
            <CityCommunityBranding v-else>{{ chapter.doc.chapter_type }}</CityCommunityBranding>
            <div class="text-3xl font-semibold">{{ chapter.doc.chapter_name }}</div>
        </div>
        <Button
            class="w-fit"
            size="md"
            label="Update Details"
            icon-left="edit"
            @click="updateDetails()"
        ></Button>
    </div>
    <div class="flex flex-col my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Banner Image</div>
        <div class="p-2 my-1">
            <img :src="getBannerImage()" alt="Banner Image" class="object-cover rounded-lg aspect-[4.96/1]">
            <div class="flex my-2 gap-2">
                <FileUploader
                    :fileTypes="'image/*'"
                    :validateFile="validateFile"
                    @success="(file) => setBannerImage(file)"
                >
                    <template v-slot="{ file, progress, error, uploading, openFileSelector }">
                        <Button
                            :variant="'subtle'"
                            :size="'md'"
                            :label="uploading ? `Uploading ${progress}` : chapter.doc.banner_image ? 'Change Banner Image' : 'Upload Banner Image'"
                            @click="openFileSelector"
                        />
                    </template>
                </FileUploader>
                <Button
                    v-if="chapter.doc.banner_image"
                    :variant="'subtle'"
                    theme="red"
                    :size="'md'"
                    :label="'Remove Banner Image'"
                    @click="() => setBannerImage({ file_url: '' })"
                />
            </div>
            <div class="text-sm text-gray-600">The ideal dimensions for a banner image are: 1240 x 300 (WxH)</div>
        </div>
    </div>
    <div class="flex flex-col my-6">
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Edit Details</div>
        <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl
                :type="'text'"
                size="md"
                :disabled="true"
                v-model="chapter.doc.chapter_name"
                :label="chapter.doc.chapter_type == 'FOSS Club' ? 'Club Name' : 'Community Name'"

            />
            <FormControl
                :type="'text'"
                size="md"
                :disabled="true"
                v-model="chapter.doc.chapter_type"
                label="Chapter Type"
            />
            <div class="col-span-2">
                <!-- ToDo: Use a TextEditor in place of a FormControl -->
                <FormControl
                    :type="'textarea'"
                    size="md"
                    v-model="chapter.doc.about_chapter"
                    label="About chapter"
                />
            </div>
        </div>
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Location</div>
        <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl
                :type="'text'"
                :disabled="true"
                size="md"
                v-model="chapter.doc.city"
                label="City"
            />
            <FormControl
                :type="'text'"
                size="md"
                :disabled="true"
                v-model="chapter.doc.state"
                label="State"
            />
            <FormControl
                :type="'text'"
                size="md"
                :disabled="true"
                v-model="chapter.doc.country"
                label="Country"
            />
            <FormControl
                :type="'text'"
                size="md"
                v-model="chapter.doc.google_map_link"
                label="Map Link"
            />
        </div>
        <div class="font-semibold text-gray-800 border-b-2 pb-2">Socials</div>
        <p class=" mt-2 text-base text-gray-600 leading-normal">Add your social media links to help people connect with you.
            <br>Please enter the whole url of your social media profile. <i>Eg: https://twitter.com/fossunited</i>
        </p>
        <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormControl
                :type="'email'"
                size="md"
                v-model="chapter.doc.email"
                label="Email"
            >
                <template #prefix>
                    <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-at"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" /><path d="M16 12v1.5a2.5 2.5 0 0 0 5 0v-1.5a9 9 0 1 0 -5.5 8.28" /></svg>
                </template>
            </FormControl>
            <FormControl
                :type="'url'"
                size="md"
                v-model="chapter.doc.x"
                label="Twitter"
            >
            <template #prefix>
                <svg xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-x"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 4l11.733 16h4.267l-11.733 -16z" /><path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772" /></svg>
            </template>
            </FormControl>
            <FormControl
                :type="'url'"
                size="md"
                v-model="chapter.doc.facebook"
                label="Facebook"
            >
            <template #prefix>
                <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-facebook"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M7 10v4h3v7h4v-7h3l1 -4h-4v-2a1 1 0 0 1 1 -1h3v-4h-3a5 5 0 0 0 -5 5v2h-3" /></svg>
            </template>
            </FormControl>
            <FormControl
                :type="'url'"
                size="md"
                v-model="chapter.doc.linkedin"
                label="LinkedIn"
            >
            <template #prefix>
                <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-linkedin"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z" /><path d="M8 11l0 5" /><path d="M8 8l0 .01" /><path d="M12 16l0 -5" /><path d="M16 16v-3a2 2 0 0 0 -4 0" /></svg>
            </template>
            </FormControl>
            <FormControl
                :type="'url'"
                size="md"
                v-model="chapter.doc.instagram"
                label="Instagram"
            >
            <template #prefix>
                <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-instagram"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M4 4m0 4a4 4 0 0 1 4 -4h8a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-8a4 4 0 0 1 -4 -4z" /><path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" /><path d="M16.5 7.5l0 .01" /></svg>
            </template>
            </FormControl>
            <FormControl
                :type="'url'"
                size="md"
                v-model="chapter.doc.mastodon"
                label="Mastodon"
            >
            <template #prefix>
                <svg  xmlns="http://www.w3.org/2000/svg"  width="24"  height="24"  viewBox="0 0 24 24"  fill="none"  stroke="currentColor"  stroke-width="2"  stroke-linecap="round"  stroke-linejoin="round"  class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-mastodon"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M18.648 15.254c-1.816 1.763 -6.648 1.626 -6.648 1.626a18.262 18.262 0 0 1 -3.288 -.256c1.127 1.985 4.12 2.81 8.982 2.475c-1.945 2.013 -13.598 5.257 -13.668 -7.636l-.026 -1.154c0 -3.036 .023 -4.115 1.352 -5.633c1.671 -1.91 6.648 -1.666 6.648 -1.666s4.977 -.243 6.648 1.667c1.329 1.518 1.352 2.597 1.352 5.633s-.456 4.074 -1.352 4.944z" /><path d="M12 11.204v-2.926c0 -1.258 -.895 -2.278 -2 -2.278s-2 1.02 -2 2.278v4.722m4 -4.722c0 -1.258 .895 -2.278 2 -2.278s2 1.02 2 2.278v4.722" /></svg>
            </template>
            </FormControl>
        </div>
    </div>
</div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, FormControl, FileUploader, Toast, toast } from 'frappe-ui'
import CityCommunityBranding from '@/components/CityCommunityBranding.vue'
import FossClubBranding from '@/components/FossClubBranding.vue'
import { ref } from 'vue'
const route = useRoute()

const chapter = createDocumentResource({
    doctype: 'FOSS Chapter',
    name: route.params.id,
    fields: ['*'],
    auto: true,
})

const getBannerImage = () => {
    if (chapter.doc.banner_image) {
        return chapter.doc.banner_image
    } else if (chapter.doc.chapter_type == 'FOSS Club') {
        return '/assets/fossunited/images/chapter/foss_club_banner.png'
    } else {
        return '/assets/fossunited/images/chapter/city_community_banner.png'
    }
}

const validateFile = (file) => {
      let extn = file.name.split('.').pop().toLowerCase()
      if (!['png', 'jpg'].includes(extn)) {
        return 'Only PNG and JPG images are allowed'
      }
}
const setBannerImage = (file) => {
    chapter.setValue.submit({
        banner_image: file.file_url
    })
}

let showToast = ref(false)
let toastTitle = ref('')
let toastMessage = ref('')

const updateDetails = () => {
    chapter.save.submit().then(() => {
        showToastMessage('Success', 'Chapter details updated successfully')
    }).catch((error) => {
        showToastMessage('Error', error.message)
    })
}

const showToastMessage = (title, message) => {
    toastTitle.value = title
    toastMessage.value = message
    showToast.value = true
    setTimeout(() => {
        showToast.value = false
    }, 5000)
}

</script>
