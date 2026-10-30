// Verifies the actual production assets and same-origin API proxy over HTTP.
// This does not substitute for visual browser QA.
import assert from 'node:assert/strict'
import { readFileSync, readdirSync, writeFileSync, mkdirSync } from 'node:fs'
import { createHash } from 'node:crypto'
const base = process.env.ECHO_PREVIEW_URL ?? 'http://127.0.0.1:5173'
const checks = []
async function get(path) {
  const response = await fetch(base + path)
  assert.equal(response.status, 200, path)
  checks.push({ path, status: response.status })
  return response
}
const html = await (await get('/')).text()
assert.ok(html.includes('id="root"') && html.includes('type="module"'))
for (const filename of readdirSync('dist/assets')) {
  const actual = Buffer.from(await (await get(`/assets/${filename}`)).arrayBuffer())
  const expected = readFileSync(`dist/assets/${filename}`)
  const digest = value => createHash('sha256').update(value).digest('hex')
  assert.equal(digest(actual), digest(expected), filename)
}
const health = await (await get('/api/health')).json()
assert.equal(health.data_ready, true)
const metrics = await (await get('/api/evaluation')).json()
const saved = JSON.parse(readFileSync('../backend/artifacts/baseline_metrics.json', 'utf8'))
assert.deepEqual(metrics.results[0], saved)
const schema = await (await get('/openapi.json')).json()
assert.equal(schema.info.title, 'ECHO-17 Forensic API')
assert.ok((await (await get('/docs')).text()).includes('SwaggerUIBundle'))
const evidence = { timestamp: new Date().toISOString(), base_url: base, checks, note: 'HTTP asset/proxy checks; visual browser QA remains separate.' }
mkdirSync('.test-build', { recursive: true })
writeFileSync('.test-build/preview_verification.json', JSON.stringify(evidence, null, 2))
console.log(JSON.stringify({ checks_passed: checks.length, base_url: base, asset_hashes_match: true, real_model_metrics_match: true }, null, 2))
