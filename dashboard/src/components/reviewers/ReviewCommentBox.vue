<template>
  <ErrorMessage :message="errorMessages" class="text-sm -mb-4" /><br />
  <div>
    <div class="flex gap-2 items-center px-4 pt-4 border border-b-0 rounded-t">
      <span class="text-base text-ink-gray-5">Review: </span>
      <Button
        v-for="option in reviewOptions"
        :key="option.value"
        :label="option.label"
        :variant="draft.to_approve === option.value ? 'solid' : 'outline'"
        @click="draft.to_approve = option.value"
      />
    </div>
    <CommentBox
      v-model="draft.remarks"
      class="border-t-0 mt-0 rounded-t-none"
      :has-custom-actions="true"
      :custom-actions="getCustomAction()"
    />
    <div class="mt-4 pt-4 border-t border-outline-gray-2 flex flex-col gap-1.5">
      <div class="flex items-center justify-between gap-2">
        <Tooltip
          text="Internal note for organizers, co-chairs and other reviewers. Not shown to the proposer or on the public page."
        >
          <span class="text-xs text-ink-gray-5 w-fit">Private note (optional)</span>
        </Tooltip>
        <Tooltip
          text="Mark as favourite. Signals a strong preference for this proposal to organizers and reviewers."
        >
          <Button
            :variant="draft.favourite ? 'subtle' : 'ghost'"
            :label="draft.favourite ? 'Favourited' : 'Favourite'"
            @click="draft.favourite = draft.favourite ? 0 : 1"
          >
            <template #prefix>
              <IconHeart
                class="w-4 h-4"
                :class="draft.favourite ? 'text-ink-red-4' : 'text-ink-gray-5'"
                :fill="draft.favourite ? 'currentColor' : 'none'"
              />
            </template>
          </Button>
        </Tooltip>
      </div>
      <Textarea
        v-model="draft.private_comment"
        :rows="2"
        placeholder="Visible only to organizers and reviewers, not the proposer"
      />
    </div>
  </div>
</template>
<script setup>
import { createResource, ErrorMessage, Tooltip, Textarea } from 'frappe-ui'
import { ref, inject } from 'vue'
import CommentBox from '@/components/ui/CommentBox.vue'
import { IconHeart } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import { useStorage } from '@vueuse/core'

const emits = defineEmits(['add:review', 'update:review'])

const session = inject('$session')

const props = defineProps({
  submissionId: {
    type: String,
    required: true,
  },
  review: {
    type: Object,
    default: () => ({
      remarks: '',
      to_approve: 'Yes',
    }),
  },
  inEdit: {
    type: Boolean,
    default: false,
  },
})

// Draft keyed per review identity ("new" when unsaved): a fresh edit seeds from
// the existing review, a mid-edit refresh restores the draft, and clearDraft on
// save makes the next open start from backend data.
const storageKey = `cfp-review-draft-${props.submissionId}-${props.review.name || 'new'}`
const draft = useStorage(storageKey, {
  to_approve: props.review.to_approve || 'Yes',
  remarks: props.review.remarks || '',
  favourite: props.review.favourite || 0,
  private_comment: props.review.private_comment || '',
})

const clearDraft = () => localStorage.removeItem(storageKey)

const reviewFields = () => ({
  remarks: draft.value.remarks,
  to_approve: draft.value.to_approve,
  favourite: draft.value.favourite ? 1 : 0,
  private_comment: draft.value.private_comment,
})

const reviewOptions = [
  { label: 'Approve', value: 'Yes' },
  { label: 'Reject', value: 'No' },
  { label: 'Not Sure', value: 'Maybe' },
]

const reviewerProfile = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS User Profile',
      filters: {
        user: session.user,
      },
      fields: ['name', 'full_name'],
    }
  },
  auto: true,
})

const errorMessages = ref('')

const validateRemark = () => {
  const errors = []

  if (
    draft.value.to_approve != 'Yes' &&
    (!draft.value.remarks || draft.value.remarks === '<p></p>')
  ) {
    errors.push('You cannot submit the review without adding remarks.')
  }
  return errors
}

const submitReview = () => {
  const errors = validateRemark()
  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }
  createResource({
    url: 'frappe.client.insert',
    makeParams() {
      return {
        doc: {
          doctype: 'FOSS Event CFP Review',
          parenttype: 'FOSS Event CFP Submission',
          parent: props.submissionId,
          parentfield: 'reviews',
          ...reviewFields(),
          reviewer_profile: reviewerProfile.data.name,
          reviewer: reviewerProfile.data.full_name,
        },
      }
    },
    auto: true,
    onSuccess() {
      errorMessages.value = ''
      clearDraft()
      emits('add:review')
    },
    onError(err) {
      errorMessages.value = err
      toast.error('Failed to submit review', err.message)
    },
  })
}

const editReview = () => {
  const errors = validateRemark()
  if (errors.length > 0) {
    errorMessages.value = errors.join('\n')
    return
  }
  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Event CFP Review',
        name: props.review.name,
        fieldname: reviewFields(),
      }
    },
    auto: true,
    onSuccess() {
      errorMessages.value = ''
      clearDraft()
      emits('update:review')
    },
    onError(err) {
      errorMessages.value = err
      toast.error('Failed to update review', err.message)
    },
  })
}

const getCustomAction = () => {
  if (props.inEdit) {
    return [editReview]
  }
  return [submitReview]
}
</script>
