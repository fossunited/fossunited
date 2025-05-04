export const getStatusBadgeTheme = (status) => {
  switch (status) {
    case 'Accepted':
      return 'green'
    case 'Not Yet Decided':
      return 'orange'
    case 'Declined':
      return 'red'
    default:
      return 'gray'
  }
}

export const defaultSelectedReviewValue = () => {
  return {
    remarks: '',
    to_approve: 'Yes',
  }
}
