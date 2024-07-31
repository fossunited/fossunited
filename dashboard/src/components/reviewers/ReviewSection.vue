<template>
  <div class="prose min-w-full">
    <h2 class="mb-2">Your Review</h2>
    <div v-if="in_review_edit" class="flex flex-col gap-2">
      <RadioGroup v-model="selectedReviewOption">
        <RadioGroupLabel class="text-sm uppercase">Your Review</RadioGroupLabel>
        <div class="flex gap-2 my-1">
          <RadioGroupOption
            v-slot="{ checked }"
            v-for="option in reviewOptions"
            :key="option.value"
            :value="option"
          >
            <Button
              :label="option.label"
              :variant="checked ? 'solid' : 'outline'"
              size="md"
            />
          </RadioGroupOption>
        </div>
      </RadioGroup>
      <FormControl
        label="Remarks"
        v-model="newRemarks"
        type="textarea"
        placeholder="Enter your remarks here"
      />
      <ErrorMessage :message="errors" />
      <Button
        class="w-fit"
        :label="reviewData.data ? 'Update Review' : 'Submit Review'"
        @click="handleReviewSubmit"
      />
    </div>
    <div v-else>
      <div
        v-if="hasReviewed.data && reviewData.data"
        class="text-base flex flex-col gap-4"
      >
        <div>
          <span>Your Review: </span>
          <span
            class="font-medium"
            :class="
              {
                Yes: 'text-green-600',
                No: 'text-red-600',
                Maybe: 'text-orange-600',
              }[selectedReviewOption.value]
            "
            >{{ selectedReviewOption.label }}</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <div class="text-md font-semibold">Remarks</div>
          <div>{{ reviewData.data.remarks }}</div>
        </div>
        <Button label="Edit Review" @click="in_review_edit = true" class="w-fit" size="sm"/>
      </div>
      <div v-else>
        <LoadingIndicator class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource, LoadingIndicator, FormControl, ErrorMessage } from 'frappe-ui'
import { defineProps, inject, ref } from 'vue'
import { useRoute } from 'vue-router'
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'

const props = defineProps({
  submission: Object,
})
const route = useRoute()
const session = inject('$session')

const in_review_edit = ref(false)
const reviewOptions = ref([
  { value: 'Yes', label: 'Approve' },
  { value: 'No', label: 'Reject' },
  { value: 'Maybe', label: 'Unsure' },
])
const newRemarks = ref('')
const errors = ref('')

const selectedReviewOption = ref(reviewOptions.value[0])

const hasReviewed = createResource({
  url: 'fossunited.api.reviewer.has_cfp_review',
  makeParams() {
    return {
      submission_id: route.params.talk_id,
    }
  },
  onSuccess(data) {
    if (!data) {
        in_review_edit.value = true
      return
    }
    reviewData.fetch()
  },
  auto: true,
})

const reviewData = createResource({
  url: 'fossunited.api.reviewer.get_review',
  makeParams() {
    return {
      submission_id: route.params.talk_id,
    }
  },
  onSuccess(data) {
    newRemarks.value = data.remarks
    selectedReviewOption.value = reviewOptions.value.find(
      (option) => option.value == data.to_approve,
    )
  },
})

const handleReviewSubmit = () => {
    if(!selectedReviewOption.value){
        errors.value = 'Please select a review option'
        return
    }

    if (reviewData.data){
        updateReview()
        return
    }

    submitReview()
}

const updateReview = () => {
    createResource({
        url: 'frappe.client.set_value',
        makeParams() {
            return {
                doctype: 'FOSS Event CFP Review',
                name: reviewData.data.name,
                fieldname: {
                    to_approve: selectedReviewOption.value.value,
                    remarks: newRemarks.value,
                },
            }
        },
        auto: true,
        onSuccess() {
            in_review_edit.value = false
            reviewData.fetch()
        },
        onError(error) {
            errors.value = 'Failed to update review'
        },
    })
}

const submitReview = () => {
    createResource({
        url: 'fossunited.api.reviewer.submit_review',
        makeParams(){
            return {
                submission_id: route.params.talk_id,
                to_approve: selectedReviewOption.value.value,
                remarks: newRemarks.value,
            }
        },
        auto: true,
        onSuccess() {
            in_review_edit.value = false
            hasReviewed.fetch()
        },
    })
}
</script>
