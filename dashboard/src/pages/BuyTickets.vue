<!-- eslint-disable vue/attribute-hyphenation -->
<template>
  <RazorpayCheckout ref="rzpCheckout" />
  <Header />
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Tickets are closed!',
      message: dialogError,
    }"
  ></Dialog>
  <div v-if="event.data" class="bg-gray-50 mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex gap-2 mb-6 items-center">
      <a :href="redirectToEvent" class="font-semibold text-base hover:underline">{{
        event.data.event_name
      }}</a>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        class="w-4 h-4"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
      </svg>
      <span class="text-base">Book Tickets</span>
    </div>
    <div class="flex gap-6">
      <div class="p-4 lg:px-8 md:py-8 border border-gray-300 rounded-md bg-white md:w-3/4">
        <h1 class="text-[2rem] font-bold">
          Book Conference Tickets for {{ event.data.event_name }}
        </h1>
        <div
          class="my-2 text-gray-700"
          v-html="markdown.render(event.data.ticket_form_description || '')"
        ></div>
        <RadioGroup v-model="checkoutInfo.tier" class="py-4">
          <RadioGroupLabel class="text-lg font-semibold leading-6 text-gray-800">
            Select a tier
          </RadioGroupLabel>
          <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-3 sm:gap-x-4 md:min-w-[48rem]">
            <!-- Active Tiers -->
            <RadioGroupOption
              v-for="tier in activeTiers"
              :key="tier.name"
              v-slot="{ active, checked }"
              as="template"
              :value="tier"
            >
              <div
                :class="[
                  checked ? 'border-gray-800 ring-1 ring-gray-800' : 'border-gray-300',
                  'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none min-w-36',
                ]"
              >
                <span class="flex flex-1">
                  <span class="flex flex-col justify-between">
                    <span class="flex flex-col gap-2">
                      <RadioGroupLabel as="span" class="block text-xl font-bold text-gray-900">{{
                        tier.title
                      }}</RadioGroupLabel>
                      <RadioGroupDescription
                        as="span"
                        class="mt-2 text-sm text-gray-500"
                        :innerHTML="markdown.render(tier.description || '')"
                      >
                      </RadioGroupDescription>
                    </span>
                    <span class="flex flex-col gap-4 mt-4">
                      <Badge v-if="tier.valid_till" class="w-fit" variant="outline" theme="green"
                        >Available till {{ dayjs(tier.valid_till).format('MMM D, YYYY') }}</Badge
                      >
                      <RadioGroupDescription as="span" class="text-xl font-medium text-gray-900"
                        >₹{{ tier.price }}</RadioGroupDescription
                      >
                    </span>
                  </span>
                </span>
                <IconCircleCheckFilled class="h-6 w-6" />
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

            <!-- Disabled/Expired Tiers -->
            <div
              v-for="tier in inactiveTiers"
              :key="tier.name"
              :class="[
                'relative flex rounded-lg border border-gray-200 bg-gray-50 p-4 shadow-sm min-w-36 opacity-60 cursor-not-allowed',
              ]"
            >
              <span class="flex flex-1">
                <span class="flex flex-col justify-between">
                  <span class="flex flex-col gap-2">
                    <span class="block text-xl font-bold text-gray-500">{{ tier.title }}</span>
                    <span
                      class="mt-2 text-sm text-gray-400"
                      v-html="markdown.render(tier.description || '')"
                    >
                    </span>
                  </span>
                  <span class="flex flex-col gap-4 mt-4">
                    <Badge v-if="!tier.enabled" class="w-fit" variant="outline" theme="red">
                      Disabled
                    </Badge>
                    <Badge
                      v-else-if="isTierExpired(tier)"
                      class="w-fit"
                      variant="outline"
                      theme="orange"
                    >
                      Expired on {{ dayjs(tier.valid_till).format('MMM D, YYYY') }}
                    </Badge>
                    <span class="text-xl font-medium text-gray-500">₹{{ tier.price }}</span>
                  </span>
                </span>
              </span>
              <IconTicketOff class="h-6 w-6 text-gray-600" />
            </div>
          </div>
        </RadioGroup>

        <div>
          <div class="flex flex-col gap-1">
            <span class="text-lg font-semibold leading-6 text-gray-800">No. of Tickets</span>
            <FormControl
              v-model="checkoutInfo.numSeats"
              class="w-1/4"
              type="select"
              :options="seatOptions"
              size="md"
              variant="subtle"
            />
          </div>

          <!-- custom fields section -->
          <div v-if="event.data.custom_fields.length > 0">
            <div class="flex-row mb-2">
              <h2 class="text-base font-semibold text-gray-800 mt-4">Additional Details</h2>
              <Switch
                v-model="customFieldsApplyToAll"
                class="w-fit text-xs"
                label="Apply Same answers for all tickets/attendees"
              />
            </div>

            <!-- global custom fields (when apply to all is enabled) -->
            <div
              v-if="customFieldsApplyToAll"
              class="mt-3 sm:grid sm:grid-cols-2 gap-2 space-y-2 sm:space-y-0"
            >
              <FormControl
                v-for="field in event.data.custom_fields"
                :key="field.name"
                v-model="globalCustomFields[field.field_name]"
                :type="FIELD_TYPE_FORM_CONTROL_MAP[field.field_type]"
                :label="field.label"
                :options="field.options"
                size="sm"
                variant="subtle"
              />
            </div>
          </div>

          <!-- attendee details -->
          <h2 class="text-lg font-semibold leading-6 text-gray-800 mt-4">Attendees</h2>
          <div>
            <div
              v-for="(attendee, index) in checkoutInfo.attendees"
              :key="index"
              class="px-4 py-4 my-4 border rounded-sm"
            >
              <p class="text-base text-gray-600 font-medium mb-1">#{{ index + 1 }}</p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-x-2 gap-y-4">
                <div class="flex flex-col gap-7">
                  <FormControl
                    v-model="attendee.full_name"
                    type="text"
                    size="sm"
                    variant="subtle"
                    :placeholder="attendee.placeholder"
                    label="Full Name"
                  />
                  <FormControl
                    v-model="attendee.organization"
                    type="text"
                    size="sm"
                    variant="subtle"
                    label="Organization / College"
                  />
                </div>
                <div class="flex flex-col gap-1">
                  <FormControl
                    v-model="attendee.email"
                    type="email"
                    size="sm"
                    variant="subtle"
                    label="Email"
                  />
                  <div class="pl-1">
                    <FormControl
                      v-model="attendee.subscribe_chapter_mailing"
                      class="text-sm"
                      type="checkbox"
                      size="sm"
                      variant="subtle"
                      :label="`Yes, I'd like to receive email updates about future events from ${event.data.event_name}.`"
                    />
                  </div>
                  <FormControl
                    v-model="attendee.designation"
                    type="text"
                    size="sm"
                    variant="subtle"
                    label="Designation"
                  />
                </div>
              </div>

              <!-- Per-Attendee custom fields (when apply to all is disabled) -->
              <div
                v-if="!customFieldsApplyToAll && event.data.custom_fields.length > 0"
                class="mt-4 border-t pt-4"
              >
                <h3 class="text-sm font-medium text-gray-700 mb-2">Additional Details</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-x-2 gap-y-4">
                  <FormControl
                    v-for="field in event.data.custom_fields"
                    :key="field.name"
                    v-model="attendee.custom_fields[field.field_name]"
                    :type="FIELD_TYPE_FORM_CONTROL_MAP[field.field_type]"
                    :label="field.label"
                    :options="field.options"
                    size="sm"
                    variant="subtle"
                  />
                </div>
              </div>

              <div
                v-if="event.data.paid_tshirts_available"
                class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2"
              >
                <FormControl
                  v-model="attendee.wants_tshirt"
                  type="checkbox"
                  size="sm"
                  variant="subtle"
                  label="Add a T-shirt?"
                />
                <FormControl
                  v-model="attendee.tshirt_size"
                  :class="attendee.wants_tshirt ? '' : ' invisible'"
                  type="select"
                  :options="T_SHIRT_SIZES"
                  size="sm"
                  class="min-w-[100px]"
                  variant="subtle"
                  label="Size"
                />
              </div>
            </div>
          </div>

          <div class="border rounded-md p-5 my-4 flex flex-col gap-4">
            <h4 class="text-base font-semibold">Billing Details</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <FormControl
                v-model="checkoutInfo.buyer_name"
                type="text"
                size="sm"
                variant="subtle"
                placeholder="John Doe"
                label="Name"
              />
              <FormControl
                v-model="checkoutInfo.email"
                type="email"
                size="sm"
                variant="subtle"
                placeholder="john@fossunited.org"
                label="Email"
              />
              <FormControl
                v-model="checkoutInfo.state"
                type="select"
                size="sm"
                variant="subtle"
                label="State"
                :options="stateOptions.data"
                :placeholder="stateOptions.data[0]?.label"
              />
            </div>
            <div class="my-2">
              <Switch
                v-model="checkoutInfo.hasGST"
                class="w-fit"
                label="Enter GST Details"
                description="Invoice will be generated with GST details."
              />
            </div>
            <div v-if="checkoutInfo.hasGST" class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div class="flex flex-col gap-2">
                <FormControl
                  v-model="checkoutInfo.company_name"
                  type="text"
                  size="sm"
                  variant="subtle"
                  label="Company Name"
                />
                <FormControl
                  v-model="checkoutInfo.gstn"
                  type="text"
                  size="sm"
                  variant="subtle"
                  label="GSTN (optional)"
                />
              </div>
              <FormControl
                v-model="checkoutInfo.billing_address"
                type="textarea"
                size="sm"
                variant="subtle"
                label="Billing Address"
              />
            </div>
            <div class="my-2">
              <Checkbox v-model="checkoutInfo.readRefundPolicy" size="sm"></Checkbox
              ><span class="font-medium leading-normal text-ink-gray-8 >text-base">
                I understand that tickets are non-refundable and have read the
                <a href="/refund-transfer-policy" class="font-semibold underline"
                  >Refund Policy</a
                ></span
              >
            </div>
          </div>
        </div>
      </div>

      <Card class="w-1/4 h-fit sticky top-20 hidden md:block" title="Ticket Summary">
        <div class="w-full mt-2 space-y-1">
          <div class="grid grid-cols-3 gap-2">
            <p>{{ checkoutInfo.tier.title }} Ticket</p>
            <p class="justify-self-center">
              ₹{{ checkoutInfo.tier.price }} x {{ checkoutInfo.numSeats }}
            </p>
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
        <hr class="my-2" />
        <div class="grid grid-cols-3 gap-2 font-semibold">
          <p>Total</p>
          <p class="justify-self-center"></p>
          <p class="justify-self-end">₹{{ totalAmount }}</p>
        </div>

        <ErrorMessage v-if="errorMessage" class="m-2 mt-5" :message="errorMessage" />
        <Button
          class="mt-4 w-full"
          size="md"
          :loading="rzpCheckout?.resource.loading"
          variant="solid"
          @click="createOrder"
        >
          Pay Now
        </Button>
      </Card>
    </div>
  </div>
  <div class="p-5 bg-gray-50">
    <Button v-if="Boolean(event.loading)" :loading="true" loading-text="Loading" />
    <p v-else-if="!eventName" class="text-gray-800 font-medium">Event not found</p>
    <p v-else-if="event.error">Error loading event</p>
  </div>
  <div
    v-if="event.data"
    class="md:hidden sticky bottom-0 z-50 pb-8 h-fit bg-white rounded-t-lg border-gray-800 px-5 py-3 border"
  >
    <div class="mb-4 flex justify-between items-center">
      <h3 class="text-lg font-medium">Ticket Summary</h3>
      <Button
        size="sm"
        variant="ghost"
        label="Show Details"
        @click="showAdditionalDetails = !showAdditionalDetails"
      />
    </div>
    <div v-if="showAdditionalDetails" class="w-full mt-2 space-y-1">
      <div class="grid grid-cols-3 gap-2">
        <p>{{ checkoutInfo.tier.title }} Ticket</p>
        <p class="justify-self-center">
          ₹{{ checkoutInfo.tier.price }} x {{ checkoutInfo.numSeats }}
        </p>
        <p class="justify-self-end">₹{{ checkoutInfo.tier.price * checkoutInfo.numSeats }}</p>
      </div>
      <div v-if="event.data.paid_tshirts_available && numTShirtAdded > 0" class="grid grid-cols-3">
        <p>T-Shirts</p>
        <p class="justify-self-center">
          ₹{{ event.data.t_shirt_price }} x
          {{ numTShirtAdded }}
        </p>
        <p class="justify-self-end">₹{{ numTShirtAdded * event.data.t_shirt_price }}</p>
      </div>
      <hr class="my-2" />
    </div>
    <ErrorMessage v-if="errorMessage" class="m-2 mt-5" :message="errorMessage" />
    <div class="grid grid-cols-3 gap-2 mt-2 font-semibold">
      <p>Total</p>
      <p class="justify-self-center"></p>
      <p class="justify-self-end">₹{{ totalAmount }}</p>
    </div>
    <Button
      class="mt-4 w-full"
      size="md"
      :loading="rzpCheckout?.resource.loading"
      variant="solid"
      @click="createOrder"
    >
      Pay Now
    </Button>
  </div>
