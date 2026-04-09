import { ref } from 'vue'
import { isValidUrl, truncateStr } from './utils'
import { createResource } from 'frappe-ui'

export const getProposalFormFields = (cfpData) => {
  const baseFields = ref([
    {
      label: 'Title',
      fieldname: 'talk_title',
      fieldtype: 'text',
      required: true,
      value: '',
    },
    {
      label: 'Session Type',
      fieldname: 'session_type',
      fieldtype: 'radio_group',
      options: getSessionTypeOptions(cfpData.only_workshops, cfpData.only_talk_proposals),
      required: true,
      value: '',
    },
    {
      label: 'Session Category',
      fieldname: 'session_categories',
      fieldtype: 'multiselect',
      options: getSessionCategoryOptions(),
      required: true,
      value: [],
    },
    {
      label: 'Other Category',
      fieldname: 'other_category',
      fieldtype: 'textarea',
      required: false,
      value: '',
      description: 'Press Enter ⏎ after each category.',
    },
    {
      label: 'Is this your first talk?',
      fieldname: 'is_first_talk',
      fieldtype: 'radio_group',
      options: [
        { label: 'Yes', value: 'Yes' },
        { label: 'No', value: 'No' },
      ],
      required: true,
      value: '',
      description: 'Please select Yes if this is your first talk (ever!)',
    },
    {
      label: 'Intended Audience',
      fieldname: 'intended_audience',
      fieldtype: 'radio_group',
      options: [
        { label: 'Beginner', value: 'Beginner' },
        { label: 'Intermediate', value: 'Intermediate' },
        { label: 'Advanced', value: 'Advanced' },
      ],
      required: true,
      value: '',
    },
    {
      label: 'Proposal Description',
      fieldname: 'talk_description',
      fieldtype: 'text_editor',
      required: true,
      value: '',
    },
    {
      label: 'Key Takeaways from this talk',
      fieldname: 'key_takeaways',
      fieldtype: 'text_editor',
      value: '',
    },
    {
      label: 'License',
      fieldname: 'talk_license',
      fieldtype: 'text',
      value: '',
      description:
        'Specify the license(s) under which your project/talk is distributed. Examples: MIT License (software), CC BY-SA 4.0 (open data/documentation), CERN OHL-W (open hardware). Refer: https://opensource.org/licenses',
    },
  ])

  let customFields = getCustomQuestions(cfpData.cfp_custom_questions)
  const order = [
    'talk_title',
    'session_type',
    'session_categories',
    'other_category',
    'intended_audience',
    'talk_license',
    'talk_description',
    'key_takeaways',
    'is_first_talk',
  ]

  baseFields.value.sort((a, b) => order.indexOf(a.fieldname) - order.indexOf(b.fieldname))
  const titleIdx = baseFields.value.findIndex((f) => f.fieldname === 'talk_title')
  baseFields.value.splice(titleIdx + 1, 0, ...customFields)

  return baseFields
}

const getSessionTypeOptions = (only_workshops, only_talk_proposals) => {
  let options = [
    { label: 'Talk', value: 'Talk', description: '25-30 mins' },
    { label: 'Lightning Talk', value: 'Lightning Talk', description: 'Upto 15 mins' },
    {
      label: 'Birds of Feather(BoF)',
      value: 'Birds of Feather(BoF)',
      help: 'Birds of a Feather sessions (or BoFs) are informal gatherings of like-minded individuals who wish to discuss a certain topic without a pre-planned agenda',
    },
    { label: 'Panel Discussion', value: 'Panel Discussion' },
    { label: 'Workshop', value: 'Workshop' },
  ]
  if (only_workshops) {
    return [{ label: 'Workshop', value: 'Workshop' }]
  }

  if (only_talk_proposals) {
    return options.filter((option) => option.value !== 'Workshop')
  }

  return options
}

