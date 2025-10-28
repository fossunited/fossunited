export const getStatusBadgeTheme = (status) => {
  switch (status) {
    case 'Yes':
    case 'Approved':
      return 'green'
    case 'No':
    case 'Review Pending':
      return 'orange'
    case 'Rejected':
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
