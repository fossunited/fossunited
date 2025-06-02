<template>
  <NestedPopover>
    <template #target>
      <Button label="Filter" variant="outline">
        <template #prefix>
          <IconFilter2 class="w-4 h-4" />
        </template>
        <template #suffix>
          <Badge v-if="filters.length" :label="filters.length" variant="subtle"></Badge>
        </template>
      </Button>
    </template>
    <template #body>
      <div class="my-2 rounded-lg border border-gray-100 bg-surface-white shadow-xl">
        <div class="min-w-[400px] p-2">
          <div v-if="filters.length">
            <div
              v-for="(filter, i) in filters"
              id="filter-list"
              :key="i"
              class="mb-3 flex items-center justify-between gap-2"
            >
              <div class="flex flex-1 items-center gap-2">
                <div class="w-13 flex-shrink-0 pl-2 text-end text-base text-ink-gray-5">
                  {{ i == 0 ? 'Where' : 'And' }}
                </div>
                <div id="fieldname" class="!min-w-[140px] flex-1">
                  <Autocomplete
                    v-model="filters[i].field"
                    :options="fields"
                    @update:model-value="editFilter(filter, i, $event)"
                  >
                  </Autocomplete>
                </div>
                <div id="operator" class="!min-w-[140px] flex-shrink-0">
                  <FormControl
                    v-model="model[filter.fieldname][0]"
                    type="select"
                    :model-value="filter.operator"
                    :options="getOperators(filter.field.fieldtype)"
                    placeholder="Operator"
                  />
                </div>
                <div id="value" class="!min-w-[140px] flex-1">
                  <SearchComplete
                    v-if="
                      typeLink.includes(filter.field.fieldtype) &&
                      ['=', '!='].includes(filter.operator)
                    "
                    v-model="model[filter.fieldname][1]"
                    :doctype="filter.field.options"
                    :value="filter.value"
                    placeholder="Value"
                  />
                  <component
                    :is="getValueSelector(filter.field.fieldtype, filter.field.options)"
                    v-else
                    v-model="model[filter.fieldname][1]"
                    placeholder="Value"
                  />
                </div>
              </div>
              <div class="flex-shrink-0">
                <Button variant="ghost" icon="x" @click="removeFilter(i)" />
              </div>
            </div>
          </div>
          <div v-else class="mb-3 flex h-7 items-center px-3 text-sm text-ink-gray-5">
            Empty - Choose a field to filter by
          </div>
          <div class="flex items-center justify-between gap-2">
            <Autocomplete
              v-model="newFilter"
              value=""
              :options="fields"
              placeholder="Filter by..."
              @change="(field) => addFilter(field.value)"
            >
              <template #target="{ togglePopover }">
                <Button
                  class="!text-ink-gray-5"
                  variant="ghost"
                  label="Add filter"
                  @click="togglePopover()"
                >
                  <template #prefix>
                    <FeatherIcon name="plus" class="h-4" />
                  </template>
                </Button>
              </template>
            </Autocomplete>
            <Button
              v-if="filters.length"
              class="!text-ink-gray-5"
              variant="ghost"
              label="Clear all filter"
              @click="model = []"
            />
          </div>
        </div>
      </div>
    </template>
  </NestedPopover>
</template>

<script setup>
import { Autocomplete, Badge, FeatherIcon, FormControl } from 'frappe-ui'
import { computed, h, ref, watch } from 'vue'
import NestedPopover from './NestedPopover.vue'
import SearchComplete from './SearchComplete.vue'
import { IconFilter2 } from '@tabler/icons-vue'

const typeCheck = ['Check']
const typeLink = ['Link']
const typeNumber = ['Float', 'Int']
const typeSelect = ['Select', 'Radio Group']
const typeString = ['Data', 'Long Text', 'Small Text', 'Text Editor', 'Text', 'JSON', 'Code']

const model = defineModel({
  type: Object,
  required: true,
})
const props = defineProps({
  docfields: {
    type: Array,
    default: () => [],
  },
})

const newFilter = ref({})

watch(
  () => newFilter.value,
  () => {
    if (!newFilter.value) {
      return
    }
    addFilter(newFilter.value.fieldname)
    newFilter.value = null
  },
)