const getSessionCategoryOptions = () => {
  return [
    {
      value: 'Introducing a FOSS project or a new version of a popular project',
      label: 'Introducing a FOSS project or a new version of a popular project',
    },
    { value: 'Tutorial about using a FOSS project', label: 'Tutorial about using a FOSS project' },
    { value: 'Contributing to FOSS', label: 'Contributing to FOSS' },
    { value: 'Technology architecture', label: 'Technology architecture' },
    {
      value: 'Engineering practice - productivity, debugging',
      label: 'Engineering practice - productivity, debugging',
    },
    { value: 'Community', label: 'Community' },
    { value: 'Technology / FOSS licenses, policy', label: 'Technology / FOSS licenses, policy' },
    {
      value: 'Story of a FOSS project - from inception to growth',
      label: 'Story of a FOSS project - from inception to growth',
    },
    {
      value: 'Knowledge Commons (Open Hardware, Open Science, Open Data etc.)',
      label: 'Knowledge Commons (Open Hardware, Open Science, Open Data etc.)',
    },
    { value: 'Other', label: 'Other' },
  ]
}

const getCustomQuestions = (questions) => {
  return questions.map((question, index) => {
    return {
      label: question.question,
      fieldname: 'custom_question_' + index,
      fieldtype: getQuestionType(question.type),
      options: question.options && question.options.split('\n'),
      required: question.is_mandatory,
      value: '',
      description: question.description,
    }
  })
}

const getQuestionType = (type) => {
  switch (type) {
    case 'Data':
      return 'text'
    case 'Select':
      return 'select'
    case 'Long Text':
      return 'textarea'
    case 'Text Editor':
      return 'text_editor'
    case 'Check':
      return 'checkbox'
    case 'Radio Group':
      return 'radio_group'
    default:
      return 'text'
  }
}

export const getReferenceItemSchema = () => {
  return {
    link: '',
  }
}

export const getSpeakerSchema = () => {
  return {
    photo: '',
    full_name: '',
    email: '',
    designation: '',
    organization: '',
    social_link: '',
    bio: '',
  }
}

export const getSpeakerFields = () => {
  return [
    {
      label: 'Speaker Image',
      fieldname: 'photo',
      value: '',
      fieldtype: 'attach_image',
      required: true,
    },
    {
      label: 'Full Name',
      fieldname: 'full_name',
      value: '',
      fieldtype: 'text',
      required: true,
    },
    {
      label: 'Email',
      fieldname: 'email',
      value: '',
      fieldtype: 'email',
      required: true,
    },
    {
      label: 'Designation',
      fieldname: 'designation',
      value: '',
      fieldtype: 'text',
      required: true,
    },
    {
      label: 'Organization',
      fieldname: 'organization',
      value: '',
      fieldtype: 'text',
    },
    {
      label: 'Social Link',
      fieldname: 'social_link',
      fieldtype: 'url',
      value: '',
    },
    {
      label: 'Contact Info',
      fieldname: 'contact_info',
      fieldtype: 'text',
      value: '',
      description: 'Phone number or signal handle for volunteers to reach out.',
    },
    {
      label: 'Speaker Bio',
      fieldname: 'bio',
      fieldtype: 'text_editor',
      value: '',
      required: true,
    },
  ]
}

