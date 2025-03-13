import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import advancedFormat from 'dayjs/plugin/advancedFormat'

dayjs.extend(customParseFormat)
dayjs.extend(advancedFormat)

export const getFormattedEventDate = (start_date, end_date = null) => {
  let startDate = dayjs(start_date, 'YYYY-MM-DD')
  let endDate = null

  if (end_date) {
    endDate = dayjs(end_date, 'YYYY-MM-DD')
  } else {
    endDate = startDate
  }

  const startDay = startDate.format('Do')
  const startMonthYear = startDate.format('MMMM, YYYY')

  if (startDate.isSame(endDate, 'day')) {
    return `${startDay} ${startMonthYear}`
  } else {
    const endDay = endDate.format('Do')
    return `${startDay} - ${endDay} ${startMonthYear}`
  }
}

export function getFormattedTime(datetime) {
  const time = dayjs(datetime).format('hh:mm A')
  return time
}