</template>

<script setup>
import MarkdownIt from 'markdown-it'
import Header from '@/components/Header.vue'
import { computed, reactive, ref, onMounted, watch, inject } from 'vue'
import {
  createResource,
  FormControl,
  Switch,
  Checkbox,
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
import { IconCircleCheckFilled, IconTicketOff } from '@tabler/icons-vue'

const dayjs = inject('$dayjs')

const MAX_SEATS_PER_BOOKING = 10
const T_SHIRT_SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL']
const FIELD_TYPE_FORM_CONTROL_MAP = {
  Data: 'text',
  Int: 'number',
  Select: 'select',
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
  readRefundPolicy: false,
  company_name: '',
  buyer_name: '',
  state: '',
  gstn: '',
  billing_address: '',
})
const customFields = reactive({})
const errorMessage = ref(null)

const customFieldsApplyToAll = ref(false)
const globalCustomFields = reactive({})

const fullNamePlaceholders = ['Jenny Smith', 'Jacob Doe', 'Jim Brown']

const stateOptions = createResource({
  url: 'fossunited.api.dashboard.get_states',
  transform(data) {
    return data.map((state) => ({ label: state.name, value: state.name }))
  },
  auto: true,
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
    const activeTiersList = data.tiers.filter((tier) => {
      const isEnabled = Boolean(tier.enabled)
      const deadlinePassed = tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
      return isEnabled && !deadlinePassed
    })

    if (activeTiersList.length > 0) {
      checkoutInfo.tier = activeTiersList[0]
    }
    resetCustomFields()
  },
})

