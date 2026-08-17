<template>
  <RazorpayCheckout v-if="currentStep === 4" ref="rzpCheckout" @error="onPaymentError" />
  <Header />
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{ title: 'Tickets are closed!', message: dialogError }"
  />

  <div v-if="event.data" class="bg-surface-gray-1 min-h-screen">
    <div class="mx-auto w-full max-w-[1100px] px-4">
      <main
        id="main-content"
        class="flex flex-col gap-4 pb-24 md:pb-8"
        aria-label="Ticket registration"
      >
        <Breadcrumb :items="breadcrumbItems" />

        <!-- Page Header -->
        <div class="flex flex-col gap-1">
          <h1 class="text-2xl font-bold tracking-tight text-ink-gray-9">Registration</h1>
        </div>

        <EventHeader :event="event.data" />

        <div
          role="note"
          class="flex items-center gap-2 px-3 py-2 rounded-lg border border-outline-amber-2 bg-surface-amber-1 text-ink-amber-3 text-sm self-center"
        >
          <IconInfoCircle class="w-5 h-5 shrink-0" aria-hidden="true" />
          <span
            >Tickets are non-cancellable.
            <a
              href="https://fossunited.org/refund-transfer-policy"
              target="_blank"
              class="underline font-semibold"
              >Only transfers are allowed</a
            >
          </span>
        </div>
        <!-- Form description -->
        <div
          v-if="event.data?.ticket_form_description"
          class="my-2 prose prose-sm max-w-none bg-surface-gray-2 rounded-lg px-4 py-3"
          v-html="markdownToHTML(event.data.ticket_form_description)"
        ></div>

        <!-- Steps + Sidebar two-column -->
        <div class="flex flex-col md:flex-row md:items-start md:gap-6">
          <div class="flex-1 min-w-0 flex flex-col gap-4">
            <!-- Step Progress -->
            <nav aria-label="Registration steps">
              <Progress
                :value="currentStep * 25"
                :intervals="true"
                :interval-count="4"
                size="lg"
                :label="stepTitle"
                :hint="true"
              >
                <template #hint>
                  <span class="text-sm font-medium text-ink-gray-4" aria-live="polite"
                    >{{ currentStep }} / 4</span
                  >
                </template>
              </Progress>
            </nav>

            <!-- Step Content -->
            <transition
              mode="out-in"
              :enter-active-class="tClasses.enterActive"
              :enter-from-class="tClasses.enterFrom"
              :enter-to-class="tClasses.enterTo"
              :leave-active-class="tClasses.leaveActive"
              :leave-from-class="tClasses.leaveFrom"
              :leave-to-class="tClasses.leaveTo"
            >
              <div :key="currentStep">
                <!-- Select Tiers -->
                <div
                  v-if="currentStep === 1"
                  class="flex flex-col gap-6 items-center"
                  role="list"
                  aria-label="Available ticket tiers"
                >
                  <article
                    v-for="tier in sortedTiers"
                    :key="tier.name"
                    role="listitem"
                    class="bg-surface-white border border-outline-gray-2 rounded-2xl flex flex-wrap items-stretch gap-3 p-4 w-full"
                    :class="
                      !isTierActive(tier)
                        ? isTierComingSoon(tier)
                          ? 'opacity-70'
                          : 'opacity-50'
                        : 'shadow-sm'
                    "
                    :aria-label="`${tier.title} ticket, ₹${tier.price}`"
                    :aria-disabled="!isTierActive(tier)"
                  >
                    <!-- Image -->
                    <div
                      class="bg-surface-gray-1 border border-outline-gray-2 rounded-lg overflow-hidden w-[58px] h-20 md:w-[78px] md:h-[108px]"
                      aria-hidden="true"
                    >
                      <img
                        :src="getTierImage(tier)"
                        :alt="`${tier.title} ticket`"
                        class="w-full h-full object-contain"
                      />
                    </div>

                    <div class="flex-1 min-w-0 flex flex-col justify-evenly">
                      <p class="font-semibold text-base text-ink-gray-9">{{ tier.title }}</p>
                      <p class="font-semibold text-xl text-ink-gray-9">₹{{ tier.price }}</p>
                      <div class="flex flex-wrap gap-1">
                        <Badge
                          v-if="tier.tshirt_included"
                          class="w-fit"
                          variant="subtle"
                          theme="green"
                          title="T-shirt is included with this tier at no extra charge"
                          >T-shirt Included</Badge
                        >
                        <Badge v-if="isTierSoldOut(tier)" class="w-fit" variant="solid" theme="red"
                          >Sold Out</Badge
                        >
                        <Badge
                          v-else-if="isTierComingSoon(tier)"
                          class="w-fit"
                          variant="subtle"
                          theme="blue"
                          >Coming Soon</Badge
                        >
                        <Badge
                          v-else-if="!tier.enabled"
                          class="w-fit"
                          variant="outline"
                          theme="red"
                          >Disabled</Badge
                        >
                        <Badge
                          v-else-if="isTierExpired(tier)"
                          class="w-fit"
                          variant="outline"
                          theme="orange"
                          >Expired</Badge
                        >
                        <Badge
                          v-if="tier.maximum_tickets > 0 && isTierActive(tier)"
                          :theme="tierRemainingTheme(tier)"
                          variant="subtle"
                          class="w-fit"
                          :aria-label="`${tierRemainingLabel(tier)} for ${tier.title}`"
                          >{{ tierRemainingLabel(tier) }}</Badge
                        >
                        <Badge
                          v-if="tier.valid_till && isTierActive(tier)"
                          class="w-fit"
                          variant="outline"
                          theme="green"
                          >Available till {{ dayjs(tier.valid_till).format('MMM D, YYYY') }}</Badge
                        >
                      </div>
                    </div>

                    <!-- Counter: only shown for active tiers -->
                    <div
                      v-if="isTierActive(tier)"
                      class="order-last md:order-none w-full md:w-auto flex items-center gap-1 justify-center md:justify-end md:self-center md:shrink-0 md:pl-2"
                      :aria-label="`${tier.title} ticket quantity`"
                    >
                      <button
                        :disabled="!isTierActive(tier) || (tierCounts[tier.name] || 0) <= 0"
                        :aria-label="`Remove one ${tier.title} ticket`"
                        class="w-10 h-10 rounded-lg border flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                        :class="
                          (tierCounts[tier.name] || 0) > 0
                            ? 'border-ink-gray-9 bg-ink-gray-9'
                            : 'border-ink-gray-9 bg-surface-white'
                        "
                        @click="decrementTier(tier.name)"
                      >
                        <IconMinus
                          aria-hidden="true"
                          class="w-4 h-4"
                          :class="(tierCounts[tier.name] || 0) > 0 ? '' : 'text-ink-gray-9'"
                        />
                      </button>
                      <span
                        class="w-8 text-center font-semibold text-ink-gray-9"
                        aria-live="polite"
                        :aria-label="`${tierCounts[tier.name] || 0} ${tier.title} tickets selected`"
                        >{{ tierCounts[tier.name] || 0 }}</span
                      >
                      <button
                        :disabled="!isTierActive(tier) || totalTickets >= MAX_SEATS"
                        :aria-label="`Add one ${tier.title} ticket`"
                        class="w-10 h-10 rounded-lg border flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                        :class="
                          isTierActive(tier)
                            ? 'border-ink-gray-9 bg-ink-gray-9'
                            : 'border-ink-gray-9 bg-surface-white'
                        "
                        @click="incrementTier(tier.name)"
                      >
                        <IconPlus
                          aria-hidden="true"
                          class="w-4 h-4"
                          :class="isTierActive(tier) ? '' : 'text-ink-gray-9'"
                        />
                      </button>
                    </div>

                    <div
                      v-if="tier.description"
                      class="w-full prose prose-sm prose-p:text-xs prose-p:text-ink-gray-5 prose-p:leading-relaxed prose-p:my-0.5 max-w-full"
                      v-html="renderedDescription(tier.description)"
                    />
                  </article>
                </div>

                <!-- STEP 2: Attendee Details -->
                <div v-else-if="currentStep === 2" class="flex flex-col gap-6">
                  <AttendeeCard
                    v-for="(attendee, idx) in attendees"
                    :key="idx"
                    :attendee="attendee"
                    :index="idx"
                    :tier-title="getTierTitle(attendee.ticket_type)"
                    :custom-fields="!customFieldsApplyToAll ? event.data.custom_fields : []"
                    :show-tshirt="Boolean(event.data.paid_tshirts_available)"
                    :tshirt-price="event.data.t_shirt_price || 0"
                    :tshirt-included="isTierTshirtIncluded(attendee.ticket_type)"
                    :can-delete="attendees.length > 1"
                    @update:attendee="attendees[idx] = $event"
                    @delete="removeAttendee(idx)"
                  />

                  <div
                    v-if="event.data.custom_fields?.length > 0 && attendees.length > 1"
                    class="flex flex-col gap-4"
                  >
                    <Switch
                      v-model="customFieldsApplyToAll"
                      class="w-fit text-xs"
                      label="Apply same answers for all tickets"
                    />
                    <div
                      v-if="customFieldsApplyToAll"
                      class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 grid grid-cols-1 md:grid-cols-2 gap-6"
                    >
                      <FormControl
                        v-for="field in event.data.custom_fields"
                        :key="field.name"
                        v-model="globalCustomFields[field.field_name]"
                        :type="FIELD_TYPE_MAP[field.field_type]"
                        :label="field.label"
                        :options="field.options"
                        :required="Boolean(field.mandatory)"
                        size="sm"
                        variant="subtle"
                      />
                    </div>
                  </div>

                  <div class="flex justify-center">
                    <button
                      :disabled="totalTickets >= MAX_SEATS"
                      class="flex items-center gap-2 bg-outline-gray-1 hover:bg-outline-gray-2 border border-outline-gray-2 rounded-lg px-5 py-2.5 font-semibold text-sm uppercase tracking-wider text-ink-gray-9 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                      @click="addAttendee"
                    >
                      <IconPlus class="w-5 h-5" /> Add Another Ticket
                    </button>
                  </div>
                </div>

                <!-- STEP 3: Verify Details -->
                <div v-else-if="currentStep === 3" class="flex flex-wrap gap-6 justify-center">
                  <div
                    v-for="(attendee, idx) in attendees"
                    :key="idx"
                    class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 flex flex-col gap-5 w-full max-w-[375px]"
                  >
                    <div class="flex items-center justify-between">
                      <span class="font-semibold text-2xl text-ink-gray-9 tracking-tight"
                        >#{{ idx + 1 }}</span
                      >
                      <span
                        class="bg-surface-green-1 text-ink-green-3 text-xs font-semibold tracking-wider uppercase px-3 py-1.5 rounded-lg"
                        >{{ getTierTitle(attendee.ticket_type) }}</span
                      >
                    </div>
                    <div class="flex flex-col gap-3">
                      <div>
                        <p class="font-semibold text-ink-gray-8">
                          {{ attendee.full_name || '—' }}
                        </p>
                        <p class="text-sm text-ink-gray-5">
                          {{
                            [attendee.designation, attendee.organization]
                              .filter(Boolean)
                              .join(' | ')
                          }}
                        </p>
                      </div>
                      <div class="text-sm text-ink-gray-5 flex flex-col gap-1">
                        <p>{{ attendee.email }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-6 flex-wrap">
                      <div
                        v-if="
                          isTierTshirtIncluded(attendee.ticket_type) ||
                          event.data.paid_tshirts_available
                        "
                        class="flex items-center gap-1.5 text-sm"
                        :class="
                          isTierTshirtIncluded(attendee.ticket_type)
                            ? 'text-ink-green-3'
                            : 'text-ink-gray-7'
                        "
                      >
                        <IconShirt class="w-5 h-5" aria-hidden="true" />
                        <span>{{
                          isTierTshirtIncluded(attendee.ticket_type)
                            ? 'T-shirt Included'
                            : attendee.wants_tshirt
                              ? attendee.tshirt_size
                              : 'Without T-shirt'
                        }}</span>
                      </div>
                      <div
                        v-if="event.data.catering && event.data.catering !== 'None'"
                        class="flex items-center gap-1.5 text-sm text-ink-gray-7"
                      >
                        <IconSoup class="w-5 h-5" />
                        <span>{{ event.data.catering }} included</span>
                      </div>
                    </div>
                    <p
                      v-if="getTierDescription(attendee.ticket_type)"
                      class="text-sm text-ink-gray-6"
                    >
                      {{ getTierDescription(attendee.ticket_type) }}
                    </p>
                  </div>
                </div>

                <!-- STEP 4: Billing -->
                <div v-else-if="currentStep === 4">
                  <BillingForm :billing="billing" :state-options="stateOptions.data" />
                </div>
              </div>
            </transition>

            <!-- Navigation (Steps 1-3) -->
            <template v-if="currentStep !== 4">
              <div class="flex gap-4 items-center justify-end">
                <Button
                  v-if="currentStep > 1"
                  label="Back"
                  size="lg"
                  variant="subtle"
                  icon-left="chevron-left"
                  class="uppercase !font-medium"
                  @click="prevStep"
                />
                <Button
                  label="Next"
                  size="lg"
                  variant="solid"
                  icon-right="chevron-right"
                  class="uppercase !font-medium !px-6"
                  :disabled="currentStep === 1 && totalTickets === 0"
                  @click="nextStep"
                />
              </div>
            </template>
            <div v-else class="flex justify-between">
              <Button
                label="Back"
                size="lg"
                variant="subtle"
                icon-left="chevron-left"
                class="uppercase !font-medium"
                aria-label="Go back to verify details"
                @click="prevStep"
              />
              <Button
                label="Proceed to Pay"
                size="lg"
                variant="solid"
                icon-right="chevron-right"
                class="uppercase !font-medium !px-6"
                :loading="rzpCheckout?.resource.loading"
                aria-label="Proceed to payment"
                @click="createOrder"
              />
            </div>

            <!-- Error messages -->
            <ul
              v-if="errorMessages.length"
              role="alert"
              aria-live="assertive"
              class="flex flex-col gap-1 p-3 rounded-lg bg-surface-red-1 border border-outline-red-2"
            >
              <li
                v-for="msg in errorMessages"
                :key="msg"
                class="text-sm text-ink-red-3 flex items-start gap-1.5"
              >
                <span class="mt-0.5 shrink-0">•</span>
                <span>{{ msg }}</span>
              </li>
            </ul>
          </div>

          <aside
            class="hidden md:block shrink-0 w-[300px] self-start sticky top-6"
            aria-label="Order summary"
          >
            <TicketSummary
              :active-tier-counts="activeTierCounts"
              :all-tiers="allTiers"
              :tshirt-count="numTShirtsAdded"
              :tshirt-price="event.data.t_shirt_price || 0"
              :error-message="currentStep === 4 ? errorMessage || '' : ''"
            />
          </aside>
        </div>
      </main>
    </div>

    <!-- Mobile order summary drawer -->
    <div
      class="fixed bottom-0 inset-x-0 z-40 md:hidden bg-surface-white border-t border-outline-gray-2 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]"
      role="region"
      aria-label="Order summary"
    >
      <!-- Expanded breakdown -->
      <div
        v-if="mobileBarExpanded"
        id="mobile-order-summary"
        class="px-4 pt-4 pb-2 max-h-[55vh] overflow-y-auto border-b border-outline-gray-2"
      >
        <TicketSummary
          :active-tier-counts="activeTierCounts"
          :all-tiers="allTiers"
          :tshirt-count="numTShirtsAdded"
          :tshirt-price="event.data.t_shirt_price || 0"
          :error-message="currentStep === 4 ? errorMessage || '' : ''"
        />
      </div>
      <!-- Always visible: total toggle row -->
      <button
        class="w-full flex items-center justify-between px-4 py-3"
        :aria-expanded="String(mobileBarExpanded)"
        aria-controls="mobile-order-summary"
        @click="mobileBarExpanded = !mobileBarExpanded"
      >
        <div class="text-left">
          <p class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">Total</p>
          <p
            class="text-lg font-bold text-ink-gray-9 leading-none"
            aria-live="polite"
            :aria-label="`Total amount: ₹${summaryTotal}`"
          >
            ₹{{ summaryTotal }}
          </p>
        </div>
        <IconChevronUp
          v-if="mobileBarExpanded"
          class="w-5 h-5 text-ink-gray-5"
          aria-hidden="true"
        />
        <IconChevronDown v-else class="w-5 h-5 text-ink-gray-5" aria-hidden="true" />
      </button>
    </div>
  </div>

  <!-- Loading / Error -->
  <div
    v-else
    class="p-5 bg-surface-gray-1 min-h-screen flex items-center justify-center"
    role="status"
    aria-live="polite"
  >
    <Button
      v-if="event.loading"
      :loading="true"
      loading-text="Loading"
      aria-label="Loading event details"
    />
    <p v-else-if="!eventName" class="text-ink-gray-8 font-medium">Event not found</p>
    <p v-else-if="event.error" role="alert">Error loading event</p>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted, watch, inject } from 'vue'
