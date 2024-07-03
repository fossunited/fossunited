<template>
  <div class="py-10 px-5 w-full flex justify-center">
    <div
      v-if="status == 'Approved' || status == 'Already Approved'"
      class="flex flex-col items-center gap-2"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="currentColor"
        class="icon w-10 h-10 fill-green-600 icon-tabler icons-tabler-filled icon-tabler-circle-check"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path
          d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-1.293 5.953a1 1 0 0 0 -1.32 -.083l-.094 .083l-3.293 3.292l-1.293 -1.292l-.094 -.083a1 1 0 0 0 -1.403 1.403l.083 .094l2 2l.094 .083a1 1 0 0 0 1.226 0l.094 -.083l4 -4l.083 -.094a1 1 0 0 0 -.083 -1.32z"
        />
      </svg>
      <div class="prose text-center">
        <div v-if="status == 'Approved'">
          <h2 class="my-3">Ticket Transferred Successfully!</h2>
          <p>
            Your ticket has been successfully transferred to the new owner.<br />
            An email has been sent to the new ticket holder.
          </p>
        </div>
        <div v-else-if="status == 'Already Approved'">
          <h2 class="my-3">Ticket Already Transferred!</h2>
          <p>
            Your ticket has already been transferred to the new owner.<br />
            An email has been sent to the new ticket holder.
          </p>
        </div>
      </div>
    </div>
    <div v-else-if="status == 'Rejected' || status == 'Already Rejected'" class="flex flex-col text-center items-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="currentColor"
        class="icon w-10 h-10 fill-red-600 icon-tabler icons-tabler-filled icon-tabler-circle-x"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path
          d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-6.489 5.8a1 1 0 0 0 -1.218 1.567l1.292 1.293l-1.292 1.293l-.083 .094a1 1 0 0 0 1.497 1.32l1.293 -1.292l1.293 1.292l.094 .083a1 1 0 0 0 1.32 -1.497l-1.292 -1.293l1.292 -1.293l.083 -.094a1 1 0 0 0 -1.497 -1.32l-1.293 1.292l-1.293 -1.292l-.094 -.083z"
        />
      </svg>
      <div class="prose">
        <div v-if="status == 'Rejected'">
            <h2 class="my-3">Transfer Rejected!</h2>
            <p>
                Your ticket transfer request has been rejected.<br />
                For further assistance, please send a mail at <a href="mailto:indiafoss@fossunited.org" class="underline">indiafoss@fossunited.org</a>.
            </p>
        </div>
        <div v-else-if="status == 'Already Rejected'">
            <h2 class="my-3">Transfer Already Rejected!</h2>
            <p>
                Your ticket transfer request has already been rejected.<br />
                For further assistance, please send a mail at <a href="mailto:indiafoss@fossunited.org">indiafoss@fossunited.org</a>
            </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'

const props = defineProps(['status'])
</script>