const redirectToEvent = computed(() => {
  if (event.data) {
    return `${window.location.origin}/${event.data.route}`
  }
  return window.location.origin
})

watch(
  () => checkoutInfo.numSeats,
  () => {
    if (checkoutInfo.attendees.length < checkoutInfo.numSeats) {
      for (let i = checkoutInfo.attendees.length; i < checkoutInfo.numSeats; i++) {
        const randomPlaceholder =
          fullNamePlaceholders[Math.floor(Math.random() * fullNamePlaceholders.length)]

        const newAttendee = {
          full_name: '',
          email: '',
          placeholder: randomPlaceholder,
          designation: '',
          subscribe_chapter_mailing: true,
          organization: '',
          wants_tshirt: false,
          tshirt_size: 'M',
          custom_fields: {},
        }

        // Initialize custom fields for new attendee if not applying to all
        if (!customFieldsApplyToAll.value && event.data?.custom_fields) {
          for (let field of event.data.custom_fields) {
            newAttendee.custom_fields[field.field_name] = ''
          }
        }

        checkoutInfo.attendees.push(newAttendee)
      }
    } else if (checkoutInfo.attendees.length > checkoutInfo.numSeats) {
      checkoutInfo.attendees = checkoutInfo.attendees.slice(0, checkoutInfo.numSeats)
    }
  },
  { immediate: true },
)

