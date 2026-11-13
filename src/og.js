// Renders src/og.html to assets/og.jpg (1200x630), the image shown when the site is shared.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.goto('file://' + require('path').join(__dirname, 'og.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({ path: require('path').join(__dirname, '../assets/og.jpg'), type: 'jpeg', quality: 88 }); await b.close();
})();
