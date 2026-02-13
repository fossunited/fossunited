<template>
  <!-- Add PR/Issue Dialog -->
  <Dialog
    v-model="showAddDialog"
    class="z-50"
    :options="{
      title: 'Add Issue / PR / Discussion',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl
          v-model="newIssuePr.link"
          type="url"
          label="Link &ast;"
          @blur="getPrIssueTitle.fetch()"
        />
        <div v-if="getPrIssueTitle.loading" class="flex gap-1">
          <LoadingIndicator class="w-4 h-4" />
          <small>Fetching details...</small>
        </div>
        <div v-if="fetchTitleError">
          <small class="text-gray-700">{{ fetchTitleError }}</small>
        </div>
        <FormControl v-model="newIssuePr.title" label="Title &ast;" />
        <FormControl
          v-model="newIssuePr.type"
          type="select"
          :options="[
            {
              label: 'Issue',
              value: 'Issue',
            },
            {
              label: 'Pull Request',
              value: 'Pull Request',
            },
            {
              label: 'Discussion',
              value: 'Discussion',
            },
          ]"
          label="Type &ast;"
        />
        <ErrorMessage :message="addIssueErrors" />
      </div>
    </template>
    <template #actions>
      <div class="grid w-full grid-cols-2 gap-4">
        <Button label="Add" variant="solid" @click="handleAddIssuePr" />
        <Button
          label="Cancel"
          theme="gray"
          @click="
            () => {
              newIssuePr.title = ''
              newIssuePr.link = ''
              newIssuePr.type = ''
              showAddDialog = false
            }
          "
        />
      </div>
    </template>
  </Dialog>

  <!-- Issue / PR ListView -->
  <div
    v-if="projectDoc.doc.issue_pr_table.length > 0"
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
  <ListView
    class="h-[440px]"
    :columns="[
      {
        label: 'Title',
        key: 'title',
        width: 2 / 5,
      },
      {
        label: 'Link',
        key: 'link',
        width: 1 / 2,
      },
      {
        label: 'Type',
        key: 'type',
        width: 1 / 4,
      },
      {
        label: '',
        key: 'actions',
        width: 1 / 4,
      },
    ]"
    :rows="groupedIssuePrs"
    :options="{
      selectable: false,
      showTooltip: false,
      resizeColumn: false,
      onRowClick: (row) => {},
      emptyState: {
        title: 'No issues or PRs linked to the project',
        description: 'You can link issues and PRs to the project to keep track of them.',
        button: {
          label: 'Link Issue / PR / Discussion',
          variant: 'solid',
          'icon-left': 'plus',
          onClick: () => {
            showAddDialog = true
          },
        },
      },
    }"
    row-key="name"
  >
    <template #cell="{ item, row, column }">
      <div v-if="column.label == 'Link'">
        <a :href="item" target="_blank" class="text-gray-900 text-base underline flex gap-1">
          <span>
            {{ item }}
          </span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
      </div>
      <div v-else-if="column.key == 'actions'">
        <Button icon="trash" size="sm" theme="red" variant="subtle" @click="deleteIssuePr(row)" />
      </div>
      <div v-else class="text-base">
        {{ item }}
      </div>
    </template>
  </ListView>
</template>
<script setup>
import { computed, ref, defineProps, defineEmits, reactive } from 'vue'
import {
  ErrorMessage,
  FormControl,
  ListView,
  Dialog,
  createResource,
  createDocumentResource,
  LoadingIndicator,
} from 'frappe-ui'
import { toast } from 'vue-sonner'
import { IconArrowUpRight } from '@tabler/icons-vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits(['fetch-project'])

const newIssuePr = reactive({
  title: '',
  link: '',
  type: '',
})

const showAddDialog = ref(false)

const projectDoc = createDocumentResource({
  doctype: 'FOSS Hackathon Project',
  name: props.project.data.name,
  auto: true,
})

const groupedIssuePrs = computed(() => {
  if (!projectDoc.doc) return []

  const groups = {
    Issue: {
      group: 'Issues',
      collapsed: false,
      rows: [],
    },
    'Pull Request': {
      group: 'Pull Requests',
      collapsed: false,
      rows: [],
    },
    Discussion: {
      group: 'Discussions',
      collapsed: false,
      rows: [],
    },
  }

  projectDoc.doc.issue_pr_table.forEach((row) => {
    groups[row.type]?.rows.push(row)
  })

  return Object.values(groups).filter((g) => g.rows.length)
})

const addIssueErrors = ref([])

const validateIssuePr = () => {
  const errors = []

  if (!newIssuePr.link) {
    errors.push('Link cannot be empty')
  } else if (!newIssuePr.link.startsWith('https://')) {
    errors.push('Enter a valid link')
  }

  if (!newIssuePr.title) {
    errors.push('Title cannot be empty')
  }

  if (!newIssuePr.type) {
    errors.push('Type cannot be empty')
  }

  return errors
}

const handleAddIssuePr = async () => {
  addIssueErrors.value = validateIssuePr()

  if (addIssueErrors.value.length) {
    return
  }

  projectDoc.doc.issue_pr_table.push({
    title: newIssuePr.title,
    link: newIssuePr.link,
    type: newIssuePr.type,
  })

  try {
    await projectDoc.save.submit()
    await projectDoc.reload()

    toast.success('Issue / PR added')

    newIssuePr.title = ''
    newIssuePr.link = ''
    newIssuePr.type = ''
    addIssueErrors.value = []
    showAddDialog.value = false
  } catch (err) {
    addIssueErrors.value = err.messages || [err.message]
  }
}

const fetchTitleError = ref('')

const getPrIssueTitle = createResource({
  url: 'fossunited.api.hackathon.get_issue_pr_title',
  makeParams() {
    return {
      url: newIssuePr.link,
    }
  },
  onSuccess(data) {
    fetchTitleError.value = ''
    addIssueErrors.value = ''
    newIssuePr.title = data.title
    newIssuePr.type = data.type
  },
  onError(err) {
    newIssuePr.title = ''
    newIssuePr.type = ''
    if (err.messages[0] == 'Not a Github URL.') {
      fetchTitleError.value = 'Failed to fetch title :( \nPlease enter data manually.'
      return
    }
    addIssueErrors.value = 'Failed to fetch title : \n' + err.message
  },
})

const deleteIssuePr = (row) => {
  projectDoc.doc.issue_pr_table = projectDoc.doc.issue_pr_table.filter((r) => r.name !== row.name)

  projectDoc.save
    .submit()
    .then(() => toast.success(`Deleted the ${row.type}`))
    .catch((err) => toast.error(err.message))
}
</script>
