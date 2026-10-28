# Delete personal data

If you want us to delete your data that is saved on the FOSS United
Foundation systems, including Personally Identifiable Information (PII),
please submit your email address on the
[Delete Data](https://fossunited.org/request-for-account-deletion/new) page.

![Request data](./assets/delete-data.png)

## Profile anonymization

After email verification, a System Manager approves the request with **Delete
Data**. Frappe processes the request on the long background queue, disables the
account, and renames the User to a `deleted-user-…` identifier.

The profile's name, contact details, biography, location, gender, image references,
and social links are replaced with placeholders. Education, work experience, and
personal project details are redacted by their parent profile, including entries
added by an administrator. The profile and child rows remain so existing links
stay valid. The anonymized profile's `/u/<username>` page returns 404.

This is the first part of a staged rollout. It does **not** yet scrub copies of
identity data in chapter rosters, CFP speakers, tickets, hackathon records, or
payments. It also does not delete uploaded File records or historical versions.
The profile username and route remain stored, but the profile page is unavailable.
Deleting a profile directly in Desk continues to use the existing hard-delete
behavior; use a Personal Data Deletion Request for this anonymization workflow.

### Verify locally

Run the profile deletion regressions and existing profile tests:

```sh
bench --site <site> run-tests --module fossunited.tests.test_account_deletion_profile
bench --site <site> run-tests --module fossunited.foss_profiles.doctype.foss_user_profile.test_foss_user_profile
```

For a browser check, create a disposable profile, visit its public page, submit a
Personal Data Deletion Request, follow the confirmation email, and approve the
request as a System Manager. Confirm the request reaches **Deleted**, its profile
and child rows contain placeholders, another user's profile is unchanged, and the
original public profile URL returns 404.

Email delivery needs a configured outgoing Email Account. Approval also requires
a running long-queue worker; saving or verifying a request alone does not
anonymize the profile.
