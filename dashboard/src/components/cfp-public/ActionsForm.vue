<template>
  <Dialog
    v-model="showConfirmDialog"
    class="z-50"
    :options="{
      title: 'Confirm Action',
      message: `Are you sure you want to ${submission.doc.is_withdrawn ? 'un-withdraw' : 'withdraw'} the CFP?`,
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'Confirm',
          variant: 'solid',
          onClick: () => toggleWithdrawCFP(),
        },
        {
          label: 'Cancel',
          onClick: () => (showConfirmDialog = false),
        },
      ],
    }"
  />
  <div class="flex flex-col gap-8 w-full p-4 md:p-8 border rounded bg-white">
    <h4 class="flex gap-2 items-center font-semibold">
      <span>Actions</span>
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-if="!submission.doc.is_withdrawn"
        class="flex justify-between gap-4 border rounded p-4 border-red-400"
      >
        <div class="flex flex-col gap-2">
          <h5 class="font-semibold">Withdraw Proposal</h5>
          <p>
            The proposal will be removed from the list of CFP submissions and will not be
            considered for the event.
          </p>
        </div>
        <Button label="Withdraw" size="md" theme="red" @click="showConfirmDialog = true" />
      </div>
      <div v-else>
        <div class="flex justify-between gap-4 border rounded p-4">
          <div class="flex flex-col gap-2">
            <h5 class="font-semibold">
              The proposal is currently <span class="text-red-500">withdrawn</span>
            </h5>
            <p class="text-base text-gray-600">
              You can un-withdraw the proposal to make it visible to the reviewers.
            </p>
          </div>
          <Button label="Un-Withdraw" size="md" theme="green" @click="showConfirmDialog = true" />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { toast } from 'vue-sonner'
import { ref, inject } from 'vue'
import { Button, Dialog, createDocumentResource } from 'frappe-ui'

const cfpid = defineModel('cfpid', {
  type: String,
  required: true,
})

const showConfirmDialog = ref(false)

const submission = inject('submission')

const toggleWithdrawCFP = () => {
  submission.setValue
    .submit({
      is_withdrawn: !submission.doc.is_withdrawn,
    })
    .then(() => {
      toast.success('Proposal Withdrawal Status Changed!')
    })
    .catch((err) => {
      toast.error(err)
    })
  showConfirmDialog.value = false
}
</script>