// Update the customFields initialization
function resetCustomFields() {
  if (event.data?.custom_fields) {
    // Reset global custom fields
    for (let field of event.data.custom_fields) {
      globalCustomFields[field.field_name] = ''
      if (field.field_type == 'Select') {
        field.options = field.options.split('\n')
      }
    }

    // Initialize custom fields for existing attendees if apply to all is disabled
    if (!customFieldsApplyToAll.value) {
      for (let attendee of checkoutInfo.attendees) {
        if (!attendee.custom_fields) {
          attendee.custom_fields = {}
        }
        for (let field of event.data.custom_fields) {
          if (!(field.field_name in attendee.custom_fields)) {
            attendee.custom_fields[field.field_name] = ''
          }
        }
      }
    }
  }
}

watch(customFieldsApplyToAll, (newValue) => {
  if (!event.data?.custom_fields) return

  if (newValue) {
    // When switching to "apply to all", clear individual attendee custom fields
    for (let attendee of checkoutInfo.attendees) {
      attendee.custom_fields = {}
    }
  } else {
    // When switching to individual, initialize custom fields for each attendee
    for (let attendee of checkoutInfo.attendees) {
      if (!attendee.custom_fields) {
        attendee.custom_fields = {}
      }
      for (let field of event.data.custom_fields) {
        attendee.custom_fields[field.field_name] = globalCustomFields[field.field_name] || ''
      }
    }
  }
})

