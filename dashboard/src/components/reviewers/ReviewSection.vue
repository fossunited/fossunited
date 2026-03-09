<template>
  <div class="flex flex-col gap-4">
    <ReviewStatsComponent :reviews="submission.data.reviews" />

    <MessageBanner
      v-if="!hasReviewed"
      variant="warning"
      message="You have not reviewed this submission yet!"
    >
      <template #prefix>
        <IconAlertTriangle class="w-4 h-4" />
      </template>
    </MessageBanner>
    <MessageBanner v-else variant="info" message="You have already reviewed this submission!">
      <template #prefix>
        <IconChecks class="w-4 h-4" />
      </template>
    </MessageBanner>

    <ReviewCommentBox
      v-if="!hasReviewed || inEdit"
      :in-edit="inEdit"
      :review="selectedReview"
      :submission-id="submission.data.name"
      @add:review="handleAddReview()"
      @update:review="handleUpdateReview()"
    />

    <!-- Review List -->
    <div class="flex flex-col">
      <div
        v-for="(review, index) in sortedReviews"
        :key="review.name"
        class="flex flex-col gap-1 my-2"
      >
        <div v-if="isReviewOwner(review)" class="p-4 border rounded flex flex-col gap-2">
          <h5 class="text-base font-semibold">Your Review</h5>
          <div class="flex justify-between items-center gap-4">
            <div
              v-if="review.remarks"
              class="prose prose-sm max-w-full"
              v-html="cleanedHTML(review.remarks)"
            ></div>
            <span v-else class="text-sm text-ink-gray-5">No Remarks</span>
            <div class="flex items-center gap-2">
              <Button label="Edit" @click="editReview(review)" />
              <Button icon="trash" theme="red" @click="deleteReview(review.name)" />
            </div>
          </div>
          <Badge
            class="w-fit"
            :label="getLabel(review.to_approve)"
            :theme="getTheme(review.to_approve)"
          />
        </div>
        <hr v-if="index != sortedReviews.length - 1" class="mt-2" />
      </div>
    </div>
  </div>
</template>
<script setup>
import { cleanedHTML } from '@/helpers/utils'
import { ref, inject, computed } from 'vue'
import { Badge, createResource } from 'frappe-ui'
import { IconChecks, IconAlertTriangle } from '@tabler/icons-vue'
import { toast } from 'vue-sonner'
import { defaultSelectedReviewValue } from '@/helpers/reviewer'
import MessageBanner from '@/components/ui/MessageBanner.vue'
import ReviewStatsComponent from './ReviewStatsComponent.vue'
import ReviewCommentBox from './ReviewCommentBox.vue'

const session = inject('$session')

const inEdit = ref(false)
const selectedReview = ref(defaultSelectedReviewValue())

const submission = inject('submission')

const sortedReviews = computed(() => {
  // if the session.user has reviewed, put that review item as the first in the list.
  return [
    ...submission.data.reviews.filter((review) => review.owner == session.user),
    ...submission.data.reviews.filter((review) => review.owner != session.user),
  ]
})

const isReviewOwner = (review) => {
  return review.owner == session.user
}

const hasReviewed = computed(() => {
  return submission.data.reviews.some((review) => review.owner == session.user)
})

const deleteReview = (reviewId) => {
  createResource({
    url: 'frappe.client.delete',
    makeParams() {
      return {
        doctype: 'FOSS Event CFP Review',
        name: reviewId,
      }
    },
    auto: true,
    onSuccess() {
      inEdit.value = false
      selectedReview.value = defaultSelectedReviewValue()

      submission.fetch()
    },
    onError(err) {
      toast.error('Failed to delete review', err.message)
    },
  })
}

const editReview = (review) => {
  inEdit.value = true
  selectedReview.value = review
}

const handleUpdateReview = () => {
  inEdit.value = false
  selectedReview.value = defaultSelectedReviewValue()
  submission.fetch()
}

const handleAddReview = () => {
  selectedReview.value = defaultSelectedReviewValue()
  submission.fetch()
}

const getLabel = (status) => {
  switch (status) {
    case 'Maybe':
      return 'Maybe'
    case 'Yes':
      return 'Approved'
    case 'No':
      return 'Rejected'
    default:
      return status
  }
}

const getTheme = (status) => {
  switch (status) {
    case 'Maybe':
      return 'orange'
    case 'Yes':
      return 'green'
    case 'No':
      return 'red'
    default:
      return 'gray'
  }
}
</script>
