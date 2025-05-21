<template>
  <div>
    <div class="flex gap-2 items-center px-4 pt-4 border border-b-0 rounded-t">
      <span class="text-base text-gray-600">Review: </span>
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
import { createResource } from 'frappe-ui'
import { ref, inject } from 'vue'
import CommentBox from '@/components/ui/CommentBox.vue'
import { toast } from 'vue-sonner'
import { filter } from 'lodash'

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

const review = ref(props.review.to_approve)
const remarks = ref(props.review.remarks)

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

const submitReview = () => {
  if ((review.value === "No" || review.value === "Maybe") && (!remarks.value || remarks.value === "<p></p>")) {
    toast.error('cannot submit review unless remarks are added')
  } else {
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
        emits('add:review')
      },
      onError(err) {
        toast.error('Failed to submit review', err.message)
      },
    })
  }
}

const editReview = () => {
  if ((review.value === "No" || review.value === "Maybe") && (!remarks.value || remarks.value === "<p></p>")) {
    toast.error('cannot submit review unless remarks are added')
  } else {
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
        emits('update:review')
      },
      onError(err) {
        toast.error('Failed to update review', err.message)
      },
    })
  }
}

const getCustomAction = () => {
  if (props.inEdit) {
    return [editReview]
  }
  return [submitReview]
}
</script>
