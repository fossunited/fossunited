<template>
  <div
    class="bg-surface-white border border-outline-gray-2 rounded-lg p-6 md:p-8 flex flex-col gap-6"
    role="form"
    aria-label="Billing details"
  >
    <div class="flex items-center gap-2">
      <IconReceipt class="w-6 h-6 text-ink-gray-7" aria-hidden="true" />
      <span class="font-semibold text-ink-gray-9" id="billing-heading">Billing Details</span>
    </div>
    <FormControl
      v-model="billing.buyer_name"
      type="text"
      label="Name"
      size="sm"
      variant="subtle"
      placeholder="John Doe"
      required
      autocomplete="name"
    />
    <FormControl
      v-model="billing.state"
      type="select"
      label="State"
      size="sm"
      variant="subtle"
      :options="stateOptions"
      required
    />
    <FormControl
      v-model="billing.email"
      type="email"
      label="Email"
      size="sm"
      variant="subtle"
      placeholder="example@email.com"
      required
      autocomplete="email"
    />
    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <input
          id="gst-toggle"
          v-model="billing.hasGST"
          type="checkbox"
          class="rounded-sm"
          :aria-expanded="billing.hasGST"
          aria-controls="gst-fields"
        />
        <label for="gst-toggle" class="text-sm text-ink-gray-7 cursor-pointer"
          >Add GST Details</label
        >
      </div>
      <p class="text-xs text-ink-gray-4 ml-6" aria-live="polite">
        Invoice will be generated with GST details
      </p>
    </div>
    <template v-if="billing.hasGST">
      <div id="gst-fields" class="contents">
        <FormControl
          v-model="billing.company_name"
          type="text"
          label="Company Name"
          size="sm"
          variant="subtle"
          required
          autocomplete="organization"
        />
        <FormControl
          v-model="billing.gstn"
          type="text"
          label="GST Details (GSTN)"
          size="sm"
          variant="subtle"
          placeholder="22AAAAA0000A1Z5"
          required
        />
        <FormControl
          v-model="billing.billing_address"
          type="textarea"
          label="Billing Address"
          size="sm"
          variant="subtle"
          required
          autocomplete="street-address"
        />
      </div>
    </template>
    <div class="flex items-start gap-2">
      <input
        id="refund-policy"
        v-model="billing.readRefundPolicy"
        type="checkbox"
        class="mt-0.5 rounded-sm"
        required
        aria-required="true"
      />
      <label for="refund-policy" class="text-sm text-ink-gray-7 cursor-pointer leading-relaxed">
        I understand that tickets are non-refundable and have read the
        <a
          href="https://fossunited.org/refund-transfer-policy"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold underline"
          >Refund Policy</a
        ><span class="text-ink-red-3 ml-0.5" aria-label="required">*</span>
      </label>
    </div>
    <div class="flex items-start gap-2">
      <input
        id="coc-agreement"
        v-model="billing.acceptCoC"
        type="checkbox"
        class="mt-0.5 rounded-sm"
        required
        aria-required="true"
      />
      <label for="coc-agreement" class="text-sm text-ink-gray-7 cursor-pointer leading-relaxed">
        By registering for this event, you agree to abide by the FOSS United
        <a
          href="https://fossunited.org/code-of-conduct"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold underline"
          >Code of Conduct</a
        >. The code of conduct and anti-harassment policies apply to everyone participating in the
        event including sponsors, judges, mentors, volunteers, organisers and the FOSS United
        staff.
        <span class="text-ink-red-3 ml-0.5" aria-label="required">*</span>
      </label>
    </div>
    <div class="flex items-start gap-2">
      <input
        id="subscribe-newsletter"
        v-model="billing.subscribeNewsletter"
        type="checkbox"
        class="mt-0.5 rounded-sm"
      />
      <label
        for="subscribe-newsletter"
        class="text-sm text-ink-gray-7 cursor-pointer leading-relaxed"
      >
        Subscribe to the
        <a
          href="https://fossunited.org/newsletter"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold underline"
          >FOSS United newsletter</a
        >
        for updates on upcoming events and community news.
      </label>
    </div>
    <p class="text-xs text-ink-gray-4">
      By completing your registration, you also agree to our
      <a
        href="https://fossunited.org/privacy-policy"
        target="_blank"
        rel="noopener noreferrer"
        class="underline"
        >Privacy Policy</a
      >.
    </p>
  </div>
</template>

<script setup>
import { FormControl } from 'frappe-ui'
import { IconReceipt } from '@tabler/icons-vue'

defineProps({
  billing: { type: Object, required: true },
  stateOptions: { type: Array, default: () => [] },
})
</script>
