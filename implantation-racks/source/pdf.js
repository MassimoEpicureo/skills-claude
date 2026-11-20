const { chromium } = require('playwright');
(async () => {
  const src = process.argv[2], out = process.argv[3], pngdir = process.argv[4];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1123, height: 794 } });
  await p.goto('file://' + src); await p.waitForTimeout(800);
  await p.pdf({ path: out, width: '297mm', height: '210mm', printBackground: true });
  const secs = await p.$$('section');
  for (let i = 0; i < secs.length; i++) await secs[i].screenshot({ path: pngdir + '/p' + (i + 1) + '.png' });
  await b.close();
})();