import { useRouter } from 'vue-router'
import {
  createResource,
  FormControl,
  Switch,
  Button,
  usePageMeta,
  ErrorMessage,
  Badge,
  Dialog,
  Progress,
} from 'frappe-ui'
import { markdownToHTML } from 'frappe-ui/src/utils/markdown'
import { toast } from 'vue-sonner'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import EventHeader from '@/components/common/EventHeader.vue'
import RazorpayCheckout from '@/components/common/RazorpayCheckout.vue'
import AttendeeCard from '@/components/tickets/AttendeeCard.vue'
import TicketSummary from '@/components/tickets/TicketSummary.vue'
import BillingForm from '@/components/tickets/BillingForm.vue'
import {
  IconInfoCircle,
  IconPlus,
  IconMinus,
  IconShirt,
  IconSoup,
  IconChevronUp,
  IconChevronDown,
} from '@tabler/icons-vue'
import { cleanedHTML, showError } from '@/helpers/utils'

const dayjs = inject('$dayjs')
const router = useRouter()

const MAX_SEATS = 10
const FIELD_TYPE_MAP = { Data: 'text', Int: 'number', Select: 'select' }

// Tier image keyword mapping — order matters
const TIER_IMAGE_KEYWORDS = [
  {
    keywords: ['student', 'stud'],
    file: 'event-ticket-student.svg',
  },
  {
    keywords: ['enthusiast', 'hobbyist', 'fan', 'supporter'],
    file: 'event-ticket-enthusiast.svg',
  },
  {
    keywords: ['contributor', 'professional', 'pro', 'developer', 'dev', 'premium', 'expert'],
    file: 'event-ticket-contributor.svg',
  },
]
const TIER_IMAGES_BASE = '/assets/fossunited/images/tickets/'
const TIER_IMAGE_DEFAULT = 'event-ticket-regular.svg'

