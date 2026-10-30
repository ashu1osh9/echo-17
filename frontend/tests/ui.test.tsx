// Only chart layout is stubbed. All sensor, label, prediction and metric data use the real API.
import React from 'react'
import test from 'node:test'
import assert from 'node:assert/strict'
import TestRenderer, { act } from 'react-test-renderer'
import App from '../src/App'

const originalFetch = globalThis.fetch
const calls: { path: string; method: string }[] = []
let delayedPath = '', release: (() => void) | null = null
let failedPath = ''
globalThis.fetch = async (input, options) => {
  const path = String(input)
  calls.push({ path, method: options?.method ?? 'GET' })
  if (path === failedPath) return new Response(JSON.stringify({ detail: 'Test-only unavailable service' }), { status: 503, headers: { 'content-type': 'application/json' } })
  if (path === delayedPath) await new Promise<void>(resolve => { release = resolve })
  return originalFetch(new URL(path, 'http://127.0.0.1:8000'), options)
}
const listeners = new Map<string, () => void>()
globalThis.location = { hash: '#/archive' } as Location
globalThis.window = { addEventListener: (event: string, callback: () => void) => listeners.set(event, callback), removeEventListener: (event: string) => listeners.delete(event), scrollTo: () => {} } as unknown as Window & typeof globalThis
globalThis.document = { hidden: false, addEventListener: () => {}, removeEventListener: () => {} } as unknown as Document
let nextFrame = 0
const frames = new Map<number, FrameRequestCallback>()
globalThis.requestAnimationFrame = callback => { frames.set(++nextFrame, callback); return nextFrame }
globalThis.cancelAnimationFrame = frame => { frames.delete(frame) }
let root: TestRenderer.ReactTestRenderer
const content = (node: any): string => node == null ? '' : typeof node === 'string' || typeof node === 'number' ? String(node) : Array.isArray(node) ? node.map(content).join('') : content(node.children ?? node.props?.children)
const text = () => content(root.toJSON())
const button = (name: string) => root.root.findAllByType('button').find(node => node.props['aria-label'] === name || content(node.props.children).includes(name))!
async function until(condition: () => boolean, timeout = 8000) {
  const start = Date.now()
  while (!condition()) {
    if (Date.now() - start > timeout) throw new Error('Timed out waiting for real API/component state')
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 25)) })
  }
}
async function navigate(hash: string) { await act(async () => { location.hash = hash; listeners.get('hashchange')?.() }) }
async function click(name: string) { assert.ok(button(name), `Missing button ${name}`); await act(async () => { button(name).props.onClick() }) }

test('real end-to-end React investigation: archive, replay, ghost, diagnosis, explicit reveal, report and evaluation', async () => {
  await act(async () => { root = TestRenderer.create(<App />) })
  await until(() => text().includes('Machine recordings'))
  assert.ok(text().includes('441'))
  assert.equal(root.root.findAllByProps({ className: 'case-card' }).length, 12)
  const search = root.root.findByProps({ 'aria-label': 'Search cycle ID' })
  await act(async () => { search.props.onChange({ target: { value: '735' } }) })
  assert.equal(root.root.findAllByProps({ className: 'case-card' }).length, 1)
  await click('Clear search')
  await act(async () => { root.root.findByProps({ 'aria-label': 'Next page' }).props.onClick() })
  assert.ok(text().includes('Page 2 / 37'))
  await navigate('#/investigation/735')
  await until(() => root.root.findAllByProps({ 'aria-label': 'Play replay' }).length > 0 && !root.root.findByProps({ 'aria-label': 'Play replay' }).props.disabled)
  assert.equal(button('Reveal Actual Condition').props.disabled, true)
  assert.ok(!text().includes('RECORDED COOLER CONDITION'))
  assert.ok(!calls.some(call => call.path.includes('/reveal/')))
  await act(async () => { root.root.findByProps({ 'aria-label': 'Reset replay' }).props.onClick() })
  assert.ok(text().includes('REPLAY PAUSED'))
  await act(async () => { root.root.findByProps({ 'aria-label': 'Play replay' }).props.onClick() })
  assert.ok(root.root.findByProps({ 'aria-label': 'Pause replay' }))
  const now = performance.now()
  await act(async () => { const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(callback => callback(now + 1000)) })
  assert.ok(Number(root.root.findByProps({ 'aria-label': 'Replay position in seconds' }).props.value) > 0)
  await act(async () => { root.root.findByProps({ 'aria-label': 'Pause replay' }).props.onClick() })
  assert.equal(frames.size, 0)
  await act(async () => { root.root.findByProps({ 'aria-label': 'Replay speed' }).props.onChange({ target: { value: '4' } }); root.root.findByProps({ 'aria-label': 'Replay position in seconds' }).props.onChange({ target: { value: '60' } }) })
  await click('Reveal Ghost Signature')
  await until(() => text().includes('TRAIN ONLY'))
  assert.ok(text().includes('ALIGNED PREVIEW RMSE'))
  // Run the complete recorded interval on a controlled animation clock, using real signal/overlay data.
  await act(async () => { root.root.findByProps({ 'aria-label': 'Reset replay' }).props.onClick() })
  await act(async () => { root.root.findByProps({ 'aria-label': 'Play replay' }).props.onClick() })
  const replayStart = performance.now()
  for (let elapsed = 1000; elapsed <= 16000; elapsed += 1000) {
    await act(async () => { const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(callback => callback(replayStart + elapsed)) })
  }
  assert.equal(root.root.findByProps({ 'aria-label': 'Replay position in seconds' }).props.value, 60)
  assert.equal(frames.size, 0)
  assert.ok(root.root.findByProps({ 'aria-label': 'Play replay' }))
  const completedChart = root.root.findAllByType('chart-boundary').find(node => node.props.data)
  assert.equal(completedChart?.props.data.length, 240)
  assert.ok(completedChart?.props.data.every(point => Number.isFinite(point.reference)))
  assert.ok(text().includes('FULL RECORDING PREVIEW'))
  await click('Run AI diagnosis')
  await until(() => text().includes('Near failure'))
  assert.ok(text().includes('What the model was given.'))
  assert.equal(button('Reveal Actual Condition').props.disabled, false)
  assert.ok(!text().includes('RECORDED COOLER CONDITION'))
  await click('Reveal Actual Condition')
  await until(() => text().includes('Prediction differs'))
  assert.ok(text().includes('Near failure (3%) predicted / Reduced efficiency (20%) recorded'))
  await click('Generate investigation')
  await until(() => text().includes('Measured evidence'), 60000)
  assert.ok(text().includes('Rule-based / non-LLM fallback') || text().includes('LLM-generated interpretation'))
  await navigate('#/investigation/5')
  await until(() => root.root.findAllByProps({ 'aria-label': 'Play replay' }).length > 0)
  assert.ok(!text().includes('RECORDED COOLER CONDITION'))
  assert.ok(!text().includes('Prediction differs'))
  assert.equal(button('Reveal Actual Condition').props.disabled, true)
  await click('Run AI diagnosis')
  await until(() => text().includes('Near failure'))
  await click('Reveal Actual Condition')
  await until(() => text().includes('Prediction matches'))
  await navigate('#/evaluation')
  await until(() => text().includes('Confusion matrix'))
  assert.ok(text().includes('99.32'))
  for (const id of [2, 735, 1467]) assert.ok(root.root.findAllByProps({ href: `#/investigation/${id}` }).length > 0)
  await navigate('#/investigation/0')
  assert.ok(text().includes('Recording not found.'))
  await navigate('#/does-not-exist')
  assert.ok(text().includes('Page not found.'))
})

