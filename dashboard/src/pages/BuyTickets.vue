<template>
  <RazorpayCheckout ref="rzpCheckout" />

  <Card
    v-if="event.data"
    :title="`Buy Tickets for ${event.data.event_name}`"
    class="m-4"
  >
    <RadioGroup class="p-2" v-model="checkoutInfo.tier">
      <RadioGroupLabel class="text-base font-semibold leading-6 text-gray-900"
        >Select a tier</RadioGroupLabel
      >

      <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-3 sm:gap-x-4">
        <RadioGroupOption
          as="template"
          v-for="tier in ticketTiers"
          :key="tier.name"
          :value="tier"
          v-slot="{ active, checked }"
        >
          <div
            :class="[
              checked
                ? 'border-gray-600 ring-2 ring-gray-600'
                : 'border-gray-300',
              'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none',
            ]"
          >
            <span class="flex flex-1">
              <span class="flex flex-col">
                <RadioGroupLabel
                  as="span"
                  class="block text-sm font-medium text-gray-900"
                  >{{ tier.title }}</RadioGroupLabel
                >
                <RadioGroupDescription
                  as="span"
                  class="mt-1 flex items-center text-sm text-gray-500"
                  >{{ tier.description }}</RadioGroupDescription
                >
                <RadioGroupDescription
                  as="span"
                  class="mt-6 text-sm font-medium text-gray-900"
                  >{{ tier.price }}</RadioGroupDescription
                >
              </span>
            </span>
            <FeatherIcon
              name="check-circle"
              :class="[!checked ? 'invisible' : '', 'h-5 w-5 text-gray-700']"
              aria-hidden="true"
            />
            <span
              :class="[
                active ? 'border' : 'border-2',
                checked ? 'border-indigo-600' : 'border-transparent',
                'pointer-events-none absolute -inset-px rounded-lg',
              ]"
              aria-hidden="true"
            />
          </div>
        </RadioGroupOption>
      </div>
    </RadioGroup>

    <div class="max-w-lg m-2 flex flex-col gap-2">
      <FormControl
        type="select"
        :options="[
          {
            label: '1',
            value: 1,
          },
          {
            label: '2',
            value: 2,
          },
          {
            label: '3',
            value: 3,
          },
        ]"
        size="sm"
        variant="subtle"
        :disabled="false"
        label="Number of seats"
        v-model="checkoutInfo.numSeats"
      />

      <FormControl
        type="email"
        size="sm"
        variant="subtle"
        placeholder="john@fossunited.org"
        :disabled="false"
        label="Email"
        v-model="checkoutInfo.email"
      />

      <h2 class="text-base font-semibold text-gray-800 mt-4">
        Payment Summary
      </h2>
      <p>Total Amount: ₹{{ totalAmount }} ({{ checkoutInfo.numSeats }} x ₹{{ checkoutInfo.tier.price }})</p>
    </div>

    <Button
      class="m-2"
      :loading="rzpCheckout?.resource.loading"
      @click="createOrder"
      variant="solid"
      >Pay Now</Button
    >
  </Card>

  <div class="m-4">
    <Button
      v-if="Boolean(event.loading)"
      :loading="true"
      loading-text="Loading"
    />
    <p v-else-if="!eventName" class="text-gray-800 font-medium">
      Event not found
    </p>
    <p v-else-if="event.error">Error loading event</p>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import {
  createResource,
  FeatherIcon,
  FormControl,
  Button,
  Card
} from 'frappe-ui'
import {
  RadioGroup,
  RadioGroupDescription,
  RadioGroupLabel,
  RadioGroupOption,
} from '@headlessui/vue'

import RazorpayCheckout from '../components/common/RazorpayCheckout.vue'

const eventName = ref(null)
const checkoutInfo = reactive({
  tier: null,
  numSeats: 1,
  email: '',
  attendees: [
    {
      full_name: 'Hussain Nagaria',
      email: 'hussain@bwh.live',
    },
    {
      full_name: 'Harsh Tandya',
      email: 'harsh@fossunited.org',
    },
  ],
})

const rzpCheckout = ref(null)

const event = createResource({
  url: 'fossunited.api.dashboard.get_event',
  makeParams() {
    return {
      name: eventName.value,
    }
  },
  onSuccess(data) {
    const tiers = data.tiers
    if (tiers.length > 0) {
      checkoutInfo.tier = tiers[0]
    }
  },
})

function createOrder() {
  rzpCheckout.value.createOrder(
    totalAmount.value,
    checkoutInfo.email,
    {
      event: eventName.value,
      tier: checkoutInfo.tier,
      num_seats: checkoutInfo.numSeats,
      attendees: checkoutInfo.attendees,
    },
    event.data.doctype,
    event.data.name,
  )
}

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('event')) {
    eventName.value = params.get('event')
    event.fetch()
  }
})

const totalAmount = computed(() => {
  return checkoutInfo.tier?.price * checkoutInfo.numSeats
})

const ticketTiers = computed(() => {
  return event.data?.tiers || []
})
</script>
