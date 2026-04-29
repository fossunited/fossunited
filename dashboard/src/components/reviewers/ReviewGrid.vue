<template>
  <div v-if="loading" class="flex justify-center p-8">
    <LoadingIndicator class="w-6 h-6" />
  </div>
  <div v-else-if="submissions.length === 0" class="flex justify-center p-8 text-ink-gray-5">
    No proposals found.
  </div>
  <div v-else class="overflow-x-auto border rounded bg-white w-full">
    <table class="w-full text-sm text-left">
      <thead class="bg-surface-gray-2 text-ink-gray-7 border-b">
        <tr>
          <th class="px-4 py-2 font-medium min-w-[200px]">Proposal</th>
          <th class="px-4 py-2 font-medium w-32">Status</th>
          <th class="px-4 py-2 font-medium w-32">Review</th>
          <th v-for="cat in categories" :key="cat.name" class="px-4 py-2 font-medium w-24">
            {{ cat.category_name }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="sub in submissions" :key="sub.name" class="border-b last:border-b-0 hover:bg-surface-gray-1">
          <td class="px-4 py-2 truncate max-w-[300px]" :title="sub.talk_title">
            <span class="font-medium">{{ sub.talk_title }}</span>
          </td>
          <td class="px-4 py-2">
            <Badge :label="sub.status" :theme="getStatusBadgeTheme(sub.status)" />
          </td>
          <td class="px-4 py-2">
            <select v-model="reviews[sub.name].to_approve" @change="saveReview(sub.name)" class="text-sm border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500">
              <option value="Yes">Approve</option>
              <option value="No">Reject</option>
              <option value="Maybe">Not Sure</option>
              <option value="Abstain">Abstain</option>
              <option value="">-</option>
            </select>
          </td>
          <td v-for="cat in categories" :key="cat.name" class="px-4 py-2">
            <input type="number" v-model="reviews[sub.name].scores[cat.name]" @blur="saveReview(sub.name)" class="w-16 px-2 py-1 text-sm border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { ref, watch, inject } from 'vue'
import { createResource, LoadingIndicator, Badge } from 'frappe-ui'
import { getStatusBadgeTheme } from '@/helpers/reviewer'
import { toast } from 'vue-sonner'

const props = defineProps({
  event: { type: String, required: true }
})

const loading = ref(true)
const submissions = ref([])
const categories = ref([])
const reviews = ref({})
const session = inject('$session')

const fetchData = createResource({
  url: 'fossunited.api.reviewer.get_bulk_review_data',
  makeParams: () => ({ event: props.event }),
  onSuccess(data) {
    submissions.value = data.submissions
    categories.value = data.categories
    
    const reviewsMap = {}
    data.submissions.forEach(sub => {
      const existing = data.reviews.find(r => r.proposal === sub.name)
      if (existing) {
        const scoresMap = {}
        if (existing.scores) {
          existing.scores.forEach(s => { scoresMap[s.category] = s.score })
        }
        reviewsMap[sub.name] = {
          name: existing.name,
          to_approve: existing.to_approve,
          scores: scoresMap
        }
      } else {
        reviewsMap[sub.name] = { to_approve: '', scores: {} }
      }
    })
    reviews.value = reviewsMap
    loading.value = false
  }
})

watch(() => props.event, () => {
  if (props.event) {
    loading.value = true
    fetchData.fetch()
  }
}, { immediate: true })

const saveReview = (proposalId) => {
  const reviewData = reviews.value[proposalId]
  if (!reviewData.to_approve) return
  
  const payload = {
    proposal: proposalId,
    to_approve: reviewData.to_approve,
    scores: Object.keys(reviewData.scores).map(cat => ({ category: cat, score: reviewData.scores[cat] }))
  }
  
  if (reviewData.name) {
    createResource({
      url: 'frappe.client.set_value',
      makeParams: () => ({
        doctype: 'FOSS Event CFP Review',
        name: reviewData.name,
        fieldname: payload
      }),
      auto: true,
      onSuccess() { toast.success('Saved review for ' + proposalId) },
      onError(err) { toast.error(err.message) }
    })
  } else {
    createResource({
      url: 'frappe.client.insert',
      makeParams: () => ({
        doc: {
          doctype: 'FOSS Event CFP Review',
          ...payload
        }
      }),
      auto: true,
      onSuccess(data) {
        reviewData.name = data.name
        toast.success('Saved review for ' + proposalId)
      },
      onError(err) { toast.error(err.message) }
    })
  }
}
</script>
