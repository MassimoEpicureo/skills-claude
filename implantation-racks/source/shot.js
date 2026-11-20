const { chromium } = require('playwright');
(async () => {
  const [,, url, out, w, h, js] = process.argv;
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  const errs=[]; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type()==='error') errs.push(m.text()) });
  await p.goto(url); await p.waitForTimeout(1500);
  if (js) { await p.evaluate(js); await p.waitForTimeout(800); }
  await p.screenshot({ path: out });
  console.log('errors:', errs.join(' | ') || 'none');
  await b.close();
})();