usePageMeta(() => ({ title: 'Book Tickets' }))

// State
const eventName = ref(null)
const currentStep = ref(1)
const transitionDir = ref('next')
const errorMessage = ref(null)
const errorMessages = ref([])
const showDialog = ref(false)
const dialogError = ref('')
const rzpCheckout = ref(null)
const mobileBarExpanded = ref(false)

const tierCounts = reactive({})
const attendees = ref([])
const customFieldsApplyToAll = ref(false)
const globalCustomFields = reactive({})

const billing = reactive({
  buyer_name: '',
  email: '',
  state: '',
  hasGST: false,
  company_name: '',
  gstn: '',
  billing_address: '',
  coupon_code: '',
  readRefundPolicy: false,
  acceptCoC: false,
  subscribeNewsletter: false,
})

// Computed
const allTiers = computed(() => event.data?.tiers || [])

const sortedTiers = computed(() =>
  [...allTiers.value].sort((a, b) => {
    const aActive = isTierActive(a) ? 0 : 1
    const bActive = isTierActive(b) ? 0 : 1
    if (aActive !== bActive) return aActive - bActive
    return (a.price || 0) - (b.price || 0)
  }),
)

const activeTierCounts = computed(() => {
  const result = {}
  for (const [name, count] of Object.entries(tierCounts)) {
    if (count > 0) {
      const tier = allTiers.value.find((t) => t.name === name)
      if (tier && isTierActive(tier)) result[name] = count
    }
  }
  return result
})

