<template>
    <div>
        <h1>Checkout with Razorpay</h1>

        <h2 class="text-xl font-bold">Select a tier</h2>

    <RadioGroup v-model="checkoutInfo.tier">

    <RadioGroupLabel class="text-base font-semibold leading-6 text-gray-900">Select a tier</RadioGroupLabel>

    <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-3 sm:gap-x-4">
      <RadioGroupOption as="template" v-for="tier in ticketTiers" :key="tier.name" :value="tier" v-slot="{ active, checked }">
        <div :class="[active ? 'border-indigo-600 ring-2 ring-indigo-600' : 'border-gray-300', 'relative flex cursor-pointer rounded-lg border bg-white p-4 shadow-sm focus:outline-none']">
          <span class="flex flex-1">
            <span class="flex flex-col">
              <RadioGroupLabel as="span" class="block text-sm font-medium text-gray-900">{{ tier.title }}</RadioGroupLabel>
              <RadioGroupDescription as="span" class="mt-1 flex items-center text-sm text-gray-500">{{ tier.description }}</RadioGroupDescription>
              <RadioGroupDescription as="span" class="mt-6 text-sm font-medium text-gray-900">{{ tier.price }}</RadioGroupDescription>
            </span>
          </span>
          <FeatherIcon name="check-circle" :class="[!checked ? 'invisible' : '', 'h-5 w-5 text-indigo-600']" aria-hidden="true" />
          <span :class="[active ? 'border' : 'border-2', checked ? 'border-indigo-600' : 'border-transparent', 'pointer-events-none absolute -inset-px rounded-lg']" aria-hidden="true" />
        </div>
      </RadioGroupOption>
    </div>
  </RadioGroup>

  <div class="max-w-lg m-2">
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
        placeholder="Placeholder"
        :disabled="false"
        label="Label"
        v-model="checkoutInfo.numSeats"
/>

<FormControl
    :type="'email'"
    size="sm"
    variant="subtle"
    placeholder="john@fossunited.org"
    :disabled="false"
    label="Email"
    v-model="checkoutInfo.email"
  />
  </div>

    <h2>Payment Summary</h2>
    <h3>Total Amount: {{ totalAmount }}</h3>

    <Button :disabled="createRazorpayOrder.loading" :loading="createRazorpayOrder.loading" @click="createOrder" variant="solid">Pay Now</Button>
    </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue';
import {createResource, FeatherIcon, FormControl, Button } from 'frappe-ui';
import { RadioGroup, RadioGroupDescription, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'
import {useRouter} from "vue-router";

const router = useRouter();

const eventName = ref(null);
const checkoutInfo = reactive({
    tier: null,
    numSeats: 1,
    email: "",
    attendees: [],
    event: eventName.value
})


const event = createResource({
    url: "fossunited.api.dashboard.get_event",
    makeParams() {
      return {
        name: eventName.value
      }
    },
    onSuccess(data) {
        const tiers = data.tiers;
        if (tiers.length > 0) {
            checkoutInfo.tier = tiers[0];
        }
    }
})

const createRazorpayOrder = createResource({
  "url": "fossunited.api.dashboard.create_razorpay_order",
  makeParams() {
    return {
      "checkout_info": {
        "amount": totalAmount.value,
        "email": checkoutInfo.email
      }
    }
  },
  onSuccess(data) {
    // show razorpay checkout window
    const orderId = data.order_id;
    const razorpayKey = data.key_id;

    const options = {
      "key": razorpayKey,
      "name": "FOSS United",
      "description": "FOSS United Event",
      "order_id": orderId,
      "handler": function(response) {
        createResource(
          {
            url: "fossunited.api.dashboard.handle_payment_success",
            auto: true,
            makeParams() {
              return {
                order_id: response.razorpay_order_id,
                payment_id: response.razorpay_payment_id,
                signature: response.razorpay_signature
              }
            },
            onSuccess() {
              router.replace({name: "success"});
            }
      })
      },
      "prefill": {
        "email": checkoutInfo.email,
      },
      "notes": {
        "address": "FOSS United Office"
      },
      "theme": {
        "color": "#3399cc"
      }
    };

    const rzp = new Razorpay(options);
    rzp.on("payment.failed", function(response) {
      console.log(response)
      // payment failed
      alert("Payment Failed!")
      createResource(
          {
            url: "fossunited.api.dashboard.handle_payment_failed",
            auto: true,
            makeParams() {
              return {
                order_id: response.error.metadata.order_id,
              }
            }
      })
    });
    rzp.open();
  }
})

function createOrder() {
  createRazorpayOrder.fetch();
}

onMounted(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.has('event')) {
        eventName.value = params.get('event')
        event.fetch();
    }

    // todo: check if razorpay script is already loaded
    let razorpayScript = document.createElement('script')
    razorpayScript.setAttribute('src', 'https://checkout.razorpay.com/v1/checkout.js')
    document.head.appendChild(razorpayScript)
})

const totalAmount = computed(() => {
    return checkoutInfo.tier?.price * checkoutInfo.numSeats;
})

const ticketTiers = computed(() => {
    return event.data?.tiers || [];
})
</script>
