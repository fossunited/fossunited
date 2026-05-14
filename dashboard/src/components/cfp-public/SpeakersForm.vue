<template>
  <section
    aria-label="Speaker Information"
    class="flex flex-col gap-6 w-full p-4 md:p-8 border rounded bg-surface-white"
  >
    <h4 v-if="showTitle" class="flex gap-2 items-center font-semibold">
      <IconUserCircle aria-hidden="true" />
      <span>Speaker Information</span>
    </h4>
    <div :class="speakers.length > 1 ? 'grid md:grid-cols-2 gap-8' : 'flex flex-col gap-8'">
      <div
        v-for="(speaker, index) in speakers"
        :key="index"
        role="group"
        :aria-label="`Speaker ${index + 1}`"
        class="flex flex-col gap-4 p-6 border rounded border-outline-gray-2"
      >
        <div
          v-if="speakers.length > 1"
          class="border-b border-outline-gray-4 pb-2 flex justify-between"
        >
          <h5 class="font-medium text-base">Speaker #{{ index + 1 }}</h5>
          <Button
            icon="trash"
            theme="red"
            :aria-label="`Remove Speaker ${index + 1}`"
            @click="deleteSpeaker(index)"
          />
        </div>
        <FileUploaderArea
          v-model="speaker[getFieldIndex(speaker, 'photo')].value"
          label="Speaker Image"
          :description="
            index === 0
              ? 'Pre-filled from your account profile. Uploading a new photo here will also update your profile. Keep a recent 1:1 headshot for best results.'
              : 'Please keep the image ratio as 1:1'
          "
          :required="true"
          @uploaded="index === 0 && syncProfilePhoto($event)"
        />
        <RenderField
          v-for="(field, _index) in fields"
          :key="_index"
          v-model:fields="speakers[index]"
          :field="field"
        />
        <TextEditor
          v-model="speaker[getFieldIndex(speaker, 'bio')].value"
          label="Speaker Bio"
          required="true"
          description="A short bio of the speaker"
        />
      </div>
    </div>
    <Button label="Add Speaker" icon-left="plus" class="w-fit" @click="addSpeaker" />

    <div class="flex items-center gap-3 pt-2 border-t border-outline-gray-2">
      <Switch v-model="subscribeNewsletter" />
      <span class="text-sm text-ink-gray-7 leading-relaxed">
        Subscribe to the
        <a
          href="https://fossunited.org/newsletter"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold underline"
          >FOSS United newsletter</a
        >
        for updates on upcoming events and community news.
      </span>
    </div>
  </section>
</template>
<script setup>
import FileUploaderArea from '@/components/ui/FileUploaderArea.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { IconUserCircle } from '@tabler/icons-vue'
import RenderField from '@/components/form/RenderField.vue'
import { getSpeakerFields } from '@/helpers/cfp'
import { createResource, Switch } from 'frappe-ui'
import { inject, ref } from 'vue'

const speakers = defineModel('speakers', {
  type: Array,
  required: true,
})

const subscribeNewsletter = defineModel('subscribeNewsletter', {
  type: Boolean,
  default: false,
})

const props = defineProps({
  showTitle: {
    type: Boolean,
    default: true,
  },
})

const fields = getSpeakerFields().filter((field) => !['photo', 'bio'].includes(field.fieldname))

const addSpeaker = () => {
  speakers.value.push(getSpeakerFields())
}

const deleteSpeaker = (index) => {
  speakers.value.splice(index, 1)
}

const getFieldIndex = (speaker, fieldname) => {
  return speaker.findIndex((field) => field.fieldname === fieldname)
}

const session = inject('$session')

const SOCIAL_PRIORITY = ['website', 'linkedin', 'github', 'x', 'mastodon', 'bluesky', 'gitlab']

const profileData = ref(null)
const speakerData = ref(null)
const profileReady = ref(false)
const speakerReady = ref(false)

const resolve = (setter, value) => {
  setter(value)
  if (profileReady.value && speakerReady.value) mergeAndPrefill()
}

createResource({
  url: 'frappe.client.get_list',
  makeParams: () => ({
    doctype: 'FOSS User Profile',
    filters: { user: session?.user },
    fields: ['name', 'full_name', 'email', 'profile_photo', 'about', 'bio', ...SOCIAL_PRIORITY],
    limit: 1,
  }),
  auto: !!session?.user,
  onSuccess(data) {
    profileData.value = data?.[0] || null
    resolve(() => (profileReady.value = true))
  },
  onError() {
    resolve(() => (profileReady.value = true))
  },
})

createResource({
  url: 'fossunited.api.cfp.get_my_latest_speaker_entry',
  auto: !!session?.user,
  onSuccess(data) {
    speakerData.value = data || null
    resolve(() => (speakerReady.value = true))
  },
  onError() {
    resolve(() => (speakerReady.value = true))
  },
})

function mergeAndPrefill() {
  const p = profileData.value
  const s = speakerData.value

  // Profile is authoritative for its own fields.
  // Speaker entry fills in fields the profile doesn't have.
  const merged = {
    photo: p?.profile_photo || s?.photo || '',
    full_name: p?.full_name || '',
    email: p?.email || '',
    bio: p?.about || p?.bio || '',
    social_link: SOCIAL_PRIORITY.map((k) => p?.[k]).find(Boolean) || s?.social_link || '',
    designation: s?.designation || '',
    organization: s?.organization || '',
    contact_info: s?.contact_info || '',
  }

  const first = speakers.value[0]
  if (!first) return
  Object.entries(merged).forEach(([fieldname, value]) => {
    const idx = first.findIndex((f) => f.fieldname === fieldname)
    if (idx !== -1 && !first[idx].value) first[idx].value = value
  })
}

const updateProfilePhoto = createResource({ url: 'frappe.client.set_value' })

function syncProfilePhoto(url) {
  if (!profileData.value?.name) return
  updateProfilePhoto.fetch({
    doctype: 'FOSS User Profile',
    name: profileData.value.name,
    fieldname: 'profile_photo',
    value: url,
  })
}
</script>
