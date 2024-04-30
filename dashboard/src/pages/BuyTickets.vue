<template>
  <RazorpayCheckout ref="rzpCheckout" />

  <Card
    v-if="event.data"
    :title="`Buy Tickets for ${event.data.event_name}`"
    class="m-4 mx-auto w-full sm:w-fit"
  >
    <RadioGroup class="p-2" v-model="checkoutInfo.tier">
      <RadioGroupLabel class="text-base font-semibold leading-6 text-gray-900"
        >Select a tier</RadioGroupLabel
      >

      <div
        class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-3 sm:gap-x-4 md:min-w-[48rem]"
      >
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
              'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none min-w-36',
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
                  >₹{{ tier.price }}</RadioGroupDescription
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

    <!-- Form -->
    <div class="max-w-lg m-2 mt-4 flex flex-col gap-2">
      <div class="grid sm:grid-cols-2 gap-2">
        <FormControl
          type="select"
          :options="seatOptions"
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
      </div>

      <h2 class="text-base font-semibold text-gray-800 mt-4">Attendees</h2>
      <div>
        <div v-for="(attendee, index) in checkoutInfo.attendees" :key="index">
          <p class="text-base text-gray-600 font-medium mt-3 mb-1">
            #{{ index + 1 }}
          </p>
          <div class="sm:flex gap-2 space-y-2 sm:space-y-0">
            <FormControl
              type="text"
              size="sm"
              variant="subtle"
              :placeholder="attendee.placeholder"
              label="Full Name"
              v-model="attendee.full_name"
            />

            <FormControl
              type="email"
              size="sm"
              variant="subtle"
              v-model="attendee.email"
              label="Email"
            />
          </div>
        </div>
      </div>

      <h2 class="text-base font-semibold text-gray-800 mt-4">
        Payment Summary
      </h2>
      <p>
        Total Amount: ₹{{ totalAmount }} ({{ checkoutInfo.numSeats }} x ₹{{
          checkoutInfo.tier.price
        }})
      </p>
    </div>

    <ErrorMessage
      class="m-2 mt-5"
      v-if="errorMessage"
      :message="errorMessage"
    />

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
import { computed, reactive, ref, onMounted, watch, inject } from 'vue'
import {
  createResource,
  FeatherIcon,
  FormControl,
  Button,
  Card,
  ErrorMessage,
} from 'frappe-ui'
import {
  RadioGroup,
  RadioGroupDescription,
  RadioGroupLabel,
  RadioGroupOption,
} from '@headlessui/vue'

import RazorpayCheckout from '../components/common/RazorpayCheckout.vue'

const dayjs = inject('$dayjs')

const MAX_SEATS_PER_BOOKING = 10

const eventName = ref(null)
const checkoutInfo = reactive({
  tier: null,
  numSeats: 1,
  email: '',
  attendees: [],
})
const errorMessage = ref(null)

const fullNamePlaceholders = ['Jenny Smith', 'Jacob Doe', 'Jim Brown']

watch(
  () => checkoutInfo.numSeats,
  () => {
    if (checkoutInfo.attendees.length < checkoutInfo.numSeats) {
      // fill empty attendees for the seats

      for (
        let i = checkoutInfo.attendees.length;
        i < checkoutInfo.numSeats;
        i++
      ) {
        const randomPlaceholder =
          fullNamePlaceholders[
            Math.floor(Math.random() * fullNamePlaceholders.length)
          ]

        checkoutInfo.attendees.push({
          full_name: '',
          email: '',
          placeholder: randomPlaceholder,
        })
      }
    } else if (checkoutInfo.attendees.length > checkoutInfo.numSeats) {
      // remove extra attendees
      checkoutInfo.attendees = checkoutInfo.attendees.slice(
        0,
        checkoutInfo.numSeats,
      )
    }
  },
  { immediate: true },
)

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
  if (checkoutFormErrors.value.length > 0) {
    errorMessage.value = checkoutFormErrors.value.join(', ')
    return
  } else {
    errorMessage.value = null
  }

  // start checkout
  rzpCheckout.value.createOrder(
    totalAmount.value,
    checkoutInfo.email,
    {
      event: eventName.value,
      tier: checkoutInfo.tier,
      attendees: checkoutInfo.attendees,
      num_seats: checkoutInfo.numSeats,
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
  let tiers = event.data?.tiers || []
  tiers = tiers.filter((tier) => {
    const isEnabled = Boolean(tier.enabled)
    const deadlinePassed =
      tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
    return isEnabled && !deadlinePassed
  })
  return tiers
})

const seatOptions = computed(() => {
  return Array.from({ length: MAX_SEATS_PER_BOOKING }, (_, i) => i + 1).map(
    (i) => ({
      label: i.toString(),
      value: i,
    }),
  )
})

const checkoutFormErrors = computed(() => {
  const errors = []
  if (!checkoutInfo.email) {
    errors.push('Please enter your email')
  }
  if (checkoutInfo.attendees.some((a) => !a.full_name || !a.email)) {
    errors.push('Please fill in all attendee details')
  }
  return errors
})
</script>
