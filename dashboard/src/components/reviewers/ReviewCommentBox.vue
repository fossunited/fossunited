<template>
  <ErrorMessage :message="errorMessages" class="text-sm -mb-4" /><br />
  <div>
    <div class="flex gap-2 items-center px-4 pt-4 border border-b-0 rounded-t">
      <span class="text-base text-ink-gray-5">Review: </span>
      <Button
        v-for="option in reviewOptions"
        :key="option.value"
        :label="option.label"
        :variant="review === option.value ? 'solid' : 'outline'"
        @click="review = option.value"
      />
    </div>
    <CommentBox
      v-model="remarks"
      class="border-t-0 mt-0 rounded-t-none"
      :has-custom-actions="true"
      :custom-actions="getCustomAction()"
    />
  </div>
</template>
<script setup>
import { createResource, ErrorMessage } from 'frappe-ui'
import { ref, inject } from 'vue'
import CommentBox from '@/components/ui/CommentBox.vue'
import { toast } from 'vue-sonner'
import { filter } from 'lodash'
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

const review = useStorage(`review-${props.submissionId}`, props.review.to_approve)
const remarks = useStorage(`remarks-${props.submissionId}`, props.review.remarks)

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

  if (review.value != 'Yes' && (!remarks.value || remarks.value === '<p></p>')) {
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
          remarks: remarks.value,
          to_approve: review.value,
          reviewer_profile: reviewerProfile.data.name,
          reviewer: reviewerProfile.data.full_name,
        },
      }
    },
    auto: true,
    onSuccess() {
      errorMessages.value = ''
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
        fieldname: {
          remarks: remarks.value,
          to_approve: review.value,
        },
      }
    },
    auto: true,
    onSuccess() {
      errorMessages.value = ''
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