test('late requests from the previous recording cannot populate a new case', async () => {
  await navigate('#/investigation/735')
  delayedPath = '/api/diagnose/735'
  await click('Run AI diagnosis')
  assert.ok(release)
  await navigate('#/investigation/5')
  await act(async () => { release?.(); delayedPath = ''; await new Promise(resolve => setTimeout(resolve, 100)) })
  assert.ok(!text().includes('MODEL INTERPRETATION","children":["Near failure'))
  assert.ok(text().includes('No prediction retrieved yet.'))
  assert.equal(button('Reveal Actual Condition').props.disabled, true)
})

test('sensor changes reset the ghost and a 1 Hz recording uses its own actual timestamp count', async () => {
  await until(() => root.root.findAllByProps({ 'aria-label': 'Play replay' }).length > 0 && !root.root.findByProps({ 'aria-label': 'Play replay' }).props.disabled)
  await click('Reveal Ghost Signature')
  await until(() => text().includes('TRAIN ONLY'))
  const temperature = root.root.findAllByType('button').find(node => content(node.props.children).includes('TS1'))!
  await act(async () => { temperature.props.onClick() })
  await until(() => text().includes('Temperature · inlet') && root.root.findAllByProps({ 'aria-label': 'Play replay' }).length > 0 && !root.root.findByProps({ 'aria-label': 'Play replay' }).props.disabled)
  assert.ok(!text().includes('TRAIN ONLY'))
  assert.ok(text().includes('60'))
  const chart = root.root.findAllByType('chart-boundary').find(node => node.props.data)
  assert.equal(chart?.props.data.length, 60)
  assert.equal(chart?.props.data[59].t, 59)
  await act(async () => { root.unmount() })
  assert.equal(frames.size, 0)
})

test('unavailable signals and evaluation show errors, then retry the real service successfully', async () => {
  location.hash = '#/investigation/5'
  failedPath = '/api/cycles/5/signals?sensor=PS1'
  await act(async () => { root = TestRenderer.create(<App />) })
  await until(() => text().includes('Test-only unavailable service'))
  assert.ok(root.root.findByProps({ 'aria-label': 'Play replay' }).props.disabled)
  assert.ok(!text().includes('TRAIN ONLY'))
  failedPath = ''
  await click('Try again')
  await until(() => !root.root.findByProps({ 'aria-label': 'Play replay' }).props.disabled)
  failedPath = '/api/evaluation'
  await navigate('#/evaluation')
  await until(() => text().includes('Test-only unavailable service'))
  assert.ok(!text().includes('99.32'))
  failedPath = ''
  await click('Try again')
  await until(() => text().includes('Confusion matrix'))
  await act(async () => { root.unmount() })
})
