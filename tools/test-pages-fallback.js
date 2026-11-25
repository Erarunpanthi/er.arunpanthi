/* Exercise the GitHub Pages 404 fallback on project and custom domains. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const page = fs.readFileSync('404.html', 'utf8');
const scripts = [...page.matchAll(/<script>\s*([\s\S]*?)\s*<\/script>/g)].map(m => m[1]);
assert.equal(scripts.length, 2);

for (const [host, prefix] of [['erarunpanthi.github.io', '/er.arunpanthi/'], ['panthiarun.com.np', '/']]) {
  const pathname = prefix + 'Psc-preparation/Current-Affairs/exam/date=2083-06-28';
  let baseMarkup = '', target;
  const location = { hostname: host, pathname, search: '?reset=1', hash: '#q', replace(value) { target = value; } };
  const document = { write(value) { baseMarkup = value; }, baseURI: `https://${host}${prefix}` };
  vm.runInNewContext(scripts[0], { location, document });
  assert.equal(baseMarkup, `<base href="${prefix}">`);
  vm.runInNewContext(scripts[1], { window: { location }, document, URLSearchParams, URL });
  assert.equal(target, `https://${host}${prefix}Psc-preparation/Current-Affairs/exam.html?reset=1&date=2083-06-28#q`);
}
console.log('GitHub Pages 404 fallback works for both deployment paths');
