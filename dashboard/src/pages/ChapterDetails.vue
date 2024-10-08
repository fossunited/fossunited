<template>
  <div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0">
    <div class="flex flex-col md:flex-row my-4 gap-4 md:justify-between">
      <ChapterHeader :chapter="chapter" />
      <div class="flex justify-between items-start gap-5 md:flex-col md:items-end">
        <Button
          class="w-fit"
          size="md"
          label="Update Details"
          icon-left="edit"
          @click="updateDetails()"
        ></Button>
        <Button
          class="w-fit bg-green-600 text-white hover:bg-green-700 disabled:opacity-80 disabled:text-white disabled:cursor-not-allowed"
          size="md"
          label="See on website"
          icon-left="external-link"
          @click="redirectRoute(`${chapter.doc.route}`)"
          :disabled="!chapter.doc.is_published"
        ></Button>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Banner Image</div>
      <div class="p-2 my-1">
        <img
          :src="getBannerImage()"
          alt="Banner Image"
          class="object-cover rounded-lg w-full aspect-[4.96/1]"
        />
        <div class="flex my-2 gap-2">
          <FileUploader
            :file-types="'image/*'"
            :validate-file="validateFile"
            @success="(file) => setBannerImage(file)"
          >
            <template #default="{ progress, uploading, openFileSelector }">
              <Button
                :variant="'subtle'"
                :size="'md'"
                :label="
                  uploading
                    ? `Uploading ${progress}`
                    : chapter.doc.banner_image
                      ? 'Change Image'
                      : 'Upload Image'
                "
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="chapter.doc.banner_image"
            :variant="'subtle'"
            theme="red"
            :size="'md'"
            :label="'Remove Image'"
            @click="() => setBannerImage({ file_url: '' })"
          />
        </div>
        <div class="text-sm text-gray-600">
          The ideal dimensions for a banner image are: 1240 x 300 (WxH)
        </div>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Edit Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl
          v-model="chapter.doc.chapter_name"
          :type="'text'"
          size="md"
          :disabled="true"
          :label="chapter.doc.chapter_type == 'FOSS Club' ? 'Club Name' : 'Community Name'"
        />
        <FormControl
          v-model="chapter.doc.chapter_type"
          :type="'text'"
          size="md"
          :disabled="true"
          label="Chapter Type"
        />
        <div class="col-span-2">
          <TextEditor
            label="About Chapter"
            placeholder="Write a description about the chapter"
            :model-value="chapter.doc.about_chapter"
            @update:model-value="($event) => (chapter.doc.about_chapter = $event)"
          />
        </div>
      </div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Location</div>
      <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl
          v-model="chapter.doc.city"
          :type="'text'"
          :disabled="true"
          size="md"
          label="City"
        />
        <FormControl
          v-model="chapter.doc.state"
          :type="'text'"
          size="md"
          :disabled="true"
          label="State"
        />
        <FormControl
          v-model="chapter.doc.country"
          :type="'text'"
          size="md"
          :disabled="true"
          label="Country"
        />
        <FormControl
          v-model="chapter.doc.google_map_link"
          :type="'text'"
          size="md"
          label="Map Link"
        />
      </div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Socials</div>
      <p class="mt-2 text-base text-gray-600 leading-normal">
        Add your social media links to help people connect with you.
        <br />Please enter the whole url of your social media profile.
        <i>Eg: https://twitter.com/fossunited</i>
      </p>
      <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl v-model="chapter.doc.email" :type="'email'" size="md" label="Email">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-at"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0" />
              <path d="M16 12v1.5a2.5 2.5 0 0 0 5 0v-1.5a9 9 0 1 0 -5.5 8.28" />
            </svg>
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.x" :type="'url'" size="md" label="Twitter">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-x"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M4 4l11.733 16h4.267l-11.733 -16z" />
              <path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772" />
            </svg>
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.facebook" :type="'url'" size="md" label="Facebook">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-facebook"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M7 10v4h3v7h4v-7h3l1 -4h-4v-2a1 1 0 0 1 1 -1h3v-4h-3a5 5 0 0 0 -5 5v2h-3" />
            </svg>
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.linkedin" :type="'url'" size="md" label="LinkedIn">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-linkedin"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path
                d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"
              />
              <path d="M8 11l0 5" />
              <path d="M8 8l0 .01" />
              <path d="M12 16l0 -5" />
              <path d="M16 16v-3a2 2 0 0 0 -4 0" />
            </svg>
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.instagram" :type="'url'" size="md" label="Instagram">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-instagram"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path
                d="M4 4m0 4a4 4 0 0 1 4 -4h8a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-8a4 4 0 0 1 -4 -4z"
              />
              <path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" />
              <path d="M16.5 7.5l0 .01" />
            </svg>
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.mastodon" :type="'url'" size="md" label="Mastodon">
          <template #prefix>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="w-5 text-gray-800 icon icon-tabler icons-tabler-outline icon-tabler-brand-mastodon"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path
                d="M18.648 15.254c-1.816 1.763 -6.648 1.626 -6.648 1.626a18.262 18.262 0 0 1 -3.288 -.256c1.127 1.985 4.12 2.81 8.982 2.475c-1.945 2.013 -13.598 5.257 -13.668 -7.636l-.026 -1.154c0 -3.036 .023 -4.115 1.352 -5.633c1.671 -1.91 6.648 -1.666 6.648 -1.666s4.977 -.243 6.648 1.667c1.329 1.518 1.352 2.597 1.352 5.633s-.456 4.074 -1.352 4.944z"
              />
              <path
                d="M12 11.204v-2.926c0 -1.258 -.895 -2.278 -2 -2.278s-2 1.02 -2 2.278v4.722m4 -4.722c0 -1.258 .895 -2.278 2 -2.278s2 1.02 2 2.278v4.722"
              />
            </svg>
          </template>
        </FormControl>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, FormControl, FileUploader } from 'frappe-ui'
import ChapterHeader from '@/components/ChapterHeader.vue'
import { redirectRoute } from '@/helpers/utils'
import { toast } from 'vue-sonner'
import TextEditor from '@/components/TextEditor.vue'

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
    banner_image: file.file_url,
  })
  if (file.file_url) {
    toast.success('Banner Image updated successfully')
  } else {
    toast.info('Banner Image removed successfully')
  }
}

const updateDetails = () => {
  chapter.save
    .submit()
    .then(() => {
      toast.success('Chapter details updated successfully')
    })
    .catch((error) => {
      toast.error('Failed to update chapter details', {
        description: error.message,
      })
    })
}
</script>
