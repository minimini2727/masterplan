#!/usr/bin/env node
// 소재 HTML 시안을 실제 사양 크기 PNG로 변환한다. 페이퍼로지 폰트를 주입한다.
// 사용법: node team/tools/html_to_png.js <html 폴더> <png 출력 폴더>
// 크기: body의 width/height(px)를 그대로 쓴다. 없으면 문서 전체 크기.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..', '..');
const FONT_DIR = path.join(ROOT, 'team', 'assets', 'fonts');

function fontCss() {
  return fs.readdirSync(FONT_DIR).filter(f => /^Paperlogy-\d+\.woff2$/.test(f)).map(f => {
    const w = f.match(/-(\d+)\./)[1];
    return `@font-face{font-family:'Paperlogy';font-weight:${w};font-style:normal;src:url('file://${path.join(FONT_DIR, f)}') format('woff2');}`;
  }).join('\n');
}

(async () => {
  const [src, out] = process.argv.slice(2);
  if (!src || !out) { console.error('사용법: node html_to_png.js <html 폴더> <png 폴더>'); process.exit(1); }
  fs.mkdirSync(out, { recursive: true });
  const files = fs.readdirSync(src).filter(f => f.endsWith('.html')).sort();
  const browser = await chromium.launch();
  const css = fontCss();
  const results = [];
  for (const f of files) {
    const page = await browser.newPage({ viewport: { width: 2000, height: 2000 } });
    await page.goto('file://' + path.resolve(src, f), { waitUntil: 'load' });
    await page.addStyleTag({ content: css + "\nbody,body *{font-family:'Paperlogy',sans-serif;}" });
    await page.evaluate(() => document.fonts.ready);
    const size = await page.evaluate(() => {
      const b = document.body, cs = getComputedStyle(b);
      const w = parseInt(cs.width) || document.documentElement.scrollWidth;
      const h = parseInt(cs.height) || document.documentElement.scrollHeight;
      return { w, h };
    });
    await page.setViewportSize({ width: size.w, height: size.h });
    const png = path.join(out, f.replace(/\.html$/, '.png'));
    await page.screenshot({ path: png, clip: { x: 0, y: 0, width: size.w, height: size.h } });
    results.push(`${f.replace(/\.html$/, '')}\t${size.w}x${size.h}`);
    await page.close();
  }
  await browser.close();
  console.log(results.join('\n'));
  console.log(`총 ${results.length}개 PNG 생성 → ${out}`);
})();
