import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createApp, defineComponent, h, nextTick } from 'vue'

import { setConfig } from '../../../node_modules/frappe-ui/src/utils/config'

const boundary = vi.hoisted(() => ({ resources: [], toastError: vi.fn(), toastSuccess: vi.fn() }))
vi.mock('vue-sonner', () => ({
  toast: { error: boundary.toastError, success: boundary.toastSuccess },
}))
vi.mock('@/data/session', () => ({
  fetchSessionProfile: vi.fn(),
  sessionProfileResource: { data: { name: 'test-profile' } },
}))
vi.mock('@/components/ui/TextEditor.vue', () => ({ default: { template: '<div />' } }))
vi.mock('frappe-ui', async () => {
  const { default: FileUploader } =
    await import('../../../node_modules/frappe-ui/src/components/FileUploader/FileUploader.vue')
  return {
    FileUploader,
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
    Switch: defineComponent({ render: () => h('div') }),
    FormControl: defineComponent({ render: () => h('input') }),
    ErrorMessage: defineComponent({ render: () => h('div') }),
  }
})
import MyProfile from '../MyProfile.vue'

// The uploader, validation, FileUploadHandler, FormData and error parsing are real.
// Only the XHR transport is controlled; API resources unrelated to uploading stay mocked.
class ControlledXHR extends EventTarget {
  static DONE = 4
  static instances = []
  upload = new EventTarget()
  readyState = 0
  status = 0
  responseText = ''
  constructor() {
    super()
    ControlledXHR.instances.push(this)
  }
  open(method, url) {
    this.method = method
    this.url = url
  }
  setRequestHeader() {}
  send(data) {
    this.data = data
  }
  complete(status, body) {
    this.status = status
    this.responseText = body
    this.readyState = ControlledXHR.DONE
    this.onreadystatechange()
  }
}
let app, host
async function settle() {
  for (let i = 0; i < 8; i++) await nextTick()
}
beforeEach(async () => {
  vi.clearAllMocks()
  boundary.resources.length = 0
  ControlledXHR.instances.length = 0
  vi.stubGlobal('XMLHttpRequest', ControlledXHR)
  vi.spyOn(console, 'error').mockImplementation(() => {})
  setConfig('maxFileSize', null)
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
  await settle()
})
afterEach(() => {
  app.unmount()
  host.remove()
  setConfig('maxFileSize', null)
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})
async function selectFile(index, size = 1) {
  const input = host.querySelectorAll('input[type=file]')[index]
  Object.defineProperty(input, 'files', {
    configurable: true,
    value: [new File([new Uint8Array(size)], 'photo.jpg', { type: 'image/jpeg' })],
  })
  input.dispatchEvent(new Event('change', { bubbles: true }))
  await settle()
}
for (const [index, label] of [
  [0, 'banner'],
  [1, 'profile'],
]) {
  describe(`real ${label} FileUploader`, () => {
    for (const [event, message] of [
      ['error', 'Upload failed'],
      ['abort', 'Upload cancelled'],
    ]) {
      it(`preserves the real ${event} message without server messages`, async () => {
        const initial = boundary.resources.length
        await selectFile(index)
        const xhr = ControlledXHR.instances[0]
        expect(xhr.url).toBe('/api/method/upload_file')
        expect(xhr.data.get('file').name).toBe('photo.jpg')
        xhr.dispatchEvent(new Event(event))
        await settle()
        expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
          `Error uploading ${label} image: ${message}`,
          expect.any(Object),
        )
        expect(boundary.resources).toHaveLength(initial)
        expect(boundary.toastSuccess).not.toHaveBeenCalled()
      })
    }
    it('preserves the configured client file-size message without inventing a limit', async () => {
      setConfig('maxFileSize', 1024)
      await selectFile(index, 2048)
      expect(ControlledXHR.instances).toHaveLength(0)
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: This file is 2 KB; the limit is 1 KB.`,
        expect.any(Object),
      )
    })
    it('preserves actual parsed server validation messages', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(
        417,
        JSON.stringify({
          _server_messages: JSON.stringify([
            JSON.stringify({ message: 'Image rejected by server' }),
          ]),
        }),
      )
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: Image rejected by server`,
        expect.any(Object),
      )
    })
    it('uses the uploader fallback for malformed server bodies', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(500, '<html>upstream failure</html>')
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: Something went wrong. Please try again in a bit.`,
        expect.any(Object),
      )
      expect(boundary.toastError.mock.calls[0][0]).not.toContain('html')
    })
    it('preserves a server message when structured server messages are absent', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(
        417,
        JSON.stringify({ message: 'Images must be square' }),
      )
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: Images must be square`,
        expect.any(Object),
      )
    })
    it('handles malformed nested server messages without displaying their payload', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(500, JSON.stringify({ _server_messages: 'not JSON' }))
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: Something went wrong. Please try again in a bit.`,
        expect.any(Object),
      )
    })
    it('does not invent a numeric limit for an unconfigured 413 response', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(413, '')
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: File size exceeds the maximum allowed limit`,
        expect.any(Object),
      )
    })
    it('retains status handling for an unauthorized upload', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(401, '{}')
      await settle()
      expect(boundary.toastError).toHaveBeenCalledExactlyOnceWith(
        `Error uploading ${label} image: Please log in to continue.`,
        expect.any(Object),
      )
    })
    it('passes the real successful upload to the image update resource', async () => {
      await selectFile(index)
      ControlledXHR.instances[0].complete(
        200,
        JSON.stringify({ message: { file_url: '/files/photo.jpg' } }),
      )
      await settle()
      const resource = boundary.resources.at(-1)
      expect(resource.url).toBe(
        `fossunited.api.profile.${index === 0 ? 'set_cover_image' : 'set_profile_image'}`,
      )
      expect(resource.makeParams()).toEqual({ file_url: '/files/photo.jpg' })
      resource.onSuccess()
      expect(boundary.toastSuccess).toHaveBeenCalledExactlyOnceWith(
        index === 0 ? 'Banner Image Updated' : 'Profile Image Updated',
      )
      expect(boundary.toastError).not.toHaveBeenCalled()
    })
  })
}
