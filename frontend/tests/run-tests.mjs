// Test React state and API integration without a browser or a second UI framework.
import { build } from 'esbuild'
import { spawnSync } from 'node:child_process'
await build({
  entryPoints: ['tests/ui.test.tsx'], bundle: true, platform: 'node', format: 'esm',
  outfile: '.test-build/ui.test.mjs', jsx: 'automatic', packages: 'external',
  plugins: [{ name: 'chart-layout-boundary', setup(builder) {
    builder.onResolve({ filter: /^recharts$/ }, () => ({ path: 'chart-layout', namespace: 'test-boundary' }))
    builder.onLoad({ filter: /.*/, namespace: 'test-boundary' }, () => ({
      contents: `import React from 'react'; const Boundary = props => React.createElement('chart-boundary', props, props.children); export {Boundary as Area, Boundary as CartesianGrid, Boundary as ComposedChart, Boundary as Line, Boundary as ReferenceLine, Boundary as ResponsiveContainer, Boundary as Tooltip, Boundary as XAxis, Boundary as YAxis};`, loader: 'js', resolveDir: process.cwd()
    }))
  } }]
})
const result = spawnSync(process.execPath, ['--experimental-strip-types', '--test', 'tests/domain.test.mjs', '.test-build/ui.test.mjs'], { stdio: 'inherit' })
process.exitCode = result.status ?? 1
