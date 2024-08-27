<template>
<RazorpayCheckout ref="rzpCheckout" />
<Header/>
<Dialog
  v-model="showDialog"
  class="z-50"
  :options="{
    title: 'Tickets are closed!',
    message: dialogError,
  }"
></Dialog>
<div
  v-if="event.data"
  class="bg-gray-50 mx-auto px-4 sm:px-6 lg:px-8 py-8"
>
  <div class="flex gap-2 mb-6 items-center">
    <a :href="redirectToEvent" class=" font-semibold text-base hover:underline">{{ event.data.event_name }}</a>
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4 ">
      <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
    </svg>
    <span class="text-base">Book Tickets</span>
  </div>
  <div class="flex gap-6">
    <div
      class="p-4 lg:px-8 md:py-8 border border-gray-300 rounded-md bg-white md:w-3/4"
    >
      <h1 class="text-[2rem] font-bold">
        Book Conference Tickets for {{ event.data.event_name }}
      </h1>
      <div class="my-2 text-gray-700 " v-html="markdown.render(event.data.ticket_form_description || '')" />
      <RadioGroup class="py-4" v-model="checkoutInfo.tier">
        <RadioGroupLabel
          class="text-lg font-semibold leading-6 text-gray-800"
        >
          Select a tier
        </RadioGroupLabel>
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
                  ? 'border-gray-800 ring-1 ring-gray-800'
                  : 'border-gray-300',
                'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none min-w-36',
              ]"
            >
              <span class="flex flex-1">
                <span class="flex flex-col justify-between">
                  <span class="flex flex-col gap-2">
                    <RadioGroupLabel
                      as="span"
                      class="block text-xl font-bold text-gray-900"
                      >{{ tier.title }}</RadioGroupLabel
                    >
                    <RadioGroupDescription
                      as="span"
                      class="mt-2 text-sm text-gray-500"
                      v-html="markdown.render(tier.description || '')"
                    >
                    </RadioGroupDescription>
                  </span>
                  <span class="flex flex-col gap-4 mt-4">
                    <Badge
                      class="w-fit"
                      variant="outline"
                      theme="green"
                      v-if="tier.valid_till"
                      >Available till
                      {{ dayjs(tier.valid_till).format('MMM D, YYYY') }}</Badge
                    >
                    <RadioGroupDescription
                      as="span"
                      class="text-xl font-medium text-gray-900"
                      >₹{{ tier.price }}</RadioGroupDescription
                    >
                  </span>
                </span>
              </span>
              <svg
              :class="[!checked ? 'invisible' : '', 'h-6 w-6 text-gray-800']"
              xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"
              >
                <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12Zm13.36-1.814a.75.75 0 1 0-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 0 0-1.06 1.06l2.25 2.25a.75.75 0 0 0 1.14-.094l3.75-5.25Z" clip-rule="evenodd" />
              </svg>
              <span
                :class="[
                  active ? 'border' : 'border-2',
                  checked ? 'border-gray-800' : 'border-transparent',
                  'pointer-events-none absolute -inset-px rounded-lg',
                ]"
                aria-hidden="true"
              />
            </div>
          </RadioGroupOption>
        </div>
      </RadioGroup>

      <div>
        <div class="flex flex-col gap-1">
          <span class="text-lg font-semibold leading-6 text-gray-800">No. of Tickets</span>
          <FormControl
            class="w-1/4"
            type="select"
            :options="seatOptions"
            size="md"
            variant="subtle"
            v-model="checkoutInfo.numSeats"
          />
        </div>

        <div v-if="event.data.custom_fields.length > 0">
          <h2 class="text-base font-semibold text-gray-800 mt-4">Additional Details</h2>
          <div class="mt-3 sm:grid sm:grid-cols-2 gap-2 space-y-2 sm:space-y-0">
            <FormControl
              v-for="field in event.data.custom_fields"
              :type="FIELD_TYPE_FORM_CONTROL_MAP[field.field_type]"
              :label="field.label"
              :options="field.options"
              size="sm"
              variant="subtle"
              v-model="customFields[field.field_name]"
             />
          </div>
        </div>

        <!-- ATTENDEE DETAILS -->
        <h2 class="text-lg font-semibold leading-6 text-gray-800 mt-4">Attendees</h2>
        <div>
          <div v-for="(attendee, index) in checkoutInfo.attendees" :key="index" class="px-4 py-4 my-4 border rounded-sm">
            <p class="text-base text-gray-600 font-medium mb-1">
              #{{ index + 1 }}
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-2 gap-y-4">
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
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                v-model="attendee.organization"
                label="Organization / College"
              />
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                v-model="attendee.designation"
                label="Designation"
              />
            </div>
            <div
              v-if="event.data.paid_tshirts_available"
              class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2"
            >
              <FormControl
                type="checkbox"
                size="sm"
                variant="subtle"
                label="Add a T-shirt?"
                v-model="attendee.wants_tshirt"
              />
              <FormControl
                :class="attendee.wants_tshirt ? '' : ' invisible'"
                type="select"
                :options="T_SHIRT_SIZES"
                size="sm"
                class="min-w-[100px]"
                variant="subtle"
                label="Size"
                v-model="attendee.tshirt_size"
              />
            </div>
          </div>
        </div>

        <div class="border rounded-md p-5 my-4 flex flex-col gap-4">
          <h4 class="text-base font-semibold">Billing Details</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="John Doe"
            label="Name"
            v-model="checkoutInfo.buyer_name"
            />
            <FormControl
              type="email"
              size="sm"
              variant="subtle"
              placeholder="john@fossunited.org"
              label="Email"
              v-model="checkoutInfo.email"
            />
            <FormControl
                type="select"
                size="sm"
                variant="subtle"
                label="State"
                :options="stateOptions.data"
                v-model="checkoutInfo.state"
                :placeholder="stateOptions.data[0]?.label"
            />
          </div>
          <div class="my-2">
            <Switch
              class="w-fit"
              label="Enter GST Details"
              description="Invoice will be generated with GST details."
              v-model="checkoutInfo.hasGST"
            />
          </div>
          <div v-if="checkoutInfo.hasGST" class="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div class="flex flex-col gap-2">
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                label="Company Name"
                v-model="checkoutInfo.company_name"
              />
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                label="GSTN (optional)"
                v-model="checkoutInfo.gstn"
              />
            </div>
            <FormControl
              type="textarea"
              size="sm"
              variant="subtle"
              label="Billing Address"
              v-model="checkoutInfo.billing_address"
            />
          </div>
        </div>

      </div>
    </div>

    <Card
      class="w-1/4 h-fit sticky top-20 hidden md:block"
      title="Ticket Summary"
    >
      <div class="w-full mt-2 space-y-1">
          <div class="grid grid-cols-3 gap-2">
            <p>{{ checkoutInfo.tier.title }} Ticket</p>
            <p class="justify-self-center">₹{{ checkoutInfo.tier.price }} x {{ checkoutInfo.numSeats }}</p>
            <p class="justify-self-end">₹{{ checkoutInfo.tier.price * checkoutInfo.numSeats }}</p>
          </div>

          <div
            v-if="event.data.paid_tshirts_available && numTShirtAdded > 0"
            class="grid grid-cols-3"
          >
            <p>T-Shirts</p>
            <p class="justify-self-center">
              ₹{{ event.data.t_shirt_price }} x
              {{ numTShirtAdded }}
            </p>
            <p class="justify-self-end">₹{{ numTShirtAdded * event.data.t_shirt_price }}</p>
          </div>
      </div>
      <hr class="my-2">
      <div class="grid grid-cols-3 gap-2 font-semibold">
        <p>Total</p>
        <p class="justify-self-center"></p>
        <p class="justify-self-end">₹{{ totalAmount }}</p>
      </div>

      <ErrorMessage
        class="m-2 mt-5"
        v-if="errorMessage"
        :message="errorMessage"
      />
      <Button
        class="mt-4 w-full"
        size="md"
        :loading="rzpCheckout?.resource.loading"
        @click="createOrder"
        variant="solid"
      >
      Pay Now
      </Button>
    </Card>
  </div>
