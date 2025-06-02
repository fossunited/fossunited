export const getStatusBadgeTheme = (status) => {
  switch (status) {
    case 'Approved':
      return 'green'
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
