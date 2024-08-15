<template>
  <ManageTicketTierDialog
    v-model="showDialog"
    :tier="tier"
    @update-tier="updateTier"
  />
  <div class="rounded border p-4">
    <div class="flex w-full justify-between items-center">
      <div class="flex flex-wrap items-center">
        <div class="prose">
          <h3 class="uppercase">{{ tier.title }}</h3>
        </div>
        <Badge :theme="tier.enabled ? 'green' : 'gray'" class="ml-2">
          {{ tier.enabled ? 'Active' : 'Inactive' }}
        </Badge>
      </div>
      <Button label="Manage" @click="manageTicketTier" />
    </div>
    <div class="mt-6 flex flex-col gap-1">
      <div class="prose">
        <h3 class="font-medium">
          {{ tier.price }} <span class="text-lg">{{ tier.currency }}</span>
        </h3>
      </div>
      <div class="text-xs text-gray-600" v-if="tier.valid_till">
        Closes: {{ new Date(tier.valid_till).toDateString() }}
      </div>
      <div class="text-xs text-gray-600" v-if="tier.maximum_tickets">
        Max Tickets: {{ tier.maximum_tickets }}
      </div>
    </div>
  </div>
</template>
<script setup>
import { toast } from 'vue-sonner'
import { Badge } from 'frappe-ui'
import { defineProps, defineEmits, ref } from 'vue'
import ManageTicketTierDialog from '@/components/event/ManageTicketTierDialog.vue'

const showDialog = ref(false)

const props = defineProps({
  tier: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update-tier'])

const updateTier = () => {
  toast.success('Ticket tier updated successfully')
  emit('update-tier')
}

const manageTicketTier = () => {
  showDialog.value = true
}
</script>
