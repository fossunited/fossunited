import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createApp, defineComponent, h, nextTick } from 'vue'

const boundary = vi.hoisted(() => ({ resources: [], toastError: vi.fn(), toastSuccess: vi.fn() }))
vi.mock('vue-sonner', () => ({
  toast: { error: boundary.toastError, success: boundary.toastSuccess },
}))
vi.mock('@/data/session', async () => {
  return {
    fetchSessionProfile: vi.fn(),
    sessionProfileResource: { data: { name: 'test-profile' } },
  }
})
vi.mock('@/components/ui/TextEditor.vue', () => ({ default: { template: '<div />' } }))
vi.mock('frappe-ui', async () => {
  const { defineComponent, h } = await import('vue')
  return {
    createResource(options) {
      boundary.resources.push(options)
      return {}
    },
    createDocumentResource() {
      return {
        doc: { name: 'test-profile', full_name: 'Test User', social_links: [], projects: [] },
        get: { submit: vi.fn() },
      }
    },
    FileUploader: defineComponent({
      emits: ['success', 'failure'],
      setup(props, { emit, slots }) {
        return () =>
          h('div', { class: 'upload-boundary' }, [
            h(
              'button',
              {
                class: 'success-upload',
                onClick: () => emit('success', { file_url: '/files/test.jpg' }),
              },
              'Upload',
            ),
            h(
              'button',
              { class: 'failed-upload', onClick: () => emit('failure', 'Upload rejected') },
              'Fail upload',
            ),
            slots.default?.({ openFileSelector: () => {} }),
          ])
      },
    }),
    Switch: defineComponent({ render: () => h('div') }),
    FormControl: defineComponent({ render: () => h('input') }),
    ErrorMessage: defineComponent({ render: () => h('div') }),
  }
})
import MyProfile from '../MyProfile.vue'

let app, host
beforeEach(async () => {
  boundary.resources.length = 0
  vi.clearAllMocks()
  vi.spyOn(console, 'error').mockImplementation(() => {})
  host = document.body.appendChild(document.createElement('div'))
  app = createApp(MyProfile)
  app.component(
    'Button',
    defineComponent({
      setup:
        (_, { slots }) =>
        () =>
          h('button', slots.default?.()),
    }),
  )
  app.mount(host)
  await nextTick()
})
afterEach(() => {
  app.unmount()
  host.remove()
  vi.restoreAllMocks()
})

for (const [index, label] of [
  [0, 'banner'],
  [1, 'profile'],
]) {
  describe(`${label} image errors`, () => {
    it('shows the server validation message instead of an object or silence', async () => {
      host.querySelectorAll('.success-upload')[index].click()
      await nextTick()
      const resource = boundary.resources.at(-1)
      expect(resource.url).toBe(
        `fossunited.api.profile.${index === 0 ? 'set_cover_image' : 'set_profile_image'}`,
      )
      const error = {
        exc_type: 'ValidationError',
        messages: ['Image file size must not exceed 10 MB.'],
      }
      resource.onError?.(error)
      expect(boundary.toastError).toHaveBeenCalledWith(
        expect.stringContaining(error.messages[0]),
        expect.any(Object),
      )
      expect(boundary.toastError.mock.calls[0][0]).not.toContain('[object Object]')
      expect(boundary.toastSuccess).not.toHaveBeenCalled()
    })
    it('keeps successful updates on the success path', async () => {
      host.querySelectorAll('.success-upload')[index].click()
      await nextTick()
      boundary.resources.at(-1).onSuccess()
      expect(boundary.toastSuccess).toHaveBeenCalledWith(
        index === 0 ? 'Banner Image Updated' : 'Profile Image Updated',
      )
      expect(boundary.toastError).not.toHaveBeenCalled()
    })
    it('uses a friendly fallback for malformed server errors', async () => {
      host.querySelectorAll('.success-upload')[index].click()
      await nextTick()
      boundary.resources.at(-1).onError?.(new TypeError('technical parser failure'))
      expect(boundary.toastError).toHaveBeenCalledWith(
        expect.stringContaining('Something went wrong. Please try again in a bit.'),
        expect.any(Object),
      )
      expect(boundary.toastError.mock.calls[0][0]).not.toContain('technical parser failure')
    })
    it('shows upload transport failures hidden by the custom uploader slot', async () => {
      const initialResources = boundary.resources.length
      host.querySelectorAll('.failed-upload')[index].click()
      await nextTick()
      expect(boundary.toastError).toHaveBeenCalledWith(
        expect.stringContaining('Upload rejected'),
        expect.any(Object),
      )
      expect(boundary.resources).toHaveLength(initialResources)
    })
  })
}
