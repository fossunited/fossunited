import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CopyToClipboardButton from '../CopyToClipboardButton.vue'
import { copyToClipboard } from '../../helpers/utils'


vi.mock('../../helpers/utils', () => ({
  copyToClipboard: vi.fn()
}))


vi.mock('frappe-ui', () => ({
  Tooltip: {
    template: '<div><slot /></div>',
    props: ['text'],
    setup(props) {
      return { text: props.text }
    }
  },
  Button: {
    template: '<button><slot /></button>',
    props: {
      icon: String,
      variant: String,
      class: String
    }
  }
}))

describe('CopyToClipboardButton', () => {
  it('renders correctly', () => {
    const wrapper = mount(CopyToClipboardButton, {
      props: {
        value: 'Copy this text'
      }
    })


    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)


    expect(wrapper.vm.tooltipText).toBe('Copy to clipboard')
  })

  it('shows success message after copying', async () => {

    copyToClipboard.mockResolvedValue(true)

    const wrapper = mount(CopyToClipboardButton, {
      props: {
        value: 'Copy this text'
      }
    })


    await wrapper.find('button').trigger('click')


    await wrapper.vm.$nextTick()

    expect(wrapper.vm.tooltipText).toBe('Copied!')


    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(wrapper.vm.tooltipText).toBe('Copy to clipboard')
  })

  it('handles copy failure gracefully', async () => {

    copyToClipboard.mockResolvedValue(false)

    const wrapper = mount(CopyToClipboardButton, {
      props: {
        value: 'Copy this text'
      }
    })

    // Click the button
    await wrapper.find('button').trigger('click')


    await wrapper.vm.$nextTick()

    expect(wrapper.vm.tooltipText).toBe('Copied!')
  })

  it('is accessible', () => {
    const wrapper = mount(CopyToClipboardButton, {
      props: {
        value: 'Copy this text'
      }
    })

    const button = wrapper.find('button')


    expect(button.attributes('icon')).toBe('copy')
    expect(button.attributes('variant')).toBe('ghost')
    expect(button.attributes('class')).toBe('w-4')

    expect(wrapper.vm.tooltipText).toBe('Copy to clipboard')
  })
})