// Only count active tiers to prevent paying for expired/disabled ones
const totalTickets = computed(() =>
  Object.values(activeTierCounts.value).reduce((s, c) => s + (c || 0), 0),
)

const numTShirtsAdded = computed(
  () =>
    attendees.value.filter((a) => a.wants_tshirt && !isTierTshirtIncluded(a.ticket_type)).length,
)

const summaryTotal = computed(() => {
  const tierTotal = Object.entries(activeTierCounts.value).reduce((sum, [name, count]) => {
    const tier = allTiers.value.find((t) => t.name === name)
    return sum + (tier?.price || 0) * (count || 0)
  }, 0)
  return tierTotal + numTShirtsAdded.value * (event.data?.t_shirt_price || 0)
})

const stepTitle = computed(
  () =>
    ({
      1: 'Select your Tickets',
      2: 'Enter Attendee Details',
      3: 'Verify Details',
      4: 'Billing',
    })[currentStep.value] || '',
)

const tClasses = computed(() => {
  const fwd = transitionDir.value === 'next'
  return {
    enterActive: 'transition ease-out duration-300',
    enterFrom: `opacity-0 transform ${fwd ? 'translate-x-8' : '-translate-x-8'}`,
    enterTo: 'opacity-100 transform translate-x-0',
    leaveActive: 'transition ease-in duration-200',
    leaveFrom: 'opacity-100 transform translate-x-0',
    leaveTo: `opacity-0 transform ${fwd ? '-translate-x-8' : 'translate-x-8'}`,
  }
})

