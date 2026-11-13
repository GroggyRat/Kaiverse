// Renders a KaiTech film to media/. From the repo root: node src/video/render.js [land|port] [fps] [intro|rot]
// Music comes from media/kaitech-<film>-music.wav when it exists (src/video/music.py, src/video/rot_music.py).
// It reuses the point forms from src/kaitech.html, so the film and the site always match.
const fs = require('fs'), path = require('path'), { spawn, spawnSync } = require('child_process'), { chromium } = require('playwright');
const root = path.join(__dirname, '../..'), which = process.argv[2] || 'land', fps = +(process.argv[3] || 30), film = process.argv[4] || 'intro';
const size = which === 'port' ? { width: 1080, height: 1920 } : { width: 1920, height: 1080 };
const site = fs.readFileSync(path.join(root, 'src/kaitech.html'), 'utf8');
const forms = site.slice(site.indexOf('/* ── forms'), site.indexOf('/* colour'));
let page = fs.readFileSync(path.join(__dirname, film + '.html'), 'utf8').replace('/*FORMS*/', forms);
const tlFile = path.join(__dirname, film + '_timeline.json');   // the brain rot cut follows its narrator's timings
if (fs.existsSync(tlFile)) page = page.replace('/*TIMELINE*/null', fs.readFileSync(tlFile, 'utf8'));
// the brain rot cut is deep-fried: punchy colour, crunchy sharpening, grain and a slight colour split
const look = film === 'rot' ? ['-vf', 'eq=contrast=1.22:saturation=1.75:gamma=0.96,unsharp=7:7:1.3,rgbashift=rh=3:bh=-3,noise=alls=9:allf=t+u'] : [];
const tmp = path.join(__dirname, '.' + film + '-built.html'); fs.writeFileSync(tmp, page);
fs.mkdirSync(path.join(root, 'media'), { recursive: true });
const out = path.join(root, 'media', `kaitech-${film}${which === 'port' ? '-vertical' : ''}.mp4`);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: size, deviceScaleFactor: 1 });
  p.on('pageerror', e => { console.error('page error:', e.message); process.exit(1); });
  await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  const dur = await p.evaluate(() => window.DURATION), frames = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', ...look,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < frames; f++) {
    await p.evaluate(t => window.renderAt(t), f / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % (fps * 4) === 0) console.log(`${which}: ${(f / fps).toFixed(0)}s of ${dur}s`);
  }
  const events = await p.evaluate(() => window.EVENTS || null);
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); fs.unlinkSync(tmp);
  if (events && film === 'rot') {   // the beat and sound effects are made to match what happened on screen
    fs.writeFileSync(path.join(root, 'media/.rot-events.json'), JSON.stringify(events));
    const m = spawnSync('python3', [path.join(__dirname, 'rot_music.py')], { stdio: 'inherit' }); if (m.status) throw new Error('rot_music.py failed');
  }
  // add the music (src/video/music.py writes it) at -16 LUFS, the usual level for social video
  const music = path.join(root, `media/kaitech-${film}-music.wav`);
  if (fs.existsSync(music)) {
    const tmpOut = out.replace(/\.mp4$/, '.music.mp4');
    await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-i', out, '-i', music, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
      '-af', film === 'rot' ? 'loudnorm=I=-11:TP=-1:LRA=7' : 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmpOut], { stdio: 'inherit' })
      .on('close', c => c ? rej(new Error('ffmpeg failed')) : res()));
    fs.renameSync(tmpOut, out);
  }
  console.log('wrote', path.relative(root, out));
})();
