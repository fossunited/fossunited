import dayjs from 'dayjs'

// Plugins
import customParseFormat from 'dayjs/plugin/customParseFormat'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import relativeTime from 'dayjs/plugin/relativeTime'
import isToday from 'dayjs/plugin/isToday'
import isYesterday from 'dayjs/plugin/isYesterday'

// Register plugins once
dayjs.extend(customParseFormat)
dayjs.extend(advancedFormat)
dayjs.extend(relativeTime)
dayjs.extend(isToday)
dayjs.extend(isYesterday)

/**
 * "2025-12-29" -> "29th December, 2025"
 */
export const getFormattedEventDate = (start_date, end_date = null) => {
  const startDate = dayjs(start_date, 'YYYY-MM-DD')
  const endDate = end_date ? dayjs(end_date, 'YYYY-MM-DD') : startDate

  const startDay = startDate.format('Do')
  const startMonthYear = startDate.format('MMMM, YYYY')

  if (startDate.isSame(endDate, 'day')) {
    return `${startDay} ${startMonthYear}`
  }

  const endDay = endDate.format('Do')
  return `${startDay} - ${endDay} ${startMonthYear}`
}

/**
 * "2025-12-29T14:30:45" -> "02:30 PM"
 */
export const getFormattedTime = (datetime) => {
  if (!datetime) return ''
  return dayjs(datetime).format('hh:mm A')
}

/**
 * "2025-12-29" -> "Monday, December 29, 2025"
 */
export const formatFullDate = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('dddd, MMMM D, YYYY')
}

/**
 * "2025-12-29T14:30:45" -> "02:30:45 PM"
 */
export const formatTimeOnly = (datetime) => {
  if (!datetime) return ''
  return dayjs(datetime).format('hh:mm:ss A')
}

/**
 * "2025-12-29T14:30:45" -> "29 Dec, 02:30 PM"
 */
export const formatCheckinDateTime = (datetime) => {
  if (!datetime) return ''
  return dayjs(datetime).format('DD MMM, hh:mm A')
}

/**
 * Relative label for check-ins
 */
export const getRelativeTime = (datetime) => {
  if (!datetime) return ''
  const date = dayjs(datetime)

  if (date.isToday()) return 'Today'
  if (date.isYesterday()) return 'Yesterday'
  return date.fromNow()
}

/**
 * Predicate helper
 */
export const isCheckedInToday = (attendee) =>
  attendee?.checkin_data?.some((d) => dayjs(d.check_in_time).isToday()) || false

// default export for raw dayjs
export default dayjs
