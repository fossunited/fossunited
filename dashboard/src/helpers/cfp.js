import { ref } from 'vue'
import { isValidUrl } from './utils'

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
      label: 'Is this your first talk?',
      fieldname: 'is_first_talk',
      fieldtype: 'radio_group',
      options: [
        { label: 'Yes', value: 'Yes' },
        { label: 'No', value: 'No' },
      ],
      value: '',
      description: 'Please select Yes if this is your first talk.',
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
  ])

  let customFields = getCustomQuestions(cfpData.cfp_custom_questions)

  baseFields.value.push(...customFields)

  return baseFields
}

const getSessionTypeOptions = (only_workshops, only_talk_proposals) => {
  let options = [
    { label: 'Talk', value: 'Talk', description: '(Upto 45 mins)' },
    { label: 'Lightning Talk', value: 'Lightning Talk', description: '(Upto 15 mins)' },
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

const getCustomQuestions = (questions) => {
  return questions.map((question, index) => {
    return {
      label: question.question,
      fieldname: 'custom_question_' + index,
      fieldtype: question.type,
      options: question.options && question.options.split('\n'),
      required: question.is_mandatory,
      value: '',
      description: question.description,
    }
  })
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
      label: 'Speaker Bio',
      fieldname: 'bio',
      fieldtype: 'text_editor',
      value: '',
      required: true,
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

    if (!isValidUrl(item.link)) {
      errors.push(`Reference #${index + 1} link is invalid`)
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
