# glenberman.com

Personal academic site for Glen Berman. The live page is plain static HTML and
CSS — no JavaScript, no runtime dependencies. All the words live in one data
file (`content.json`); a small script turns that into `index.html`, and a
GitHub Action runs the script automatically on every change.

## Editing the site (adding a publication, changing text, etc.)

**You only ever edit `content.json`.** Open it on github.com, click the pencil
icon, make your change, and commit. Within a minute or so the site rebuilds and
redeploys itself — you don't run anything.

`content.json` holds the name, the intro lines, each section, and the footer.
Text fields understand a little Markdown:

- `**your name**` → **bold** (use it to bold your name in a citation)
- `*venue*` → *italic* (use it for the journal / conference name)
- `[label](https://example.com)` → a link

**To add a publication**, find the section with `"heading": "Selected
publications"` and add an entry to its `items` list, e.g.:

```json
{
  "citation": "**Berman, G.** (2025). Title of the paper. *Name of the Venue.* doi.org/...",
  "pdf": "https://link-to-the-pdf"
}
```

The `"pdf"` line is optional — leave it out if there's no PDF.

**To add a working paper or other writing**, add entries to the `items` list of
the `"Working papers"` or `"Other writing"` section in exactly the same shape.
Those two sections are empty right now, so they don't appear on the live site
yet — they'll show up automatically once you add a first entry.

**To add a project** ("Other things I'm working on"), add a line to its `items`
list — a project is just one Markdown string:

```json
"[Project name](https://link) — your role, 2025"
```

## Files

- `content.json` — **the file you edit.** All the site's words.
- `index.html` — generated automatically from `content.json`. Don't edit by hand.
- `template.html` — the page shell the content is poured into (rarely touched).
- `build.py` — the script that turns `content.json` into `index.html`.
- `styles.css` — design tokens and styles ("Classical" system: warm gold accent, hairline rules, justified body copy).
- `fonts/` — self-hosted Cormorant Garamond and Lora (both SIL Open Font License).
- `portrait.jpg` — the photo above the title (600px wide).
- `favicon.svg` — browser-tab icon ("GB").
- `CNAME` — tells GitHub Pages to serve the site at glenberman.com.
- `.github/workflows/deploy.yml` — the GitHub Action that rebuilds and deploys.

### Rebuilding locally (optional)

You never need to, but if you want to preview changes on your own machine:
`python3 build.py` regenerates `index.html`, then open it in a browser.

## First-time deployment to GitHub Pages

1. Create a new repository on github.com (public, no README).
2. Upload everything in this folder (drag and drop works: repo page →
   "uploading an existing file"). Include the `fonts/` folder, `CNAME`, and the
   `.github` folder.
3. In the repo: **Settings → Pages** → under "Build and deployment", set
   **Source** to **GitHub Actions** (not "Deploy from a branch" — the included
   workflow handles building and publishing).
4. The Action runs on the first push; the site appears at
   `https://<username>.github.io/<repo>/` within a couple of minutes. You can
   watch it under the repo's **Actions** tab.

### Pointing glenberman.com at it

At your domain registrar (wherever glenberman.com's DNS is managed):

1. Add four **A records** for the apex domain (`@`) pointing to GitHub Pages:
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
2. Optionally add a **CNAME record** for `www` pointing to `<username>.github.io`.
3. Back in the repo's **Settings → Pages**, enter `glenberman.com` under
   Custom domain (the `CNAME` file keeps that setting from being lost on
   redeploys), and tick **Enforce HTTPS** once the certificate is issued (can
   take up to an hour after DNS propagates).

Since the domain currently points at WordPress.com, the DNS change is what
actually moves the live site — nothing breaks until you change the records, so
you can get the GitHub Pages version working at the `github.io` URL first and
switch DNS when happy.
