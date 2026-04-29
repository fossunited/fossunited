<template>
  <div class="flex flex-col gap-4">
    <div class="space-y-2">
      <h3 class="text-2xl font-semibold">Preview Submission</h3>
      <p class="text-sm text-ink-gray-5">Review the details of your proposal before submitting.</p>
    </div>
    <div class="border p-4 md:p-8 bg-surface-white rounded">
      <div class="flex flex-col gap-3">
        <h4 class="text-xl font-medium">
          {{ getValueFromProposal('talk_title') }}
        </h4>
        <div class="text-sm flex gap-2 items-center">
          <Badge
            :label="getValueFromProposal('session_type')"
            variant="outline"
            theme="blue"
            size="lg"
          ></Badge>
          <Badge
            :label="getValueFromProposal('intended_audience')"
            variant="outline"
            theme="gray"
            size="lg"
          >
            <template #prefix>
              <IconUsersGroup class="h-4 w-4" />
            </template>
          </Badge>
        </div>
        <RenderSessionCategories :categories="getValueFromProposal('session_categories')" />
        <div class="space-y-2">
          <h5 class="text-base font-medium text-ink-gray-5">Session Description</h5>
          <div
            class="prose prose-sm border-l pl-2 border-outline-gray-3"
            v-html="getValueFromProposal('talk_description')"
          ></div>
        </div>
        <div v-if="getValueFromProposal('key_takeaways')" class="space-y-2">
          <h5 class="text-base font-medium text-ink-gray-5">Key Takeaways</h5>
          <div
            class="prose prose-sm border-l pl-2 border-outline-gray-3"
            v-html="getValueFromProposal('key_takeaways')"
          ></div>
        </div>
        <RenderReferences :references="proposalReferences" />
        <div class="space-y-2">
          <h5 class="text-base font-medium text-ink-gray-5">Speakers</h5>
          <div class="flex flex-col gap-2">
            <SpeakerCard
              v-for="(speaker, index) in proposalSpeakers"
              :key="index"
              :speaker="speaker"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="flex flex-col gap-2">
      <div v-for="(field, index) in confirmationFields" :key="index">
        <template v-if="field.fieldname === 'accept_coc'">
          <div class="inline-flex space-x-2 rounded transition">
            <input
              id="coc-cfp"
              v-model="field.value"
              type="checkbox"
              class="rounded-sm mt-[1px] bg-surface-white border-outline-gray-4 text-ink-gray-9 hover:border-outline-gray-5 focus:ring-offset-0 focus:border-outline-gray-8 active:border-outline-gray-6 transition hover:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 active:bg-surface-gray-2 w-3.5 h-3.5 shrink-0"
            />
            <label for="coc-cfp" class="block text-base font-medium text-ink-gray-8 select-none cursor-pointer leading-relaxed">
              By registering for this event, you agree to abide by the FOSS United
              <a
                href="https://fossunited.org/code-of-conduct"
                target="_blank"
                rel="noopener noreferrer"
                class="font-semibold underline"
                >Code of Conduct</a
              >. The code of conduct and anti-harassment policies apply to everyone participating
              in the event including sponsors, judges, mentors, volunteers, organisers and the FOSS
              United staff.<span class="text-ink-red-3 ml-0.5">*</span>
            </label>
          </div>
        </template>
        <template v-else>
          <FormControl
            v-model="field.value"
            type="checkbox"
            :label="field.label"
            :required="field.required"
          />
        </template>
      </div>
    </div>
  </div>
</template>
<script setup>
import RenderReferences from './RenderReferences.vue'
import RenderSessionCategories from './RenderSessionCategories.vue'
import SpeakerCard from './SpeakerCard.vue'
import { IconUsersGroup } from '@tabler/icons-vue'
import { Badge, FormControl } from 'frappe-ui'

const props = defineProps({
  proposalFields: {
    type: Object,
    required: true,
  },
  proposalReferences: {
    type: Object,
    required: true,
  },
  proposalSpeakers: {
    type: Object,
    required: true,
  },
})

const confirmationFields = defineModel('confirmationFields', {
  type: Array,
  required: true,
})

const getValueFromProposal = (fieldname) => {
  const proposalField = props.proposalFields.find((field) => field.fieldname === fieldname)
  if (proposalField) {
    return proposalField.value
  }
}
</script>