</div>
<div class="p-5 bg-gray-50">
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
<div v-if="event.data" class="md:hidden sticky bottom-0 z-50 pb-8 h-fit bg-white rounded-t-lg border-gray-800 px-5 py-3 border">
  <div class="mb-4 flex justify-between items-center">
    <h3 class="text-lg font-medium ">Ticket Summary</h3>
    <Button
      size="sm"
      variant="ghost"
      @click="showAdditionalDetails = !showAdditionalDetails"
      label="Show Details"
    />
  </div>
  <div v-if="showAdditionalDetails" class="w-full mt-2 space-y-1">
    <div class="grid grid-cols-3 gap-2">
      <p>{{ checkoutInfo.tier.title }} Ticket</p>
      <p class="justify-self-center">₹{{ checkoutInfo.tier.price }} x {{ checkoutInfo.numSeats }}</p>
      <p class="justify-self-end">₹{{ checkoutInfo.tier.price * checkoutInfo.numSeats }}</p>
    </div>
    <div
      v-if="event.data.paid_tshirts_available && numTShirtAdded > 0"
      class="grid grid-cols-3"
    >
      <p>T-Shirts</p>
      <p class="justify-self-center">
        ₹{{ event.data.t_shirt_price }} x
        {{ numTShirtAdded }}
      </p>
      <p class="justify-self-end">₹{{ numTShirtAdded * event.data.t_shirt_price }}</p>
    </div>
    <hr class="my-2">
  </div>
  <ErrorMessage
      class="m-2 mt-5"
      v-if="errorMessage"
      :message="errorMessage"
    />
  <div class="grid grid-cols-3 gap-2 mt-2 font-semibold">
      <p>Total</p>
      <p class="justify-self-center"></p>
      <p class="justify-self-end">₹{{ totalAmount }}</p>
  </div>
  <Button
      class="mt-4 w-full"
      size="md"
      :loading="rzpCheckout?.resource.loading"
      @click="createOrder"
      variant="solid"
    >
    Pay Now
  </Button>