const breadcrumbItems = computed(() => [
  { label: event.data?.event_name || '...', link: redirectToEvent.value },
  { label: 'Tickets' },
  { label: 'Register' },
])

const redirectToEvent = computed(() =>
  event.data ? `${window.location.origin}/${event.data.route}` : window.location.origin,
)

// Helpers
function isTierActive(tier) {
  return Boolean(tier.enabled) && !isTierExpired(tier)
}
function isTierExpired(tier) {
  return tier.valid_till && dayjs().isAfter(tier.valid_till, 'day')
}
function getTierTitle(tierName) {
  return allTiers.value.find((t) => t.name === tierName)?.title || tierName
}

function getTierDescription(tierName) {
  return allTiers.value.find((t) => t.name === tierName)?.description || ''
}

function isTierTshirtIncluded(tierName) {
  return Boolean(allTiers.value.find((t) => t.name === tierName)?.tshirt_included)
}

function isTierSoldOut(tier) {
  return tier.maximum_tickets > 0 && (tier.sold_count || 0) >= tier.maximum_tickets
}

function isTierComingSoon(tier) {
  return !tier.enabled && !isTierSoldOut(tier) && tier.valid_till && !isTierExpired(tier)
}

function tierRemainingCount(tier) {
  if (!tier.maximum_tickets) return null
  return tier.maximum_tickets - (tier.sold_count || 0)
}

