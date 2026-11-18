---
name: spendly-ui-designer
description: Designs and builds UI pages and components for Spendly, the Flask/Jinja personal expense tracker (JayeshAC06/spendly). Use whenever the user says "design the ___ page", "create UI for ___", "build a component for ___", or "redesign / improve ___" in a Spendly context, or asks for any Spendly screen such as dashboard, expenses list, add/edit expense form, profile, filters, charts, empty states, modals or navbar changes. Trigger even if the user doesn't say "UI", for example "make the expenses page look better" or "I need a summary card for monthly spend".
---

# Spendly UI Designer

Produce modern, clean, fintech-style UI for Spendly that looks like it was always part of the app. The existing design wins over any generic "SaaS" instinct, because a page that is prettier but different makes the product feel patched together.

## Before designing

1. **Read the current design, don't assume it.** If the repo is available, read `static/css/style.css` (all tokens live in `:root`), `templates/base.html`, and one or two templates close to what you're building (`login.html` for forms and cards, `landing.html` for sections and stat tiles). Also read `CLAUDE.md` for conventions. The live repo always wins over `references/design-system.md`, which is only a snapshot and may be stale (the app has since gained sessions and a database). If the repo isn't available, use the snapshot and say it may be out of date.
2. **If the design is still unclear, ask for screenshots** of the existing pages before guessing. One short question beats a redesign that has to be redone.
3. **Clarify only what changes the design**: which page or component, what data it shows, and any constraints. Otherwise make reasonable assumptions and state them in one line.

## Stack and what "modular components" means here

Spendly is server-rendered Flask with Jinja templates and one hand-written stylesheet. There is no React and no build step, so do not output JSX, Tailwind or npm dependencies. Instead:

- Pages extend `base.html` and fill its blocks (`title`, `head`, `content`, `scripts`).
- Reusable pieces become **Jinja macros** in `templates/_components.html` (stat card, expense row, empty state, badge) or **partials** pulled in with `{% include %}`. Use macros when the piece takes parameters, and includes when it doesn't.
- Styles go in `static/css/style.css`, appended as a new commented section that matches the file's existing section headers. Use the CSS variables, and never hardcode a colour that already has a token.
- JS is optional and small: put it in the `scripts` block or `static/js/main.js`. Prefer CSS-only solutions (details/summary, :focus-within, checkbox toggles) first.
- Backend routes are mostly placeholders. Design against **sample context data** and list the variables the template expects (for example `expenses`, `total_spent`) so the route author knows what to pass. Don't implement routes or DB code unless asked: requested UI is the deliverable, and unrequested backend code adds review work and can clash with the author's plans. Before using `url_for('...')` for a link, check the real endpoint name in `app.py`.

## Design rules

**Direction:** minimal, calm, fintech. Cards on a warm paper background, generous whitespace, one clear primary action per screen.

- **Spacing:** 8px grid. Use multiples of 0.5rem (0.5, 1, 1.5, 2, 3rem). Spacing inside a card is smaller than the gap between cards, so groups read as groups.
- **Shape:** reuse `--radius-sm` (controls, buttons), `--radius-md` (cards), `--radius-lg` (large containers, modals).
- **Depth:** the existing look is flat with 1px borders. Keep borders as the default separator. Add a soft shadow only where something floats or is interactive (dropdowns, modals, hovered cards), for example `0 4px 16px rgba(15,15,15,0.06)`. Subtle means barely visible.
- **Colour:** neutrals from the ink/paper tokens, `--accent` (deep green) for primary emphasis and positive states, `--accent-2` (amber) sparingly for highlights, `--danger` for destructive or overspend. Use the `-light` variants for tinted backgrounds. Colour must never be the only signal, so pair it with an icon or label.
- **Type:** DM Serif Display for page titles and card headings only, DM Sans for everything else. Establish hierarchy with size and weight, with at most three levels per screen. Numbers are the hero of a finance UI, so make amounts large, weighted and aligned (`font-variant-numeric: tabular-nums`).
- **Money:** format in rupees (₹) with Indian digit grouping, for example ₹1,24,500. Expenses read neutral or danger, never green. Green means income, savings or "under budget".
- **Icons:** Lucide, as inline SVG (24x24 viewBox, `stroke="currentColor"`, `stroke-width="2"`, `fill="none"`, round caps and joins), sized 16-20px beside text. Inline SVG avoids a CDN or build step. Pair every icon-only button with an `aria-label`. The brand glyph `◈` stays as is. Pick icons that carry meaning, such as a category icon next to an expense, not decoration.
- **Usability:** one primary action, labels above inputs, helpful empty states ("No expenses yet" plus a button to add one), visible focus states, 44px minimum touch targets on mobile, and error messages next to the problem in plain words.
- **Responsive:** mobile-first behaviour with the file's existing breakpoints (900px and 600px). Grids collapse to one column, tables become stacked rows, and primary buttons go full width on small screens.
- **Accessibility:** semantic elements (`nav`, `main`, `section`, `table` for tabular data, `button` vs `a` used correctly), text contrast of at least 4.5:1, and no information in colour alone.

Avoid generic or dated looks: heavy gradients, stock-dashboard purple, drop shadows on everything, mixed radii, emoji as icons, and one-off inline styles.

## Output format

Reply in this order, and keep it tight. Use this exact skeleton so the files can be copied straight into the project:

~~~~markdown
## UI structure
- **Layout:** top-to-bottom sections in a few lines.
- **UX decisions:** two or three decisions that matter, and why.
- **Context variables:** `name` (type and meaning) for each variable the template expects.

## Code

### `templates/<page>.html`
```html
{% extends "base.html" %}
...
```

### `templates/_components.html`   (only if macros are added)
```html
{% macro ... %}
```

### `static/css/style.css`   (append at the end)
```css
/* ---- <Section name> ---- */
```

### `static/js/main.js`   (only if JS is needed)
```js
```

## Notes
Assumptions, and anything that touches existing files (for example a new navbar link in `base.html`).
~~~~

Rules for the code blocks:

- Put the file path in a heading directly above each block, and tag every block with its language (`html`, `css`, `js`) so it can be copied without edits.
- Give each block the complete content for that file or section, with no `...` placeholders left in the final answer.
- Omit sections that don't apply, for example no JS heading when no JS is needed.
- Skip boilerplate that `base.html` already provides, and add no commentary between blocks beyond what a maintainer needs.

Where each kind of file goes:

| Kind | Path | Notes |
|---|---|---|
| Page | `templates/<name>.html` | Extends `base.html`, content in `{% block content %}` |
| Reusable pieces | `templates/_components.html` | Jinja macros, imported with `{% from "_components.html" import ... %}` |
| Styles | `static/css/style.css` | Append a new commented section, never edit existing rules |
| Scripts | `static/js/main.js` | Only when CSS alone can't do it |

When working in the repo itself, write the files directly instead of pasting them, then summarise what changed in a few lines.

For a visual preview when asked, render the page as a standalone HTML file that links the real `style.css`, so the preview shows the true styling.

## Redesign / improve requests

Read the current page first and name what is weak (hierarchy, density, unclear action) before changing it. Keep what already works and the existing class names where possible, so the diff is small and nothing else on the site breaks.