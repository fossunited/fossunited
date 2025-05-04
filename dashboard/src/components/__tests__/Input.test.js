// File: src/components/__tests__/Input.test.js

import { describe, it, expect } from 'vitest'
import { render, fireEvent } from '@testing-library/vue'
import Input from '../Input.vue'

describe('Input.vue', () => {
  it('renders the label and description', () => {
    const { getByText } = render(Input, {
      props: {
        label: 'Email',
        description: 'Enter your email address'
      }
    })
    expect(getByText('Email')).toBeTruthy()
    expect(getByText('Enter your email address')).toBeTruthy()
  })

  it('shows required asterisk when required', () => {
    const { getByText } = render(Input, {
      props: {
        label: 'Name',
        required: true
      }
    })
    expect(getByText('*')).toBeTruthy()
  })

  it('updates value when user types', async () => {
    const { getByRole, emitted } = render(Input, {
      props: {
        modelValue: '',
        'onUpdate:modelValue': () => {}
      }
    })
    const input = getByRole('textbox')
    await fireEvent.update(input, 'hello')
    // The input's value should be updated
    expect(input.value).toBe('hello')
  })
})
