<template>
  <!-- Add/Edit PR/Issue Dialog -->
  <Dialog
    v-model="showAddDialog"
    class="z-50"
    :options="{
      title: editingRow ? 'Edit Issue / PR / Discussion' : 'Add Issue / PR / Discussion',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl v-model="newIssuePr.link" type="url" label="Link &ast;" />
        <FormControl v-model="newIssuePr.title" label="Title &ast;" />
        <FormControl
          v-model="newIssuePr.type"
          type="select"
          :options="issueTypes"
          label="Type &ast;"
        />
        <ErrorMessage :message="addIssueErrors" />
      </div>
    </template>
    <template #actions>
      <div class="grid w-full grid-cols-2 gap-4">
        <Button
          :label="editingRow ? 'Save' : 'Add'"
          variant="solid"
          @click="editingRow ? handleEditIssuePr() : handleAddIssuePr()"
        />
        <Button label="Cancel" theme="gray" @click="closeDialog" />
      </div>
    </template>
  </Dialog>

  <!-- Issue / PR ListView -->
  <div
    v-if="!isHackathonEnded && projectDoc.doc.issue_pr_table.length > 0"
    class="flex flex-row-reverse w-full p-2 mb-2"
  >
    <Button
      class="w-full md:w-fit"
      label="Link Issue / PR / Discussion"
      icon-left="plus"
      variant="solid"
      @click="showAddDialog = true"
    />
  </div>
  <ListView :columns="listColumns" :rows="groupedIssuePrs" :options="listOptions" row-key="name">
    <template #cell="{ item, row, column }">
      <div v-if="column.label == 'Link'">
        <a
          :href="item"
          target="_blank"
          class="text-ink-gray-9 text-base underline flex gap-1 truncate"
        >
          <span>{{ item }}</span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
      </div>
      <div v-else-if="column.key == 'actions'" class="flex gap-1">
        <Button icon="edit" size="sm" variant="subtle" @click="openEditDialog(row)" />
        <Button icon="trash" size="sm" theme="red" variant="subtle" @click="deleteIssuePr(row)" />
      </div>
      <div v-else class="text-base truncate text-wrap">{{ item }}</div>
    </template>
  </ListView>
</template>
<script setup>
import { computed, ref, watch, defineProps, defineEmits, reactive } from 'vue'
import { ErrorMessage, FormControl, ListView, Dialog, createDocumentResource } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { IconArrowUpRight } from '@tabler/icons-vue'

const props = defineProps({
  project: { type: Object, required: true },
  isHackathonEnded: { type: Boolean, default: false },
})

const emits = defineEmits(['fetch-project'])

const issueTypes = [
  { label: 'Issue', value: 'Issue' },
  { label: 'Pull Request', value: 'Pull Request' },
  { label: 'Discussion', value: 'Discussion' },
]

const newIssuePr = reactive({ title: '', link: '', type: '' })
const showAddDialog = ref(false)
const addIssueErrors = ref([])
const editingRow = ref(null)

const projectDoc = createDocumentResource({
  doctype: 'FOSS Hackathon Project',
  name: props.project.data.name,
  auto: true,
})

const listColumns = computed(() => {
  const cols = [
    { label: 'Title', key: 'title', width: '300px' },
    { label: 'Link', key: 'link' },
    { label: 'Type', key: 'type', width: '100px' },
  ]
  if (!props.isHackathonEnded) {
    cols.push({ label: '', key: 'actions', width: '100px' })
  }
  return cols
})

const listOptions = computed(() => ({
  selectable: false,
  showTooltip: true,
  resizeColumn: true,
  onRowClick: () => {},
  emptyState: {
    title: 'No issues or PRs linked to the project',
    description: props.isHackathonEnded
      ? 'The hackathon has ended.'
      : 'You can link issues and PRs to the project to keep track of them.',
    ...(!props.isHackathonEnded && {
      button: {
        label: 'Link Issue / PR / Discussion',
        variant: 'solid',
        'icon-left': 'plus',
        onClick: () => {
          showAddDialog.value = true
        },
      },
    }),
  },
}))

const GROUP_LABELS = {
  Issue: 'Issues',
  'Pull Request': 'Pull Requests',
  Discussion: 'Discussions',
}

const groupedIssuePrs = ref([])

watch(
  () => projectDoc.doc?.issue_pr_table,
  (table) => {
    if (!table) return

    // Preserve collapsed state across reloads
    const collapsed = Object.fromEntries(groupedIssuePrs.value.map((g) => [g.group, g.collapsed]))

    const groups = Object.fromEntries(
      Object.entries(GROUP_LABELS).map(([type, label]) => [
        type,
        { group: label, collapsed: collapsed[label] ?? false, rows: [] },
      ]),
    )

    table.forEach((row) => groups[row.type]?.rows.push(row))

    groupedIssuePrs.value = Object.values(groups).filter((g) => g.rows.length)
  },
  { deep: true, immediate: true },
)

const resetNewIssuePr = () => {
  newIssuePr.title = ''
  newIssuePr.link = ''
  newIssuePr.type = ''
  addIssueErrors.value = []
  editingRow.value = null
}

const closeDialog = () => {
  resetNewIssuePr()
  showAddDialog.value = false
}

const openEditDialog = (row) => {
  editingRow.value = row
  newIssuePr.title = row.title
  newIssuePr.link = row.link
  newIssuePr.type = row.type
  addIssueErrors.value = []
  showAddDialog.value = true
}

const validateIssuePr = () => {
  const errors = []
  if (!newIssuePr.link) errors.push('Link cannot be empty')
  else if (!newIssuePr.link.startsWith('https://')) errors.push('Enter a valid link')
  if (!newIssuePr.title) errors.push('Title cannot be empty')
  if (!newIssuePr.type) errors.push('Type cannot be empty')
  return errors
}

const handleAddIssuePr = async () => {
  addIssueErrors.value = validateIssuePr()
  if (addIssueErrors.value.length) return

  projectDoc.doc.issue_pr_table.push({
    title: newIssuePr.title,
    link: newIssuePr.link,
    type: newIssuePr.type,
  })

  try {
    await projectDoc.save.submit()
    await projectDoc.reload()
    toast.success('Issue / PR added')
    closeDialog()
  } catch (err) {
    addIssueErrors.value = err.messages || [err.message]
  }
}

const handleEditIssuePr = async () => {
  addIssueErrors.value = validateIssuePr()
  if (addIssueErrors.value.length) return

  const row = projectDoc.doc.issue_pr_table.find((r) => r.name === editingRow.value.name)
  if (row) {
    row.title = newIssuePr.title
    row.link = newIssuePr.link
    row.type = newIssuePr.type
  }

  try {
    await projectDoc.save.submit()
    await projectDoc.reload()
    toast.success('Issue / PR updated')
    closeDialog()
  } catch (err) {
    addIssueErrors.value = err.messages || [err.message]
  }
}

const deleteIssuePr = (row) => {
  projectDoc.doc.issue_pr_table = projectDoc.doc.issue_pr_table.filter((r) => r.name !== row.name)
  projectDoc.save
    .submit()
    .then(() => toast.success(`Deleted the ${row.type}`))
    .catch((err) => showError(err, `Failed to delete item.`))
}
</script>
