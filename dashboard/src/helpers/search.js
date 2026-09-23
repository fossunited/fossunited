/**
 * Order-independent ("haystack") text search.
 *
 * The query is split into whitespace-separated tokens and every token must
 * appear somewhere in the haystack, in any order. So "malan david" matches a
 * speaker named "David Malan", and "malan keynote" matches a talk titled
 * "Keynote" by "David Malan" even though the words live in different fields.
 *
 * Tokens never contain whitespace, so joining the fields with a space keeps
 * them from matching across a field boundary.
 */

export function tokenizeQuery(query) {
  return String(query ?? '')
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
}

export function buildHaystack(parts) {
  return parts
    .flat(Infinity)
    .filter(Boolean)
    .map((part) => String(part).toLowerCase())
    .join(' ')
}

/**
 * @param {Array} parts  fields to search across (nested arrays are flattened,
 *                       falsy entries dropped)
 * @param {string|string[]} query  raw query string, or pre-tokenized tokens
 * @returns {boolean}  true when every token is found; an empty query matches
 */
export function matchesQuery(parts, query) {
  const tokens = Array.isArray(query) ? query : tokenizeQuery(query)
  if (!tokens.length) return true

  const haystack = buildHaystack(parts)
  return tokens.every((token) => haystack.includes(token))
}
