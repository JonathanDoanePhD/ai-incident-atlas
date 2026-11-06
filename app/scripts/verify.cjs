/* End-to-end verification with Playwright (pre-installed Chromium).
 * Usage: node scripts/verify.cjs [baseUrl] [outDir]
 * - Screenshots of every page at desktop (1440×900) and mobile (375×812) sizes
 * - Fails on console errors / page errors
 * - Confirms that filter/slider changes do NOT recreate node objects (3-D object uuids stay identical)
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE = process.argv[2] || 'http://localhost:4173/';
const OUT = process.argv[3] || path.join(__dirname, '..', '..', 'docs', 'screenshots');
fs.mkdirSync(OUT, { recursive: true });

const PAGES = [
  ['constellation', '#/'],
  ['catalog', '#/catalog'],
  ['incident', '#/incident/4'],
  ['insights', '#/insights'],
  ['about', '#/about'],
];

async function run() {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const problems = [];
  const report = { pages: {}, sliderCheck: null };

  for (const [device, viewport, scale] of [['desktop', { width: 1440, height: 900 }, 2], ['mobile', { width: 375, height: 812 }, 2]]) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: scale });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(String(e)));
    for (const [name, hash] of PAGES) {
      await page.goto(BASE + hash, { waitUntil: 'networkidle' });
      await page.waitForTimeout(name === 'constellation' ? 3500 : 1200);
      const file = path.join(OUT, `${name}-${device}.png`);
      await page.screenshot({ path: file, fullPage: name !== 'constellation' });
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      report.pages[`${name}-${device}`] = { errors: [...errors], horizontalOverflow: overflow };
      if (overflow) problems.push(`${name}-${device}: horizontal overflow`);
      errors.length = 0;
    }

    if (device === 'desktop') {
      // ---- slider check: node objects must not be recreated by filter changes ----------------------------
      await page.goto(BASE + '#/', { waitUntil: 'networkidle' });
      await page.waitForTimeout(3500);
      const snap = () => page.evaluate(() => {
        const g = window.__atlasGraph;
        const nodes = g.graphData().nodes;
        return { n: nodes.length, uuids: nodes.slice(0, 400).map((n) => (n.__threeObj ? n.__threeObj.uuid : null)),
                 pos: nodes.slice(0, 50).map((n) => [n.x, n.y, n.z].map((v) => Math.round(v * 1000))) };
      });
      const before = await snap();
      const slider = page.locator('#year-upper');
      for (const v of [2015, 2019, 2022, 2024, 2026]) {
        await slider.fill(String(v));
        await page.waitForTimeout(250);
      }
      // severity slider + a colour change + a facet checkbox
      await page.locator('select').nth(1).selectOption('sev');
      await page.waitForTimeout(400);
      const after = await snap();
      const same = before.uuids.every((u, i) => u !== null && u === after.uuids[i]);
      const samePos = JSON.stringify(before.pos) === JSON.stringify(after.pos);
      report.sliderCheck = { nodes: before.n, objectsPreserved: same, positionsUnchanged: samePos };
      if (!same) problems.push('slider/colour changes recreated node objects');
      if (!samePos) problems.push('slider/colour changes moved nodes');
      // hover + select screenshot
      await page.mouse.move(720, 450);
      await page.screenshot({ path: path.join(OUT, 'constellation-severity-desktop.png') });
      // preset: recurring failure modes with a selection
      await page.locator('select').first().selectOption('failures');
      await page.waitForTimeout(1200);
      await page.screenshot({ path: path.join(OUT, 'constellation-failures-desktop.png') });
    }
    for (const [k, v] of Object.entries(report.pages)) if (v.errors.length) problems.push(`${k}: ${v.errors.slice(0, 3).join(' | ')}`);
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'verify-report.json'), JSON.stringify({ report, problems }, null, 1));
  console.log(JSON.stringify({ sliderCheck: report.sliderCheck, problems }, null, 1));
  process.exit(problems.length ? 1 : 0);
}

run().catch((e) => { console.error(e); process.exit(2); });
