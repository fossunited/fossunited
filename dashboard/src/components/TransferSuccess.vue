<template>
  <div
    class="flex bg-gray-50 flex-col gap-4 w-full h-screen items-center py-12"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="icon w-20 h-20 stroke-green-600 icon-tabler icons-tabler-outline icon-tabler-circle-dashed-check"
    >
      <path stroke="none" d="M0 0h24v24H0z" fill="none" />
      <path d="M8.56 3.69a9 9 0 0 0 -2.92 1.95" />
      <path d="M3.69 8.56a9 9 0 0 0 -.69 3.44" />
      <path d="M3.69 15.44a9 9 0 0 0 1.95 2.92" />
      <path d="M8.56 20.31a9 9 0 0 0 3.44 .69" />
      <path d="M15.44 20.31a9 9 0 0 0 2.92 -1.95" />
      <path d="M20.31 15.44a9 9 0 0 0 .69 -3.44" />
      <path d="M20.31 8.56a9 9 0 0 0 -1.95 -2.92" />
      <path d="M15.44 3.69a9 9 0 0 0 -3.44 -.69" />
      <path d="M9 12l2 2l4 -4" />
    </svg>
    <div class="prose">
      <h2 class="text-gray-700">Transfer Initiated</h2>
    </div>

    <div class="shadow-lg w-2/5 rounded bg-white text-center px-4 py-6">
      <p>
        Ticket Transfer has been initiated. <br /><br />
        An email has been sent to the ticket holder.
        <br />
        On approval, the ticket will be transferred to the new owner.
        <br/>
        <br/>
        For further assistance, send an email to <a class="underline" href="mailto:team@fossunited.org">team@fossunited.org</a>
      </p>
    </div>
  </div>
</template>
<script setup></script>