</div>

</template>

<script setup>
import MarkdownIt from "markdown-it";
import Header from '@/components/Header.vue'
import { computed, reactive, ref, onMounted, watch, inject } from 'vue'
import {
  createResource,
  FormControl,
  Switch,
  Button,
  Card,
  usePageMeta,
  ErrorMessage,
  Badge,
  Dialog,
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
const T_SHIRT_SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL']
const FIELD_TYPE_FORM_CONTROL_MAP = {
  "Data": "text",
  "Int": "number",
  "Select": "select"
}

usePageMeta(() => {
  return {
    title: 'Book Tickets',
  }
})

const showAdditionalDetails = ref(false)
const markdown = new MarkdownIt()

const eventName = ref(null)
const checkoutInfo = reactive({
  tier: null,
  numSeats: 1,
  email: '',
  attendees: [],
  hasGST: false,
  company_name: '',
  buyer_name: '',
  state: '',
  gstn: '',
  billing_address: '',
})
const customFields = reactive({});
const errorMessage = ref(null)

const fullNamePlaceholders = ['Jenny Smith', 'Jacob Doe', 'Jim Brown']

const stateOptions = createResource({
  url: 'fossunited.api.dashboard.get_states',
  transform(data){
    return data.map(state => ({ label: state.name, value: state.name }))
  },
  auto: true,
})

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
          designation: '',
          organization: '',
          wants_tshirt: false,
          tshirt_size: 'M',
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
    resetCustomFields();
  },
})

const redirectToEvent = computed(() => {
  if(event.data){
    return `${window.location.origin}/${event.data.route}`
  }
})

function resetCustomFields() {
  for (let field of event.data?.custom_fields) {
    customFields[field.field_name] = "";
    if (field.field_type == "Select") {
      field.options = field.options.split("\n");
    }
  }
}

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
      custom_fields: customFields
    },
    event.data.doctype,
    event.data.name,
    {
      buyer_name: checkoutInfo.buyer_name,
      company_name: checkoutInfo.company_name,
      gstn: checkoutInfo.gstn,
      state: checkoutInfo.state,
      billing_address: checkoutInfo.billing_address,
    },
  )
}

const showDialog = ref(false)
const dialogError = ref('')

const checkIfTicketsLive = createResource({
  url: 'fossunited.api.tickets.is_ticket_live',
  makeParams() {
    return {
      event_id: eventName.value,
    }
  },
  onSuccess(data) {
    if (!data) {
      dialogError.value = 'Tickets are not live for this event'
      showDialog.value = true
      return
    }
    event.fetch()
  },
  onError() {
    errorMessage.value = 'Error checking ticket status'
  },
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('event')) {
    eventName.value = params.get('event')
    checkIfTicketsLive.fetch()
  }
})

const totalAmount = computed(() => {
  let total = checkoutInfo.tier?.price * checkoutInfo.numSeats

  if (event.data.paid_tshirts_available) {
    total += numTShirtAdded.value * event.data.t_shirt_price
  }

  return total
})

const numTShirtAdded = computed(() => {
  let tShirts = 0

  for (let attendee of checkoutInfo.attendees) {
    if (attendee.wants_tshirt) {
      tShirts += 1
    }
  }

  return tShirts
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

  // validate email address
  if (
    checkoutInfo.email &&
    !checkoutInfo.email.match(
      /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    )
  ) {
    errors.push('Please enter a valid email address')
  }

  if (checkoutInfo.attendees.some((a) => !a.full_name || !a.email)) {
    errors.push('Please fill in all attendee details')
  }

  // check mandatory custom fields
  for (let field of event.data?.custom_fields || []) {
    if (field.mandatory && !customFields[field.field_name]) {
      errors.push(`Please fill in ${field.label}`)
    }
  }

  for (let attendee of checkoutInfo.attendees) {
    if (attendee.email && !attendee.email.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
      errors.push('Please enter a valid email address for all attendees')
    }
  }

  if (!checkoutInfo.state) {
    errors.push('Please select a state in Billing Details')
  }

  if(!checkoutInfo.buyer_name) {
    errors.push('Please enter name in Billing Details')
  }

  return errors
})
</script>
