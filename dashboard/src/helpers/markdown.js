import { marked } from 'marked'

// frappe-ui 1.0 dropped its `markdownToHTML` util from the public exports (the
// old `frappe-ui/src/utils/markdown` deep import no longer resolves under its
// `exports` map). This is the same implementation 0.1.x shipped, on the same
// `marked` major frappe-ui itself depends on, so output is unchanged.
// Callers still sanitize the result (DOMPurify) before `v-html` where needed.
export function markdownToHTML(text) {
  return marked.parse(text, {
    gfm: true,
    breaks: true,
    async: false,
  })
}
