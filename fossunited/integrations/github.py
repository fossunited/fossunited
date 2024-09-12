
import frappe
from github import Github


class GithubHelper:
    def __init__(self):
        """
        Initialize Github object using the access token from Github Settings
        """
        try:
            github_settings = frappe.get_single("Github Settings")
            access_token = github_settings.get_password("access_token")
            self.github = Github(access_token)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Github Settings not found"))
            raise e

    def get_repo(self, repo_url):
        """
        Get the repo object from the repo url
        """
        repo = self.github.get_repo(repo_url)
        return repo

    def get_issue_info(self, repo_url, issue_number):
        """
        Get the issue object from the repo url and issue number
        """
        repo = self.get_repo(repo_url)
        issue = repo.get_issue(int(issue_number))
        return issue

    def get_pr_info(self, repo_url, pr_number):
        """
        Get the pull request object from the repo url and pr number
        """
        repo = self.get_repo(repo_url)
        pr = repo.get_pull(int(pr_number))
        return pr

    def get_discussion_info(self, repo_url, discussion_number):
        """
        Get the discussion object from the repo url and discussion number
        """
        repo = self.get_repo(repo_url)
        discussion = repo.get_issue(discussion_number)
        return discussion
