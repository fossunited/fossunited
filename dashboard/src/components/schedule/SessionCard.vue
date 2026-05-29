<template>
  <!-- Mobile card: two-panel stacked ──────────────────────────────────── -->
  <div class="sm:hidden flex flex-col w-full py-2">
    <!-- Top panel: time+cal overlap | speaker thumbs -->
    <div
      class="relative z-10 flex items-center justify-between bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-2xl p-2 mb-[-14px]"
    >
      <!-- Overlapping time chip + calendar button -->
      <div class="isolate flex">
        <div
          v-if="!preview"
          class="relative z-[2] h-11 w-[94px] rounded-lg bg-surface-gray-7 text-ink-white text-sm font-semibold uppercase flex items-center justify-center whitespace-nowrap px-2.5 shrink-0"
        >
          {{ formatTime(session.start_time) }}
        </div>
        <button
          class="relative z-[1] -ml-2 h-11 w-[52px] rounded-r-lg bg-surface-gray-2 dark:bg-surface-gray-3 flex items-center justify-center pl-4 pr-2.5 text-ink-gray-6 transition-colors hover:bg-surface-gray-3"
          title="Add to calendar"
          @click.stop="downloadIcs"
        >
          <IconCalendarPlus class="w-5 h-5" />
        </button>
      </div>
      <!-- YouTube (mobile) -->
      <a
        v-if="session.talk_video"
        :href="session.talk_video"
        target="_blank"
        rel="noopener noreferrer"
        class="shrink-0 w-9 h-9 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 flex items-center justify-center text-ink-gray-5 hover:text-red-500 transition-colors"
        title="Watch recording"
        @click.stop
      >
        <IconBrandYoutube class="w-4 h-4" />
      </a>
      <!-- Speaker thumbnails (up to 2) -->
      <div class="flex gap-1.5 shrink-0">
        <div
          v-for="(speaker, i) in visibleSpeakers.slice(0, 2)"
          :key="i"
          class="w-11 h-11 rounded-lg overflow-hidden border border-outline-gray-2 shrink-0"
        >
          <img
            :src="speaker.photo || ''"
            :alt="speaker.full_name || ''"
            class="w-full h-full object-cover object-top"
            loading="lazy"
            @error="(e) => (e.target.style.display = 'none')"
          />
        </div>
      </div>
    </div>

    <!-- Bottom panel: title, speakers, badges -->
    <component
      :is="cfpHref ? 'a' : 'div'"
      v-bind="cfpHref ? { href: cfpHref, target: '_blank', rel: 'noopener noreferrer' } : {}"
      class="relative z-0 bg-surface-white dark:bg-surface-gray-2 border border-outline-gray-2 rounded-b-2xl px-3 pt-[22px] pb-3 flex flex-col gap-1.5"
    >
      <h3 class="text-sm font-normal leading-snug text-ink-gray-9 line-clamp-2">
        {{ session.title }}
      </h3>
      <div class="flex flex-wrap gap-0.5">
        <span
          v-for="(speaker, i) in speakers"
          :key="i"
          class="text-xs text-ink-gray-5 pr-2.5 py-0.5 whitespace-nowrap"
        >
          {{ speaker.full_name }}
        </span>
      </div>
      <div class="flex items-center gap-1.5 flex-wrap">
        <span
          v-if="sessionDuration"
          class="h-6 px-2 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-5 text-xs font-semibold uppercase flex items-center whitespace-nowrap"
        >
          {{ sessionDuration }}
        </span>
        <span
          v-if="showCategory"
          class="rounded font-bold uppercase flex items-center justify-center whitespace-nowrap leading-[1]"
          :class="[
            categoryStyle,
            preview ? 'h-3 px-1 text-[9px] leading-[1] tracking-tight' : 'h-6 px-2 text-xs',
          ]"
        >
          {{ sessionCategory }}
        </span>
      </div>
    </component>
  </div>

  <!-- ── Desktop card: timeline layout ────────────────────────────────────── -->
  <div class="hidden sm:flex flex-col w-full py-1">
    <div class="flex items-center flex-wrap gap-y-2">
      <button
        class="flex items-center h-10 shrink-0 transition-opacity hover:opacity-80"
        title="Add to calendar"
        @click.stop="downloadIcs"
      >
        <div
          class="h-10 w-10 shrink-0 bg-surface-gray-7 rounded-l-lg flex items-center justify-center text-ink-white transition-opacity hover:opacity-80"
        >
          <IconCalendarPlus class="w-5 h-5" />
        </div>
        <div
          v-if="!preview"
          class="h-10 px-3 bg-surface-gray-7 rounded-r-lg text-ink-white text-base font-semibold uppercase flex items-center whitespace-nowrap"
          @click.stop="downloadIcs"
        >
          {{ formatTime(session.start_time) }}
        </div>
      </button>
      <!-- YouTube -->
      <a
        v-if="session.talk_video"
        :href="session.talk_video"
        target="_blank"
        rel="noopener noreferrer"
        class="ml-2 shrink-0 w-8 h-8 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 flex items-center justify-center text-ink-gray-5 hover:text-red-500 transition-colors"
        title="Watch recording"
        @click.stop
      >
        <IconBrandYoutube class="w-4 h-4" />
      </a>
      <!-- Divider line -->
      <div class="hidden md:block flex-1 border-t border-outline-gray-5 mx-3 min-w-[20px]" />
      <!-- Badges -->
      <div class="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
        <span
          v-if="sessionDuration"
          class="h-6 px-2 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-5 text-xs font-semibold uppercase flex items-center whitespace-nowrap"
        >
          {{ sessionDuration }}
        </span>
        <span
          v-if="showCategory"
          class="rounded font-bold uppercase flex items-center justify-center whitespace-nowrap leading-[1]"
          :class="[
            categoryStyle,
            preview ? 'h-3 px-1 text-[9px] leading-[1] tracking-tight' : 'h-6 px-2 text-xs',
          ]"
        >
          {{ sessionCategory }}
        </span>
        <span
          v-if="session._date"
          class="h-6 px-2 rounded-lg bg-surface-blue-2 text-ink-blue-3 text-xs font-semibold flex items-center whitespace-nowrap"
        >
          {{ formatIsoDate(session._date) }}
        </span>
        <span
          v-if="session._hall"
          class="h-6 px-2 rounded-lg bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-6 text-xs font-semibold flex items-center whitespace-nowrap"
        >
          {{ session._hall }}
        </span>
      </div>
    </div>

    <div class="flex items-stretch">
      <!-- Vertical dashed line: 40px wide, centered under calendar button -->
      <div v-if="!preview" class="w-10 shrink-0 flex justify-center py-1">
        <div class="border-l border-outline-gray-5 w-0" />
      </div>
      <!-- Content -->
      <component
        :is="cfpHref ? 'a' : 'div'"
        v-bind="cfpHref ? { href: cfpHref, target: '_blank', rel: 'noopener noreferrer' } : {}"
        class="flex flex-1 gap-4 items-start pt-2 pb-10 min-w-0 group"
        :class="cfpHref ? 'cursor-pointer' : ''"
      >
        <!-- Speaker photos 80×80 -->
        <div
          v-if="speakers.length"
          class="shrink-0 size-20 overflow-hidden rounded-lg border border-outline-gray-2 grid gap-0.5"
          :class="speakerGridClass"
        >
          <img
            v-for="(speaker, i) in visibleSpeakers"
            :key="i"
            :src="speaker.photo || ''"
            :alt="speaker.full_name || 'Speaker'"
            class="w-full h-full object-cover object-top"
            loading="lazy"
            @error="(e) => (e.target.style.display = 'none')"
          />
        </div>
        <!-- Talk details -->
        <div class="flex flex-col gap-1.5 flex-1 min-w-0">
          <h3
            class="text-base font-semibold leading-snug text-ink-gray-9"
            :class="cfpHref ? 'group-hover:underline' : ''"
          >
            {{ session.title }}
          </h3>
          <div v-if="speakers.length" class="flex flex-wrap gap-1">
            <span
              v-for="(speaker, i) in speakers"
              :key="i"
              class="px-2 py-0.5 rounded bg-surface-gray-2 dark:bg-surface-gray-3 text-ink-gray-7 text-sm font-medium whitespace-nowrap"
            >
              {{ speaker.full_name }}
            </span>
          </div>
          <p
            v-if="speakerMeta"
            class="text-xs text-ink-gray-5 line-clamp-2 leading-relaxed"
            v-html="speakerMeta"
          />
        </div>
      </component>
    </div>
  </div>
</template>

<script setup>
import { computed, toRef } from 'vue'
import { IconCalendarPlus, IconBrandYoutube } from '@tabler/icons-vue'
import dayjs from 'dayjs'
import { useSession } from '@/composables/useSession'
import { cleanedHTML } from '@/helpers/utils'

const props = defineProps({
  session: { type: Object, required: true },
  preview: { type: Boolean, default: false },
})

const {
  formatTime,
  speakers,
  visibleSpeakers,
  speakerGridClass,
  sessionDuration,
  sessionCategory,
  showCategory,
  categoryStyle,
  cfpHref,
  downloadIcs,
} = useSession(toRef(props, 'session'))

function formatIsoDate(isoDate) {
  return dayjs(isoDate).format('D MMM')
}

const speakerMeta = computed(() => {
  const s = speakers.value[0]
  if (!s) return ''
  if (s.bio) return cleanedHTML(s.bio)
  return [s.designation, s.organization].filter(Boolean).join(' · ')
})
</script>
