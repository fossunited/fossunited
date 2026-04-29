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
    <div v-if="eventCategories?.data?.length" class="flex flex-col gap-4 p-4 border-x border-b-0">
      <div v-for="category in eventCategories.data" :key="category.name" class="flex flex-col gap-1">
        <label class="text-sm font-medium text-ink-gray-7">{{ category.category_name }} <span class="text-xs text-ink-gray-5 font-normal">(Weight: {{ category.weight }})</span></label>
        <FormControl type="number" v-model="scores[category.name]" :placeholder="'Score for ' + category.category_name" />
      </div>
    </div>
    <CommentBox
      v-model="remarks"
      class="border-t-0 mt-0 rounded-t-none"
      :has-custom-actions="true"
      :custom-actions="getCustomAction()"
    />
    <div class="flex gap-2 items-center mt-4">
      <Button v-if="!inEdit" label="Save & Next" variant="solid" @click="handleSaveAndNext" />
      <Button v-if="!inEdit" label="Skip for Now" variant="outline" @click="$emit('next')" />
      <Button v-if="!inEdit" label="Abstain" variant="outline" @click="handleAbstain" />
    </div>
  </div>
</template>
<script setup>
import { createResource, ErrorMessage } from 'frappe-ui'
import { ref, inject, computed } from 'vue'
import CommentBox from '@/components/ui/CommentBox.vue'
import { toast } from 'vue-sonner'
import { filter } from 'lodash'
import { useStorage } from '@vueuse/core'

const emits = defineEmits(['add:review', 'update:review', 'next'])

const session = inject('$session')
const submissionDoc = inject('submission')
const submissionData = computed(() => submissionDoc?.data)
const eventCategories = inject('eventCategories')
console.log('ReviewCommentBox categories:', eventCategories?.data?.length)

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

const review = useStorage(`review-${props.submissionId}`, props.review.to_approve || 'Yes')
const remarks = useStorage(`remarks-${props.submissionId}`, props.review.remarks || '')
const scores = useStorage(`scores-${props.submissionId}`, {})

if (props.inEdit && props.review.scores) {
  props.review.scores.forEach(s => {
    scores.value[s.category] = s.score
  })
}

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

async function closeAssignedTodo() {
  const todoName = await createResource({
    url: 'frappe.client.get_value',
    params: {
      doctype: 'ToDo',
      filters: {
        reference_type: 'FOSS Event CFP Submission',
        reference_name: props.submissionId,
        allocated_to: session.user,
        status: 'Open',
      },
      fieldname: 'name',
    },
    auto: true,
  }).promise
  if (todoName)
    createResource({
      url: 'frappe.client.set_value',
      params: { doctype: 'ToDo', name: todoName, fieldname: 'status', value: 'Closed' },
      auto: true,
    })
}

const validateRemark = () => {
  const errors = []

  if (review.value != 'Yes' && (!remarks.value || remarks.value === '<p></p>')) {
    errors.push('You cannot submit the review without adding remarks.')
  }
  return errors
}

const submitReview = (onSuccessCallback) => {
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
          proposal: props.submissionId,
          remarks: remarks.value,
          to_approve: review.value,
          reviewer_profile: reviewerProfile.data.name,
          reviewer: reviewerProfile.data.full_name,
          scores: Object.keys(scores.value).map(cat => ({ category: cat, score: scores.value[cat] }))
        },
      }
    },
    auto: true,
    onSuccess() {
      errorMessages.value = ''
      emits('add:review')
      closeAssignedTodo()
      if (onSuccessCallback) onSuccessCallback()
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
          proposal: props.submissionId,
          remarks: remarks.value,
          to_approve: review.value,
          scores: Object.keys(scores.value).map(cat => ({ category: cat, score: scores.value[cat] }))
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

const handleSaveAndNext = () => {
  submitReview(() => {
    emits('next')
  })
}

const handleAbstain = () => {
  review.value = 'Abstain'
  remarks.value = remarks.value || 'Abstained'
  handleSaveAndNext()
}
</script>