function tierRemainingTheme(tier) {
  const r = tierRemainingCount(tier)
  if (r === null) return 'gray'
  const pct = r / tier.maximum_tickets
  if (r <= 5 || pct <= 0.1) return 'red'
  if (r <= 15 || pct <= 0.25) return 'orange'
  return 'green'
}

function tierRemainingLabel(tier) {
  const r = tierRemainingCount(tier)
  if (r === null || r < 0) return ''
  if (r === 0) return 'Sold Out'
  const pct = r / tier.maximum_tickets
  if (r <= 5 || pct <= 0.1) return `Only ${r} left!`
  if (r <= 15 || pct <= 0.25) return `${r} left`
  return `${r} available`
}

function getTierImage(tier) {
  // If backend provides a custom image URL, use it
  if (tier.image) return tier.image
  const name = (tier.title || '').toLowerCase()
  for (const { keywords, file } of TIER_IMAGE_KEYWORDS) {
    if (keywords.some((k) => name.includes(k))) return TIER_IMAGES_BASE + file
  }
  return TIER_IMAGES_BASE + TIER_IMAGE_DEFAULT
}

function renderedDescription(raw) {
  if (!raw) return ''
  return cleanedHTML(markdownToHTML(raw))
}

// Tier counter actions — guard against inactive tiers
function incrementTier(name) {
  const tier = allTiers.value.find((t) => t.name === name)
  if (!tier || !isTierActive(tier)) return
  if (totalTickets.value >= MAX_SEATS) return
  tierCounts[name] = (tierCounts[name] || 0) + 1
}
function decrementTier(name) {
  if ((tierCounts[name] || 0) <= 0) return
  tierCounts[name]--
}

