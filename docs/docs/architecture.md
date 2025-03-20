# Architecture of the Platform

The FOSS United Platform is built using the [Frappe framework](https://frappeframework.com/).
In case you're not already aware, applications that use the Frappe framework
are built around [`DocType`s](https://frappeframework.com/docs/user/en/tutorial/create-a-doctype).
For example, the `FOSSUserProfile`, which powers the Profile, is a `DocType`.
The names of a few `DocType`s that are fundamental to the Platform can be
found in `fossunited.doctype_ids`.

If you are unfamiliar with Entity relationship diagrams or if you need a
refresher, you could refer to the wiki section on the [Crow's foot notation](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model#Crow's_foot_notation),
or this explainer from [freecodecamp](https://www.freecodecamp.org/news/crows-foot-notation-relationship-symbols-and-how-to-read-diagrams/)

## Architecture Diagram

Note: Not all features or systems in this diagram are actually used, as the diagram also includes components of what Frappe uses underneath the hood.

```mermaid
graph TD;

    U[User Browser] <--> N[nginx];
    U <--> V[VueJS Dashboard];

    Admin[Admin Browser] <--> D[Desk: SPA Custom JS];

    N <--> C[Application Server: Gunicorn & Werkzeug];

    C <--> D;
    C <--> E[Socket.io Server: Node & Redis];
    C <--> F[Jinja Templating Engine];
    C <--> G[Background Workers: Python RQ];
    C <--> H[MariaDB];
    C <--> I[Redis Cache];
    C <--> J[Amazon S3: File Storage];

    G <--> I;
    G <--> H;
```

## Entity relationships for a Chapter

```mermaid
erDiagram
  Chapter }|--o{ Profile: "has volunteer"
  Chapter }|--o{ Event : organizes
  Event }|--o{ Sponsor : has
  Event }|--o{ Profile: "organized by"
  Event }|--o{ Attendee : has
  Attendee ||--|| RSVP : has
  Event }|--o{ Proposal : contains
  Proposal }|--|{ Proposer : "submitted by"
  Proposal ||--o{ Review : has
  Review }o--o{ Reviewer : "submitted by"
```

## Entity relationships for a Hackathon

(To be completed)

## Entity relationships for a Profile

```mermaid
erDiagram
  User ||..|| Profile: "associated with"
  Profile }o--o{ Chapter : volunteers
  Chapter }|--o{ Event : organises
  Profile }o--o{ Event : attended
  Profile }|--o{ Proposal : submit
  Proposal ||--o| Talk : accepted
```
