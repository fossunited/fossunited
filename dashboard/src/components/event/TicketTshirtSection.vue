<template>
  <div>
    <div class="prose w-full">
      <h2 class="mb-1">Manage T-Shirts</h2>
      <p class="text-sm">You can manage the t-shirts for this event here.</p>
    </div>
    <div class="w-full md:w-1/3 mt-4 flex gap-2 flex-col rounded border p-4">
      <div class="flex justify-between items-center">
        <div class="text-base font-semibold mb-1">
          T-Shirts add-on is
          <span
            :class="
              event.data.paid_tshirts_available
                ? 'text-green-600'
                : 'text-gray-600'
            "
            >{{
              event.data.paid_tshirts_available ? 'Available' : 'Unavailable'
            }}</span
          >
        </div>
        <div class="space-x-2">
          <Button
            class="w-fit mt-2"
            :label="
              event.data.paid_tshirts_available ? 'Deactivate' : 'Activate'
            "
            :theme="event.data.paid_tshirts_available ? 'red' : 'gray'"
            @click="toggleTshirtStatus.fetch()"
          />
        </div>
      </div>
      <div class="mt-6 flex flex-col gap-1">
        <div class="flex gap-2" v-if="inPriceEdit">
          <Input
            class="w-1/3"
            v-model="newTshirtPrice"
            inputClasses="text-2xl"
            placeholder="0.00"
          >
          </Input>
          <Button icon="x" @click="inPriceEdit = false" />
          <Button icon="check" theme="green" @click="handleTshirtPriceUpdate" />
        </div>
        <div v-else class="prose flex items-center gap-2">
          <h3 class="font-medium mb-0">
            {{ event.data.t_shirt_price }} <span class="text-lg">INR</span>
          </h3>
          <Button icon="edit" @click="inPriceEdit = true" />
        </div>
      </div>
      <ErrorMessage :message="errorMessages" />
    </div>
  </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import { createResource, ErrorMessage } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import Input from '@/components/Input.vue'

const props = defineProps({
  event: {
    type: Object,
    default: null,
  },
})

const inPriceEdit = ref(false)
const newTshirtPrice = ref(props.event.data.t_shirt_price)
const route = useRoute()

const toggleTshirtStatus = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fieldname: 'paid_tshirts_available',
      value: !props.event.data.paid_tshirts_available,
    }
  },
  onSuccess() {
    props.event.fetch()
  },
})

const errorMessages = ref('')
const tshirtPriceUpdateErrors = () => {
  const errors = []

  if (!newTshirtPrice.value) {
    errors.push('Price cannot be empty')
  }
  if (isNaN(newTshirtPrice.value)) {
    errors.push('Price should be a number')
  }
  if (Number(newTshirtPrice.value) <= 0) {
    errors.push('Price should be greater than 0')
  }

  return errors
}

const updateTshirtPrice = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter Event',
      name: route.params.id,
      fieldname: 't_shirt_price',
      value: newTshirtPrice.value,
    }
  },
  onSuccess() {
    props.event.fetch()
    toast.success('T-shirt price updated successfully')
    inPriceEdit.value = false
  },
})

const handleTshirtPriceUpdate = () => {
  const errors = tshirtPriceUpdateErrors()
  if (errors.length) {
    errorMessages.value = errors.join(', ')
    return
  }
  errorMessages.value = ''

  updateTshirtPrice.fetch()
}
</script>