// Attendee management
function makeAttendee(ticketType = '') {
  const a = {
    ticket_type: ticketType,
    full_name: '',
    email: '',
    designation: '',
    organization: '',
    wants_tshirt: isTierTshirtIncluded(ticketType),
    tshirt_size: '',
    subscribe_chapter_mailing: true,
    custom_fields: {},
  }
  for (const f of event.data?.custom_fields || []) {
    a.custom_fields[f.field_name] = ''
  }
  return a
}

function buildAttendees() {
  const newList = []
  const used = new Set()
  // Use activeTierCounts to prevent building attendees for inactive tiers
  for (const [name, count] of Object.entries(activeTierCounts.value)) {
    for (let i = 0; i < (count || 0); i++) {
      const existing = attendees.value.find((a) => a.ticket_type === name && !used.has(a))
      if (existing) {
        used.add(existing)
        newList.push(existing)
      } else {
        newList.push(makeAttendee(name))
      }
    }
  }
  attendees.value = newList
}

function addAttendee() {
  if (totalTickets.value >= MAX_SEATS) return
  const firstActiveTier = Object.keys(activeTierCounts.value)[0] || ''
  attendees.value.push(makeAttendee(firstActiveTier))
  if (firstActiveTier) tierCounts[firstActiveTier] = (tierCounts[firstActiveTier] || 0) + 1
}

function removeAttendee(index) {
  const removed = attendees.value.splice(index, 1)[0]
  if (removed?.ticket_type && (tierCounts[removed.ticket_type] || 0) > 0) {
    tierCounts[removed.ticket_type]--
  }
}

// Navigation
function onPaymentError(err) {
  const msg =
    typeof err === 'string' ? err : err?.messages?.[0] || err?.message || 'Payment failed'
  setError(msg)
  showError(err, 'Failed to initiate payment')
}

function setErrors(msgs) {
  errorMessages.value = msgs
  errorMessage.value = msgs[0] || null
  if (msgs[0]) toast.error(msgs[0], { duration: 4000 })
}

function setError(msg) {
  setErrors(msg ? [msg] : [])
}

function nextStep() {
  errorMessages.value = []
  errorMessage.value = null
  const errors = validateStep(currentStep.value)
  if (errors.length) {
    setErrors(errors)
    return
  }
  if (currentStep.value === 1) buildAttendees()
  transitionDir.value = 'next'
  currentStep.value++
}

function prevStep() {
  errorMessages.value = []
  errorMessage.value = null
  if (currentStep.value <= 1) return
  transitionDir.value = 'back'
  currentStep.value--
}

function validateStep(step) {
  const errors = []
  if (step === 1 && totalTickets.value === 0) {
    errors.push('Please select at least one ticket')
  }
  if (step === 2) {
    for (const [i, a] of attendees.value.entries()) {
      if (!a.full_name) errors.push(`Attendee #${i + 1}: Full name is required`)
      else if (!a.email) errors.push(`Attendee #${i + 1}: Email is required`)
      else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(a.email)) {
        errors.push(`Attendee #${i + 1}: Invalid email address`)
      }
      if (a.wants_tshirt && !a.tshirt_size) {
        errors.push(`Attendee #${i + 1}: T-shirt size is required`)
      }
      if (!customFieldsApplyToAll.value) {
        for (const f of event.data?.custom_fields || []) {
          if (f.mandatory && !a.custom_fields?.[f.field_name]) {
            errors.push(`Attendee #${i + 1}: ${f.label} is required`)
          }
        }
      }
    }
    if (customFieldsApplyToAll.value) {
      for (const f of event.data?.custom_fields || []) {
        if (f.mandatory && !globalCustomFields[f.field_name]) {
          errors.push(`${f.label} is required`)
        }
      }
    }
  }
  return errors
}

