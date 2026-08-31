export const getTicketQrUrl = (ticketId) =>
  `/api/method/fossunited.api.tickets.get_ticket_qr?ticket_id=${encodeURIComponent(ticketId)}`

export const getTicketDownloadUrl = (ticketId) =>
  `/api/method/fossunited.api.tickets.download_ticket?ticket_id=${encodeURIComponent(ticketId)}`

/** Single ticket downloads via download_ticket; multiple get bundled into one PDF. */
export const getTicketsDownloadUrl = (ticketIds) =>
  ticketIds.length === 1
    ? getTicketDownloadUrl(ticketIds[0])
    : `/api/method/fossunited.api.tickets.download_all_tickets?ticket_ids=${encodeURIComponent(
        JSON.stringify(ticketIds),
      )}`

export const getTicketIcsUrl = (eventId) =>
  `/api/method/fossunited.api.chapter.generate_ics?event_ids=${encodeURIComponent(
    JSON.stringify([eventId]),
  )}&download=1`

export const getTicketEventUrl = (ticket) =>
  ticket.has_external_webpage
    ? ticket.external_event_url
    : window.location.origin + '/' + ticket.route

/**
 * T-shirt chip state for a ticket: collected (green, filled), ordered and
 * event still upcoming (green, border only), or ordered but never collected
 * and the event has already concluded (red, border only).
 */
export const getTshirtState = (ticket) => {
  if (ticket.tshirt_delivered) {
    return {
      tooltip: 'Collected',
      class: 'bg-surface-green-2 text-ink-green-4 border-transparent',
    }
  }
  if (ticket.is_concluded) {
    return {
      tooltip: 'Not collected',
      class: 'bg-transparent text-ink-red-4 border-outline-red-3',
    }
  }
  return {
    tooltip: 'Not collected yet',
    class: 'bg-transparent text-ink-green-4 border-outline-green-3',
  }
}
