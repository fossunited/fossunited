<template></template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'

const router = useRouter()

const CHECKOUT_JS_SRC = 'https://checkout.razorpay.com/v1/checkout.js'

onMounted(() => {
  if (!isRazorpayCheckoutJSLoaded()) {
    loadRazorpayCheckoutJS()
  }
})

function handlePaymentSuccess(response) {
  createResource({
    url: 'fossunited.api.dashboard.handle_payment_success',
    auto: true,
    makeParams() {
      return {
        order_id: response.razorpay_order_id,
        payment_id: response.razorpay_payment_id,
        signature: response.razorpay_signature,
      }
    },
    onSuccess() {
      router.push({
        name: 'success',
        query: {
          order_id: response.razorpay_order_id,
          payment_id: response.razorpay_payment_id,
        },
      })
    },
  })
}

function handlePaymentFailed(response) {
  createResource({
    url: 'fossunited.api.dashboard.handle_payment_failed',
    auto: true,
    makeParams() {
      return {
        order_id: response.error.metadata.order_id,
      }
    },
  })
}

const createRazorpayOrderResource = createResource({
  url: 'fossunited.api.dashboard.create_razorpay_order',
  onSuccess(data) {
    const orderId = data.order_id
    const razorpayKey = data.key_id

    const options = {
      key: razorpayKey,
      name: 'FOSS United',
      description: 'FOSS United Event',
      order_id: orderId,
      handler: handlePaymentSuccess,
      theme: {
        color: '#3399cc',
      },
    }

    const rzp = new Razorpay(options)
    rzp.on('payment.failed', handlePaymentFailed)
    rzp.open()
  },
})

function isRazorpayCheckoutJSLoaded() {
  const scripts = document.getElementsByTagName('script')

  for (let script of scripts) {
    if (script.getAttribute('src') === CHECKOUT_JS_SRC) {
      return true
    }
  }

  return false
}

function loadRazorpayCheckoutJS() {
  let razorpayScript = document.createElement('script')
  razorpayScript.setAttribute('src', CHECKOUT_JS_SRC)
  document.head.appendChild(razorpayScript)
}

const createRazorpayOrder = (
  amount,
  customerEmail,
  metaData = {},
  refDocType = null,
  refDocName = null,
  taxDetails = {}
) => {
  createRazorpayOrderResource.fetch({
    checkout_info: {
      amount,
      email: customerEmail,
      tax_details: taxDetails
    },
    meta_data: metaData,
    ref_doctype: refDocType,
    ref_docname: refDocName,
  })
}

defineExpose({
  createOrder: createRazorpayOrder,
  resource: createRazorpayOrderResource,
})
</script>
