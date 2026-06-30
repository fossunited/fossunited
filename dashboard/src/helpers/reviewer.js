const STATUS_THEMES = {
  Approved: 'green',
  Rejected: 'red',
  'Review Pending': 'orange',
  Screening: 'blue',
  Withdrawn: 'gray',
}

export const getStatusBadgeTheme = (status) => STATUS_THEMES[status] ?? 'gray'

export const defaultSelectedReviewValue = () => {
  return {
    remarks: '',
    to_approve: 'Yes',
    favourite: 0,
    private_comment: '',
  }
}
