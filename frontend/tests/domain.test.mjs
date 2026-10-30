import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { advanceTime, alignedGraph, cycleName, filterCycles, parseRoute, previewDifferences } from '../src/domain.ts'

test('hash routes survive reloads and reject unknown paths', () => {
  assert.equal(parseRoute('').page, 'archive')
  assert.deepEqual(parseRoute('#/investigation/735'), { page: 'investigation', id: 735 })
  assert.equal(parseRoute('#/evaluation').page, 'evaluation')
  assert.equal(parseRoute('#/investigation/not-a-cycle').page, 'missing')
})
test('replay uses elapsed wall time, honors speed and clamps to the recording window', () => {
  assert.equal(advanceTime(0, 250, 4), 1)
  assert.equal(advanceTime(59.5, 1000, 2), 60)
  assert.equal(advanceTime(5, -100, 1), 5)
  assert.equal(advanceTime(10, 1000, .25), 10.25)
})
const base = new URL('../../backend/', import.meta.url)
const csv = readFileSync(new URL('artifacts/baseline_predictions.csv', base), 'utf8').trim().split(/\r?\n/)
const cycles = csv.slice(1).map(line => ({ id: Number(line.split(',')[0]) }))
test('archive search and session filters use all real held-out IDs without labels', () => {
  assert.equal(cycles.length, 441)
  assert.equal(filterCycles(cycles, 'Cycle #0735', 'all', [735])[0].id, 735)
  assert.deepEqual(filterCycles(cycles, '', 'opened', [735]), [{ id: 735 }])
  assert.equal(filterCycles(cycles, '', 'unopened', [735]).length, 440)
  assert.equal(filterCycles(cycles, 'not a cycle', 'all', []).length, 0)
  assert.equal(cycleName(5), 'Cycle 0005')
})
const response = await fetch('http://127.0.0.1:8000/api/cycles/735/signals?sensor=TS1')
assert.ok(response.ok)
const signal = await response.json()
const ghostResponse = await fetch('http://127.0.0.1:8000/api/ghost/735?sensor=TS1')
assert.ok(ghostResponse.ok)
const ghost = await ghostResponse.json()
test('progressive replay reveals only actual measured timestamps, including 1 Hz endpoints', () => {
  assert.equal(signal.times.length, 60)
  const partial = alignedGraph(signal, null, 2.5)
  assert.deepEqual(partial.map(point => point.t), [0, 1, 2])
  assert.deepEqual(partial.map(point => point.value), signal.values.slice(0, 3))
  assert.equal(alignedGraph(signal, null, 60).length, signal.values.length)
  assert.equal(alignedGraph(signal, null, 0).length, 1)
})
test('100 Hz and 10 Hz preview replay uses the supplied original timestamps without inventing points', async () => {
  const recordings = await Promise.all(['PS1', 'FS1'].map(async sensor => {
    const response = await fetch(`http://127.0.0.1:8000/api/cycles/735/signals?sensor=${sensor}`)
    assert.ok(response.ok)
    return response.json()
  }))
  for (const recording of recordings) {
    assert.equal(recording.values.length, 240)
    assert.equal(recording.times.at(-1), 60 - 1 / recording.rate_hz_original)
    assert.ok(recording.times.every((value, index) => index === 0 || value > recording.times[index - 1]))
    assert.deepEqual(alignedGraph(recording, null, .55).map(p => p.t), recording.times.filter(t => t <= .55))
  }
})
test('ghost overlay refuses stale cycle, sensor or timestamp alignment', () => {
  assert.equal(alignedGraph(signal, ghost, 60)[0].reference, ghost.reference_values[0])
  for (const wrong of [{ ...ghost, cycle_id: 5 }, { ...ghost, sensor: 'PS1' }, { ...ghost, times: [] }]) {
    assert.ok(alignedGraph(signal, wrong, 60).every(point => point.reference === undefined))
  }
})
test('preview differences are computed from actual aligned recordings', () => {
  const values = ghost.target_values.map((value, i) => value - ghost.reference_values[i])
  const result = previewDifferences(ghost)
  assert.equal(result.mean, values.reduce((a, b) => a + b, 0) / values.length)
  assert.equal(result.rmse, Math.sqrt(values.reduce((a, b) => a + b * b, 0) / values.length))
  assert.equal(previewDifferences({ ...ghost, reference_values: [] }), null)
})