export const getSubmissionConfirmationFields = () => {
  return [
    {
      label: 'I have gone through the proposal guidelines before submitting the proposal',
      fieldname: 'proposal_guidelines_ack',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
    {
      label: 'I wrote this myself, it was NOT generated primarily by AI',
      fieldname: 'authorship_ack',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
    {
      label: 'I have included relevant references to provide as much context as possible',
      fieldname: 'references_ack',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
    {
      label: 'I can do a mock presentation of this talk if required',
      fieldname: 'mock_presentation_ack',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
    {
      label:
        'I agree that my talk, slides, and related materials will be published under a Creative Commons (CC BY-SA 4.0) license if my proposal is accepted.',
      fieldname: 'license_ack',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
    {
      fieldname: 'accept_coc',
      fieldtype: 'checkbox',
      required: true,
      value: false,
    },
  ]
}

export const validateRequiredFields = (fields) => {
  const errors = []

  fields.forEach((field) => {
    if (field.required && !field.value) {
      errors.push(`${field.label} is required`)
    }
  })

  return errors
}

export const validateReferences = (references) => {
  const errors = []

  references.forEach((item, index) => {
    if (!item.link) {
      if (references.length == 1) {
        errors.push('Atleast one reference is required')
        return errors
      }
      errors.push(`Reference #${index + 1} is missing a link`)
    }

    const short_url = truncateStr(item.link, 20)
    if (!isValidUrl(item.link)) {
      errors.push(
        `Reference #${index + 1} (${short_url}) link is invalid. Only https links are allowed.`,
      )
    }
    if (item.link.length > 250) {
      errors.push(
        `Reference #${index + 1} (${short_url}) link is longer than 250 characters. Please use URL shortner or add clean links.`,
      )
    }
  })

  return errors
}

export const validateSpeakerFields = (speakers) => {
  const errors = []

  speakers.forEach((fields, index) => {
    const fieldErrors = validateRequiredFields(fields) // Returns an array of errors

    if (fieldErrors.length) {
      // Merge all errors properly with a newline separator
      errors.push(`Speaker #${index + 1}:\n${fieldErrors.join('\n')}`)
    }
  })

  return errors
}

const getTransformedProposalFields = (proposalFields) => {
  const transformedFields = {}
  const customAnswers = []

  proposalFields.forEach((field) => {
    if (field.fieldname.startsWith('custom_question')) {
      customAnswers.push({
        question: field.label,
        type: field.fieldtype,
        response: field.value,
      })
    } else if (field.fieldname == 'session_categories') {
      let categories = field.value.join('\n')
      transformedFields['session_categories'] = categories
    } else {
      transformedFields[field.fieldname] = field.value
    }
  })

  transformedFields['custom_answers'] = customAnswers

  return transformedFields
}

const getTransformedReferenceItems = (referenceItems) => {
  const transformedReferences = []

  referenceItems.forEach((item) => {
    transformedReferences.push({
      link: item.link,
    })
  })

  return {
    references: transformedReferences,
  }
}

const getTransformedSpeakers = (speakers) => {
  return {
    speakers: speakers.map((speakerDetails) => {
      const speaker = getSpeakerSchema()
      speakerDetails.forEach((field) => {
        if (Object.prototype.hasOwnProperty.call(speaker, field.fieldname)) {
          speaker[field.fieldname] = field.value
        }
      })
      return speaker
    }),
  }
}

export const getTransformedSubmissionFields = (proposalFields, referenceItems, speakers) => {
  return {
    ...getTransformedProposalFields(proposalFields),
    ...getTransformedReferenceItems(referenceItems),
    ...getTransformedSpeakers(speakers),
  }
}

export const getCfpFilterFields = async (eventId) => {
  const fields = createResource({
    url: 'fossunited.api.cfp.get_proposal_filter_fields',
    makeParams() {
      return {
        event_id: eventId,
      }
    },
  })

  await fields.fetch()

  return fields
}

export const filterSubmissions = (cfpSubmissions, filters) => {
  let filteredSubmissions = [...cfpSubmissions]

  Object.entries(filters).forEach(([key, value]) => {
    const operator = value[0]
    const filterValue = value[1]

    filteredSubmissions = filteredSubmissions.filter((submission) => {
      let result
      switch (operator) {
        case 'like':
          result = submission[key]?.toLowerCase().includes(filterValue.toLowerCase())
          break
        case 'not like':
          result = !submission[key]?.toLowerCase().includes(filterValue.toLowerCase())
          break
        case '!=':
          result = submission[key] !== filterValue
          break
        case '<':
          result = submission[key] < filterValue
          break
        case '>':
          result = submission[key] > filterValue
          break
        case '<=':
          result = submission[key] <= filterValue
          break
        case '>=':
          result = submission[key] >= filterValue
          break
        default:
          result = submission[key] === filterValue
          break
      }

      return result
    })
  })

  return filteredSubmissions
}

export const statusIndicatorColor = (status) => {
  switch (status) {
    case 'Approved':
      return 'green-400'
    case 'Review Pending':
      return 'orange-400'
    case 'Rejected':
      return 'red-400'
    case 'Screening':
      return 'gray-400'
    default:
      return 'blue-400'
  }
}
