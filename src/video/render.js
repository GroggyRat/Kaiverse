// Renders the KaiTech intro film to media/. Run from the repo root: node src/video/render.js [land|port] [fps]
// It reuses the point forms from src/kaitech.html, so the film and the site always match.
const fs = require('fs'), path = require('path'), { spawn } = require('child_process'), { chromium } = require('playwright');
const root = path.join(__dirname, '../..'), which = process.argv[2] || 'land', fps = +(process.argv[3] || 30);
const size = which === 'port' ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
const site = fs.readFileSync(path.join(root, 'src/kaitech.html'), 'utf8');
const forms = site.slice(site.indexOf('/* ── forms'), site.indexOf('/* colour'));
const page = fs.readFileSync(path.join(__dirname, 'intro.html'), 'utf8').replace('/*FORMS*/', forms);
const tmp = path.join(__dirname, '.intro-built.html'); fs.writeFileSync(tmp, page);
fs.mkdirSync(path.join(root, 'media'), { recursive: true });
const out = path.join(root, 'media', which === 'port' ? 'kaitech-intro-vertical.mp4' : 'kaitech-intro.mp4');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: size, deviceScaleFactor: 1 });
  p.on('pageerror', e => { console.error('page error:', e.message); process.exit(1); });
  await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  const dur = await p.evaluate(() => window.DURATION), frames = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < frames; f++) {
    await p.evaluate(t => window.renderAt(t), f / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % (fps * 4) === 0) console.log(`${which}: ${(f / fps).toFixed(0)}s of ${dur}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); fs.unlinkSync(tmp);
  console.log('wrote', path.relative(root, out));
})();
