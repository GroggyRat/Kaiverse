# KaiTech website

The public site for KaiTech: software that keeps Fiji business moving.

It is a static site plus one small server function for the demo request form. Vercel serves the repository root as it is.

## Files

| Path | What it is |
|---|---|
| `src/content.json` | All the words: every section and product, with their facts, screens and longer descriptions. Edit this to change copy. |
| `src/kaitech.html` | The one-screen site: the point object, layout and behaviour. Its content block is filled from `content.json` by the build. |
| `src/pages/` | About, Privacy and Terms, as plain HTML content. |
| `src/og.html`, `src/og.js` | The link preview image. Run `node src/og.js` to redraw `assets/og.jpg`. |
| `build.py` | Builds `index.html`, one page per product (`workforce`, `billzilla`, `inspect`, `drivo`), About, Privacy, Terms, `sitemap.xml` and `robots.txt`. |
| `assets/` | Favicon, preview image, client logos and product screens (shown with sample data). |
| `api/demo.js` | The server function behind the demo request form: checks the request, saves it to Supabase, emails KaiTech and the visitor through Gmail. |
| `supabase/demo_requests.sql` | Creates the table the requests are saved in. |
| `package.json` | The function's one dependency, nodemailer, for Gmail. Vercel installs it. |
| `vercel.json` | Clean addresses (`/billzilla` instead of `/billzilla.html`) and caching for images. |
| `explorations/` | Earlier design options, kept for reference. Not deployed. |

## Change something

Edit a file in `src/`, then run:

```bash
python3 build.py
```

Commit the rebuilt files along with the source.

- **Founder photo:** save a square photo as `assets/founder.jpg` and rebuild. It replaces the initials on the About page.
- **New address:** when the site moves to its own domain, rebuild with `SITE_URL=https://your-domain python3 build.py` so search engines and link previews use it.

## Deploy

The live site is the Vercel project `kaiverse`, deployed from the `main` branch: every push to `main` goes live, and other branches get preview addresses. To set it up again, import the repository in Vercel with the framework set to "Other" and no build command. The root is served as static files. `api/demo.js` becomes `/api/demo`.

## Switch on the demo request form

1. In Supabase, open the SQL editor and run `supabase/demo_requests.sql`. Requests then appear in the `demo_requests` table. The site uses the Supabase project named Kaiverse.
2. In Vercel, under the project's Environment Variables, add:

| Name | Value |
|---|---|
| `SUPABASE_URL` | The project URL from Supabase, Settings, API |
| `SUPABASE_KEY` | The publishable (public) key from the same page. The SQL above lets this key add demo requests and nothing else; it cannot read them. |

3. For emails, add:

| Name | Value |
|---|---|
| `GMAIL_USER` | `kaitechfj@gmail.com` |
| `GMAIL_APP_PASSWORD` | A 16-letter app password for that account (Google Account, Security, App passwords). Not the normal Gmail password. |
| `DEMO_NOTIFY_EMAIL` | Optional. Where the notification goes; defaults to `GMAIL_USER`. |
| `DEMO_AUTO_REPLY` | Optional. Set to `off` to stop the confirmation email to visitors. |
| `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY` | Optional. From Cloudflare Turnstile (free). With both set, the form shows a spam check and the server verifies it. |

Each request sends two emails through Gmail: one to KaiTech with the details (Reply answers the visitor), and a short confirmation to the visitor. A visitor address can send at most four requests in ten minutes.

4. Redeploy. Until the two Supabase values are set, the form tells visitors to email or call instead.

Without the email settings, requests are still saved; you just get no email about them.
