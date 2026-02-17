<script setup>
defineProps({
  label: {
    type: String,
    default: '',
  },
  value: {
    type: String,
    default: '',
  },
})
</script>
<template>
  <div class="flex items-center gap-4 text-sm">
    <div class="basis-1/5 text-ink-gray-5 flex items-center pl-0 p-2">
      <slot name="label-prefix"></slot>
      <slot name="label">
        <span> {{ label }} </span>
      </slot>
      <slot name="post-label"></slot>
    </div>
    <div class="flex items-center p-2">
      <slot>
        <span>
          {{ value }}
        </span>
      </slot>
      <slot name="post-value"></slot>
    </div>
  </div>
</template>
