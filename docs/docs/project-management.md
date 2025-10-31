# Project Management

Work on the Platform is planned and executed using a [GitHub project](https://github.com/orgs/fossunited/projects/3)
at the moment and known issues about the project are tracked using the GitHub
[issues board](https://github.com/fossunited/fossunited/issues/).

This is more or less reflected in [Changelog.md](changelog.md) in text format explaining the changes as monthly tech report from FOSS united foundation and platform. Updates are also be communicated in [blog](https://fossunited.org/blog/tech-report) and [forum post](https://forum.fossunited.org/t/foss-united-monthly-tech-report/) to keep the community informed.

The GitHub issues board organizes work in a clear workflow:

- Issues that the Foundation is actively working on are placed in the "ToDo" column.
- Issues planned for future prioritization, such as the next month, are placed in the "No Status" column.
- When an issue is picked up for work, it is moved to the "In Progress" column and assigned to the responsible contributor.
- Issues are typically closed automatically by GitHub when a Pull Request addressing them is merged, at which point they are moved to the "Done" column.
- At the start of each month, a new column is created for the previous month, and all issues from the "Done" column are manually moved into it to maintain historical records.

Our project dashboard follows a monthly archival pattern, moving closed issues to their respective month columns:

- October 25
- September 25

Apart from documentation, another way to get involved with the project is with
Project Management. For example, we need users of the Platform to discover and
report bugs in the project. We need volunteers to report on the issue
board and respond to new issues from the Community. Reproducing issues or
responding to the issues with request for additional information to aid in
reproduction of the issue are incredibly valuable ways to contribute to the
project.


## Commit Practice

We recommend using commit prefixes to make changes clear at a glance. Each commit should include a description explaining the intention and context of the change to support future development and historical reference.

- `:doctype` - changes related to frappe doctype and their rationale
- `:backend` - backend code modifications supplying data to the site
- `:frontend` - changes to web pages and user interface
- `:fix` - corrections for broken functionality, referencing the cause
- `:minor` - minor or maintenance updates with no functional impact
- `:init` - initial setup or boilerplate for new features
- `:feat` - completed feature implementations
- `:test` - updates or additions to unit tests
- `:dashboard` - modifications to dashboard components
