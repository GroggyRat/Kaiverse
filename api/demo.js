// POST /api/demo — saves a demo request and tells KaiTech about it.
// Runs as a Vercel function. Needs SUPABASE_URL and SUPABASE_KEY (the project's publishable key:
// supabase/demo_requests.sql lets that key add requests and nothing else).
// Optional, for a notification email per request, either
//   GMAIL_USER and GMAIL_APP_PASSWORD (sends through that Gmail account), or
//   RESEND_API_KEY, DEMO_FROM_EMAIL and DEMO_NOTIFY_EMAIL (sends through Resend).
const PRODUCTS = ['KaiWorkforce', 'BillZilla', 'KaiInspect', 'Drivo', 'Not sure yet'];
const clean = (v, max) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

module.exports = async function handler(req, res) {
  const send = (status, body) => { res.statusCode = status; res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(body)); };
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return send(405, { error: 'Send this as a POST request.' }); }

  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = null; } }
  if (!b || typeof b !== 'object') return send(400, { error: 'The request was empty. Please fill in the form and try again.' });

  // A hidden field people never see. Anything that fills it is a bot: say thanks, save nothing.
  if (clean(b.website, 200)) return send(200, { ok: true });

  const row = {
    name: clean(b.name, 120), business: clean(b.business, 160), email: clean(b.email, 200).toLowerCase(),
    phone: clean(b.phone, 40), product: clean(b.product, 40), message: clean(b.message, 2000),
  };
  if (!row.name) return send(400, { error: 'Please enter your name.', field: 'name' });
  if (!row.business) return send(400, { error: 'Please enter your business name.', field: 'business' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.email)) return send(400, { error: 'Please enter a valid email address.', field: 'email' });
  if (!PRODUCTS.includes(row.product)) row.product = 'Not sure yet';

  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_KEY;
  if (!url || !key) { console.error('demo: SUPABASE_URL or SUPABASE_KEY is not set'); return send(503, { error: 'The form is not switched on yet.' }); }

  try {
    const r = await fetch(url.replace(/\/$/, '') + '/rest/v1/demo_requests', {
      method: 'POST',
      headers: Object.assign({ apikey: key, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, key.startsWith('eyJ') ? { Authorization: 'Bearer ' + key } : {}),
      body: JSON.stringify(row),
    });
    if (!r.ok) { console.error('demo: Supabase said', r.status, await r.text()); return send(502, { error: 'We could not save your request.' }); }
  } catch (e) { console.error('demo: Supabase unreachable', e); return send(502, { error: 'We could not save your request.' }); }

  // The request is saved. The email is a courtesy to KaiTech, so a failure here does not fail the request.
  const mail = {
    subject: 'Demo request: ' + row.product + ' (' + row.business + ')',
    text: ['Name: ' + row.name, 'Business: ' + row.business, 'Email: ' + row.email, 'Phone: ' + (row.phone || 'not given'),
      'Product: ' + row.product, '', row.message || '(no message)', '', 'Reply to this email to answer ' + row.name + ' directly.'].join('\n'),
  };
  const gmailUser = process.env.GMAIL_USER, gmailPass = process.env.GMAIL_APP_PASSWORD;
  const resend = process.env.RESEND_API_KEY, from = process.env.DEMO_FROM_EMAIL;
  if (gmailUser && gmailPass) {
    // Through the Gmail account itself: sent from that address to DEMO_NOTIFY_EMAIL, or to itself.
    try {
      const nodemailer = require('nodemailer');
      const t = nodemailer.createTransport({ service: 'gmail', auth: { user: gmailUser, pass: gmailPass.replace(/\s+/g, '') } });
      await t.sendMail({ from: 'KaiTech website <' + gmailUser + '>', to: process.env.DEMO_NOTIFY_EMAIL || gmailUser, replyTo: row.name + ' <' + row.email + '>', ...mail });
    } catch (e) { console.error('demo: Gmail could not send', e && e.message); }
  } else if (resend && from && process.env.DEMO_NOTIFY_EMAIL) {
    try {
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + resend, 'Content-Type': 'application/json' },
        body: JSON.stringify({ from, to: [process.env.DEMO_NOTIFY_EMAIL], reply_to: row.email, ...mail }),
      });
      if (!r.ok) console.error('demo: Resend said', r.status, await r.text());
    } catch (e) { console.error('demo: Resend unreachable', e); }
  }
  return send(200, { ok: true });
};