// Razorpay Order
function createOrder() {
  errorMessages.value = []
  errorMessage.value = null
  const errors = []
  if (!billing.buyer_name) errors.push('Please enter your name in Billing Details')
  if (!billing.email) errors.push('Please enter your email in Billing Details')
  else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(billing.email)) {
    errors.push('Please enter a valid email address')
  }
  if (!billing.state) errors.push('Please select a state in Billing Details')
  if (billing.hasGST) {
    if (!billing.company_name) errors.push('Please enter the company name for GST billing')
    if (!billing.gstn) errors.push('Please enter the GSTN')
    if (!billing.billing_address) errors.push('Please enter the billing address for GST billing')
  }
  if (!billing.readRefundPolicy) errors.push('Please accept the Refund Policy to proceed')
  if (!billing.acceptCoC) errors.push('Please accept the Code of Conduct to proceed')
  if (errors.length) {
    setErrors(errors)
    return
  }

  // Use activeTierCounts for accurate billing — inactive tiers excluded
  const subTotal =
    Object.entries(activeTierCounts.value).reduce((s, [name, count]) => {
      const tier = allTiers.value.find((t) => t.name === name)
      return s + (tier?.price || 0) * (count || 0)
    }, 0) +
    numTShirtsAdded.value * (event.data.t_shirt_price || 0)

  if (billing.subscribeNewsletter) {
    newsletterSubscribe.fetch()
  }

  rzpCheckout.value.createOrder(
    subTotal,
    billing.email,
    {
      event: eventName.value,
      tier_counts: { ...activeTierCounts.value },
      tiers_snapshot: Object.fromEntries(
        Object.keys(activeTierCounts.value).map((name) => {
          const t = allTiers.value.find((t) => t.name === name)
          return [name, { title: t?.title, price: t?.price }]
        }),
      ),
      attendees: attendees.value.map((a) => ({ ...a, accept_coc: billing.acceptCoC ? 1 : 0 })),
      num_seats: totalTickets.value,
      custom_fields_apply_to_all: customFieldsApplyToAll.value,
      global_custom_fields: customFieldsApplyToAll.value ? { ...globalCustomFields } : null,
    },
    event.data.doctype,
    event.data.name,
    {
      buyer_name: billing.buyer_name,
      state: billing.state,
      ...(billing.hasGST
        ? {
            company_name: billing.company_name,
            gstn: billing.gstn,
            billing_address: billing.billing_address,
          }
        : {}),
    },
    event.data.event_name,
  )
}

// Resources
const newsletterSubscribe = createResource({
  url: 'fossunited.api.emailing.listmonk_subscribe',
  makeParams: () => ({ email: billing.email, name: billing.buyer_name }),
})

const stateOptions = createResource({
  url: 'fossunited.api.dashboard.get_states',
  transform: (data) => data.map((s) => ({ label: s.name, value: s.name })),
  auto: true,
})

const event = createResource({
  url: 'fossunited.api.dashboard.get_event',
  makeParams: () => ({ name: eventName.value }),
  onSuccess(data) {
    for (const k in tierCounts) delete tierCounts[k]
    for (const f of data.custom_fields || []) {
      globalCustomFields[f.field_name] = ''
      if (f.field_type === 'Select' && typeof f.options === 'string') {
        f.options = f.options.split('\n')
      }
    }
  },
})

const checkIfTicketsLive = createResource({
  url: 'fossunited.api.tickets.is_ticket_live',
  makeParams: () => ({ event_id: eventName.value }),
  onSuccess(data) {
    if (!data) {
      dialogError.value = 'Tickets are not live for this event'
      showDialog.value = true
      return
    }
    event.fetch()
  },
  onError() {
    setError('Error checking ticket status')
  },
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.has('event')) {
    eventName.value = params.get('event')
    checkIfTicketsLive.fetch()
  }
})

watch(customFieldsApplyToAll, (newVal) => {
  if (!newVal && event.data?.custom_fields) {
    for (const a of attendees.value) {
      if (!a.custom_fields) a.custom_fields = {}
      for (const f of event.data.custom_fields) {
        a.custom_fields[f.field_name] = globalCustomFields[f.field_name] || ''
      }
    }
  }
})
</script>
