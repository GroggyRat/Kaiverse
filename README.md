# KaiTech website

The public site for KaiTech: software that keeps Fiji business moving.

It is a static site plus one small server function for the demo request form. Vercel serves the repository root as it is.

## Files

| Path | What it is |
|---|---|
| `src/kaitech.html` | The one-screen site: the point object, the seven sections and all their copy (the `MODES` list near the top of the script). |
| `src/pages/` | About, Privacy and Terms, as plain HTML content. |
| `build.py` | Wraps the sources into `index.html`, `about.html`, `privacy.html` and `terms.html`. |
| `assets/favicon.svg` | Browser tab icon. |
| `api/demo.js` | The server function behind the demo request form: checks the request, saves it to Supabase, and emails KaiTech. |
| `supabase/demo_requests.sql` | Creates the table the requests are saved in. |
| `explorations/` | Earlier design options, kept for reference. Not part of the site. |

## Change something

Edit a file in `src/`, then run:

```bash
python3 build.py
```

Commit the rebuilt HTML files along with the source.

## Deploy

Import the repository in Vercel with the framework set to "Other" and no build command. The root is served as static files. `api/demo.js` becomes `/api/demo`.

## Switch on the demo request form

1. In Supabase, open the SQL editor and run `supabase/demo_requests.sql`. Requests then appear in the `demo_requests` table.
2. In Vercel, under the project's Environment Variables, add:

| Name | Value |
|---|---|
| `SUPABASE_URL` | The project URL from Supabase, Settings, API |
| `SUPABASE_SERVICE_ROLE_KEY` | The service role key from the same page. Keep it secret; it is only ever used on the server. |
| `RESEND_API_KEY` | Optional. A Resend API key, to get an email for each request. |
| `DEMO_FROM_EMAIL` | Optional. The sender, on a domain verified in Resend, for example `KaiTech <demo@kaitech.com.fj>`. |
| `DEMO_NOTIFY_EMAIL` | Optional. Where the notification goes, for example `kaitechfj@gmail.com`. |

3. Redeploy. Until the two Supabase values are set, the form tells visitors to email or call instead.

Without the three optional values, requests are still saved; you just get no email about them.
