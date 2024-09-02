import frappe

from fossunited.fossunited.utils import get_doc_likes


@frappe.whitelist(allow_guest=True)
def get_likes(proposals) -> dict:
    """
    Get proposal like count for a given list of proposals

    Args:
        proposals (list): The list of proposal ids
    Returns:
        dict: with proposal id as key and count of likes as values
    """

    proposalLikes = dict()

    for proposal in proposals:
        proposalLikes[proposal] = len(get_doc_likes("FOSS Event CFP Submission", proposal))

    return proposalLikes