const fields = computed(() => {
  const fields = props.docfields
    .filter((field) => {
      return (
        !field.is_virtual &&
        (typeCheck.includes(field.fieldtype) ||
          typeLink.includes(field.fieldtype) ||
          typeNumber.includes(field.fieldtype) ||
          typeSelect.includes(field.fieldtype) ||
          typeString.includes(field.fieldtype))
      )
    })
    .map((field) => {
      return {
        label: field.label,
        value: field.fieldname,
        description: field.fieldtype,
        ...field,
      }
    })
  return fields
})

const filters = computed(() => {
  const filtersDict = model.value
  return makeFiltersList(filtersDict)
})

function makeFiltersList(filtersDict) {
  if (!filtersDict) return []
  return Object.entries(filtersDict).map(([fieldname, [operator, value]]) => {
    const field = getField(fieldname)
    return {
      fieldname,
      operator,
      value,
      field,
    }
  })
}

function getField(fieldname) {
  return fields.value.find((f) => f.fieldname === fieldname)
}

function makeFiltersDict(filtersList) {
  return filtersList.reduce((acc, filter) => {
    const { fieldname, operator, value } = filter
    acc[fieldname] = [operator, value]
    return acc
  }, {})
}

function getOperators(fieldtype) {
  let options = []
  if (typeString.includes(fieldtype) || typeLink.includes(fieldtype)) {
    options.push(
      ...[
        { label: 'Equals', value: '=' },
        { label: 'Not Equals', value: '!=' },
        { label: 'Like', value: 'like' },
        { label: 'Not Like', value: 'not like' },
      ],
    )
  }
  if (typeNumber.includes(fieldtype)) {
    options.push(
      ...[
        { label: '<', value: '<' },
        { label: '>', value: '>' },
        { label: '<=', value: '<=' },
        { label: '>=', value: '>=' },
        { label: 'Equals', value: '=' },
        { label: 'Not Equals', value: '!=' },
      ],
    )
  }
  if (typeSelect.includes(fieldtype)) {
    options.push(
      ...[
        { label: 'Equals', value: '=' },
        { label: 'Not Equals', value: '!=' },
      ],
    )
  }
  if (typeCheck.includes(fieldtype)) {
    options.push(...[{ label: 'Equals', value: '=' }])
  }
  return options
}

function getDefaultOperator(fieldtype) {
  if (
    typeSelect.includes(fieldtype) ||
    typeLink.includes(fieldtype) ||
    typeCheck.includes(fieldtype) ||
    typeNumber.includes(fieldtype)
  ) {
    return '='
  }
  return 'like'
}

function getValueSelector(fieldtype, options) {
  if (typeSelect.includes(fieldtype) || typeCheck.includes(fieldtype)) {
    const _options = fieldtype == 'Check' ? ['Yes', 'No'] : getSelectOptions(options)
    return h(FormControl, {
      type: 'select',
      options: _options,
    })
  } else {
    return h(FormControl, { type: 'text' })
  }
}

function getDefaultValue(field) {
  if (typeSelect.includes(field.fieldtype)) {
    return getSelectOptions(field.options)[0]
  }
  if (typeCheck.includes(field.fieldtype)) {
    return 'Yes'
  }
  return ''
}

function getSelectOptions(options) {
  return options.split('\n')
}

function addFilter(fieldname) {
  const field = getField(fieldname)

  const filter = {
    fieldname,
    operator: getDefaultOperator(field.fieldtype),
    value: getDefaultValue(field),
    field,
  }
  model.value = {
    ...model.value,
    [filter.fieldname]: [filter.operator, filter.value],
  }
}

function removeFilter(index) {
  const fieldname = Object.keys(model.value)[index]
  delete model.value[fieldname]
}

function editFilter(filter, index, field) {
  const filtersList = makeFiltersList(model.value)
  filtersList.splice(index, 1, {
    fieldname: field.fieldname,
    operator: getDefaultOperator(field.fieldtype),
    value: getDefaultValue(field),
    field,
  })
  model.value = makeFiltersDict(filtersList)
}
</script>
