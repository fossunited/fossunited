<template>
  <div class="flex flex-col gap-8 w-full p-4 md:p-8 border rounded bg-white">
    <h4 v-if="showTitle" class="flex gap-2 items-center font-semibold">
      <span>Actions</span>
    </h4>
    <Button theme="green" @click="confirmWithdrawal = true"
      v-if="submission.doc.is_withdrawn == true">
      Un-Withdraw CFP
    </Button>
    <Button theme="red" @click="confirmWithdrawal = true"
      v-if="submission.doc.is_withdrawn == false">
      Withdraw CFP
    </Button>
    <Dialog
      v-model="confirmWithdrawal"
      class="z-50"
      :options="{
        title: 'Withdraw CFP',
        message: `Are you sure you want to change withdrawal status of this CFP?`,
        icon: {
          name: 'alert-triangle',
          appearance: 'warning',
        },
        actions: [
          {
            label: 'Cancel',
            onClick: () => (confirmWithdrawal.value = false),
          },
          {
            label: 'Change Withdrawal Status',
            theme: 'red',
            onClick: () => (toggleWithdrawCFP()),
          },
        ],
      }"
    />
  </div>
</template>
<script setup>
import RenderField from '@/components/form/RenderField.vue'
import ReferencesComponent from '@/components/cfp-public/ReferencesComponent.vue'
import { toast } from 'vue-sonner'
import { ref } from 'vue'
import { Button, Dialog, createDocumentResource } from 'frappe-ui'

const cfpid = defineModel('cfpid', {
  type: String,
  required: true,
})

const props = defineProps({
  showTitle: {
    type: Boolean,
    default: true,
  },
  cfpid: {
    type: String,
  },
})

const confirmWithdrawal = ref(false)

const submission = createDocumentResource({
  doctype: 'FOSS Event CFP Submission',
  name: cfpid.value,
  fields: ['*'],
})

const toggleWithdrawCFP = () => {
  submission.setValue
    .submit({
      is_withdrawn: !submission.doc.is_withdrawn
    })
    .then(() => {
      toast.success('Proposal Withdrawal Status Changed!')
    })
    .catch((err) => {
      toast.error(err)
    })
  confirmWithdrawal.value = false
}

</script>
