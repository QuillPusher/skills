# Site mode: multi-page web help

Use for web help, online help or in-app help: one HTML page per topic, grouped under section hubs, with a shared sidebar.

## Working folder layout

```
<output-name>-src/
  nav.json          site structure (below)
  src/
    index.html      home page fragment (required)
    projects.html   hub fragment (optional: generated from nav.json if missing)
    projects-create.html
    ...
  media-01/ ...     images extracted by pandoc or extract_pdf.py, referenced from fragments
```

Fragment file names must match the `file` values in `nav.json`. Image paths in a fragment are relative to that fragment's folder (`src/`), for example `../media-01/media/image3.png`.

## nav.json

```json
{
  "product": "Acme",
  "headerTitle": "Acme Docs",
  "year": 2026,
  "eyebrow": "Documentation",
  "home": { "file": "index.html", "title": "Home", "appRoute": "/" },
  "sections": [
    {
      "label": "Projects",
      "file": "projects.html",
      "icon": "book",
      "desc": "Create, organise and share projects.",
      "appRoute": "/projects",
      "pages": [
        { "label": "Create a Project", "file": "projects-create.html", "icon": "plus",
          "desc": "Start a project from a template or from scratch.",
          "appRoute": "/projects/new", "appPageName": "New Project" },
        { "label": "Members", "file": "projects-members.html", "icon": "users",
          "desc": "Invite people and set their roles." }
      ]
    }
  ]
}
```

| Key | Required | Meaning |
|---|---|---|
| `product` | Yes | Product name for page titles and the footer |
| `headerTitle` | No | Header text; default "`<product>` Documentation" |
| `year` | No | Footer year; default this year |
| `eyebrow` | No | Small label above generated hub titles; default "Documentation" |
| `home` | Yes | Home page (`landing` layout). Its fragment must exist. |
| `sections[]` | Yes | One per sidebar group and hub page, in reading order |
| `sections[].icon`, `pages[].icon` | No | One of: home user users tool book clock download plus bolt chat shield check chart trend send settings file |
| `desc` | For hub tiles | One sentence shown on the hub tile (pages) or under the hub title (sections) |
| `appRoute` | No | Product URL path for in-app Help. Pages that have one go into `help-map.json`. Agree the routes with the developers. |
| `appPageName` | No | Name of the app screen in `help-map.json`; default is `label` |

## What the build adds automatically

- **Sidebar** on every page from `nav.json`, with the current page highlighted.
- **Hub pages**: if `src/<hub file>` is missing, a hub is generated with a cover (`eyebrow`, section `label`, `desc`) and one tile per page. Write the hub fragment yourself only if it needs more than that.
- **Breadcrumb** (hub › page) on topic pages, unless the fragment already has one.
- **Previous / Next** buttons in reading order (home, hub 1, its pages, hub 2, ...), unless the fragment already has a `.page-nav`. Not added to the home page.
- **Landing wrapper**: the home fragment is wrapped in `<div class="landing">` if it isn't already.
- **Images** are copied to `<output>/images/` and paths rewritten.
- **help-map.json** for every entry with an `appRoute`.

## Page fragments

- **Home** (`index.html`): copy the landing blocks from the template: `lp-hero`, then `lp-section` blocks (What's New cards in `lp-grid-3`, a walkthrough in `lp-grid-2` with `lp-steps` and an `lp-links-card`), then `lp-footer`. No `.cover`.
- **Topic page**: `.cover` with the topic `<h1>` and a one-line `.subtitle`, then one `<section>` per h2. No breadcrumb or Previous/Next needed.
- Link between pages with relative file names (`projects-members.html#roles`). The checker reports links to files that don't exist.
