# KaiTech website

The public site for KaiTech: software that keeps Fiji business moving.

It is a static site with no build tools beyond one Python script, so Vercel can serve the repository root as it is. There is no backend: "Book a demo" opens an email to kaitechfj@gmail.com.

## Files

| Path | What it is |
|---|---|
| `src/kaitech.html` | The one-screen site: the point object, the seven sections and all their copy (the `MODES` list near the top of the script). |
| `src/pages/` | About, Privacy and Terms, as plain HTML content. |
| `build.py` | Wraps the sources into `index.html`, `about.html`, `privacy.html` and `terms.html`. |
| `assets/favicon.svg` | Browser tab icon. |
| `explorations/` | Earlier design options, kept for reference. Not part of the site. |

## Change something

Edit a file in `src/`, then run:

```bash
python3 build.py
```

Commit the rebuilt HTML files along with the source.

## Deploy

Import the repository in Vercel with the framework set to "Other" and no build command. The root is served as static files.
