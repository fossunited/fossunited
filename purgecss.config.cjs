/** @type {import('purgecss').UserDefinedOptions} */
module.exports = {
  content: [
    // Jinja templates — primary source of class usage
    'fossunited/**/*.html',
    // Python controllers — classes sometimes built dynamically in get_context()
    'fossunited/**/*.py',
    // Legacy JS in templates
    'fossunited/**/*.js',
    // Vue dashboard (separate bundle, but shares some class names)
    'dashboard/src/**/*.vue',
    'dashboard/src/**/*.js',
    'dashboard/src/**/*.ts',
  ],

  css: ['fossunited/public/css/custom.css'],

  output: 'fossunited/public/css/',

  /**
   * Broad extractor: grabs every token that could be a CSS class name.
   * This is intentionally greedy — better to keep too much than delete live styles.
   * Handles: Jinja expressions, Python strings, HTML class attrs, JS strings.
   */
  defaultExtractor: (content) => content.match(/[a-zA-Z][a-zA-Z0-9_-]*/g) || [],

  safelist: {
    /**
     * Bootstrap 4 utility classes — never purge these.
     * custom.css and templates rely on Bootstrap being present.
     */
    pattern:
      /^(btn|col|row|d-|p-|m-|px-|py-|pt-|pb-|pl-|pr-|mx-|my-|mt-|mb-|ml-|mr-|w-|h-|text-|bg-|border-|flex|justify-content-|align-items-|align-self-|navbar|nav-|dropdown|modal|fade|show|active|disabled|sr-only|sr-only-focusable|font-weight-|float-|position-|overflow-|rounded|shadow|container|img-|order-|offset-)/,

    /**
     * Classes applied dynamically — purgecss can't see these statically.
     * Keep all v3- prefixed classes, event-specific (ev-) and icon (ti-) classes.
     */
    greedy: [/^v3-/, /^ev-/, /^ti /],

    /**
     * Specific classes known to be set dynamically in Python/JS
     * or used in frappe desk / web page editor contexts.
     */
    deep: [/data-theme/, /ql-/, /from-markdown/, /web-page-content/, /blog-content/],

    /**
     * Bootstrap classes that custom.css overrides for v3 dark mode theming.
     * purgecss sees these as "already provided by Bootstrap" and wrongly purges
     * the custom.css overrides — keep them explicitly.
     */
    standard: [
      'form-control',  // overrides Bootstrap input colors for dark mode (used in renderfield macro)
      'foss-form-question',  // renderfield.html macro — RSVP, CFP and all Jinja forms
      'form-divider',  // foss_event_cfp_submission.html
      'must-attend',  // timeline_base.html event badge
      'v3-card',  // agenda_card.html macro (and used widely)
    ],
  },
}
