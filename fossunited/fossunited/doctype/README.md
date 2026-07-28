# doctype

DocTypes for the `fossunited` app, following standard Frappe conventions.
Each subfolder is one DocType - its schema/permissions live in the `.json`,
and its logic lives in the `.py` controller (plus `__init__.py`, which
Frappe needs to treat it as a module).

Some doctypes also have:
- a `.js` file, for client-side form behaviour
- a `test_*.py`, for unit tests
- a `templates/` folder, for doctypes rendered on the website

New doctypes should be added via `bench`, not created by hand, so the
generated files stay consistent with the rest here.