function isTierExpired(tier) {
  return tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
}

function createOrder() {
  if (checkoutFormErrors.value.length > 0) {
    errorMessage.value = checkoutFormErrors.value.join(', ')
    return
  } else {
    errorMessage.value = null
  }

  rzpCheckout.value.createOrder(
    totalAmount.value,
    checkoutInfo.email,
    {
      event: eventName.value,
      tier: checkoutInfo.tier,
      attendees: checkoutInfo.attendees,
      num_seats: checkoutInfo.numSeats,
      custom_fields_apply_to_all: customFieldsApplyToAll.value,
      global_custom_fields: customFieldsApplyToAll.value ? globalCustomFields : null,
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
    event.data.event_name,
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

const activeTiers = computed(() => {
  let tiers = event.data?.tiers || []
  tiers = tiers.filter((tier) => {
    const isEnabled = Boolean(tier.enabled)
    const deadlinePassed = tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
    return isEnabled && !deadlinePassed
  })
  return tiers
})

const inactiveTiers = computed(() => {
  let tiers = event.data?.tiers || []
  tiers = tiers.filter((tier) => {
    const isEnabled = Boolean(tier.enabled)
    const deadlinePassed = tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
    return !isEnabled || deadlinePassed
  })
  return tiers
})

const ticketTiers = computed(() => {
  return activeTiers.value
})

const seatOptions = computed(() => {
  return Array.from({ length: MAX_SEATS_PER_BOOKING }, (_, i) => i + 1).map((i) => ({
    label: i.toString(),
    value: i,
  }))
})

const checkoutFormErrors = computed(() => {
  const errors = []
  if (!checkoutInfo.email) {
    errors.push('\nPlease enter your email')
  }

  if (
    checkoutInfo.email &&
    !checkoutInfo.email.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)
  ) {
    errors.push('\nPlease enter a valid email address')
  }

  if (checkoutInfo.attendees.some((a) => !a.full_name || !a.email)) {
    errors.push('\nPlease fill in all attendee details')
  }

  // Validate global custom fields if apply to all is enabled
  if (customFieldsApplyToAll.value) {
    for (let field of event.data?.custom_fields || []) {
      if (field.mandatory && !globalCustomFields[field.field_name]) {
        errors.push(`\nPlease fill in ${field.label}`)
      }
    }
  } else {
    // Validate individual attendee custom fields
    for (let attendee of checkoutInfo.attendees) {
      for (let field of event.data?.custom_fields || []) {
        if (field.mandatory && !attendee.custom_fields?.[field.field_name]) {
          errors.push(`\nPlease fill in ${field.label} for all attendees`)
          break // Only show error once per missing field
        }
      }
    }
  }

  for (let attendee of checkoutInfo.attendees) {
    if (
      attendee.email &&
      !attendee.email.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)
    ) {
      errors.push('\nPlease enter a valid email address for all attendees')
    }
  }

  if (!checkoutInfo.state) {
    errors.push('\nPlease select a state in Billing Details')
  }

  if (!checkoutInfo.buyer_name) {
    errors.push('\nPlease enter name in Billing Details')
  }

  if (!checkoutInfo.readRefundPolicy) {
    errors.push(
      '\nPlease read and accept our refund policy if you want to proceed with the purchase',
    )
  }

  return errors
})
</script>
