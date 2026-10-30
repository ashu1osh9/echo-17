# ECHO-17 attribution and license boundaries

ECHO-17 application code is MIT licensed under `LICENSE`. This grant does not relicense datasets, models, third-party software, fonts or their outputs. This is a non-commercial research/hackathon demonstration, not an industrial monitoring product.

| Component | Role / attribution | Terms and source |
|---|---|---|
| UCI 447 | Helwig, N., Pignanelli, E., and Schütze, A. (2015), Condition Monitoring of Hydraulic Systems. Real 60-second recordings and aligned condition labels. | [DOI 10.24432/C5CW21](https://doi.org/10.24432/C5CW21), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Derived UCI data | Six measured channels summarized into 36 statistics; selected recorded samples downsampled for replay. Attribution retained in the deployment manifest. No synthetic waveforms. | Same data attribution/license; changes identified here and in the manifest. |
| TabPFN | Prior Labs' tabular foundation-model implementation; genuine 3.5 classification on Colab Tesla T4. No novel foundation-model architecture is claimed by ECHO-17. | [Official implementation/license](https://github.com/PriorLabs/TabPFN/blob/main/LICENSE) and [3.5 checkpoint terms](https://huggingface.co/Prior-Labs/tabpfn_3_5/blob/main/LICENSE) are distinct. The 3.5 checkpoint has separate non-commercial/non-production restrictions. No checkpoint or inference dependency is bundled in the public demo. Do not describe weights as MIT. |
| Gemma 3 | Google, genuine local 1B instruction-model inference; bounded evidence selection through Ollama. | [Gemma Terms](https://ai.google.dev/gemma/terms), including applicable use restrictions. Saved reports are outputs, not redistributed weights. No Gemma weights are included in the public demo. |
| Ollama | Local model runtime and official model registry. | [Official source/license](https://github.com/ollama/ollama/blob/main/LICENSE); runtime licensing does not replace model terms. |
| Python, NumPy, pandas, SciPy, scikit-learn, joblib | Data validation, numerical statistics, Random Forest and evaluation. | Python PSF terms; NumPy/pandas/SciPy/scikit-learn/joblib upstream license files apply, generally BSD-style. Preserve their notices in installed distributions. |
| FastAPI, Pydantic, Uvicorn, requests, httpx, pytest | API, schema validation, HTTP and tests. | Upstream MIT/BSD/Apache terms as supplied with each installed package. |
| React, TypeScript, Vite, Recharts, Lucide | Existing user interface, typed build, measured charts and icons. | Respective upstream MIT/Apache/ISC licenses; preserve package notices. |
| DM Sans and Space Grotesk | Existing typography loaded from Google Fonts with system-font fallbacks. | See the font families' upstream Open Font License notices. No proprietary font binary is redistributed here. |

Development extends the existing ECHO-17 starter and used Codex assistance. The article, tests and run log distinguish genuine model execution from prepared configuration. Existing design and source attribution are preserved. Model comparison uses the same saved split; no novelty claim is made for Random Forest, TabPFN or Gemma themselves.

Before external publication, the owner must review applicable model terms for the intended non-commercial demonstration. Publishing a research preview is not permission to offer a commercial/safety-critical model service. Configuration files are not evidence that Render was used.

**TabPFN public-release gate:** the published 3.5 terms restrict **outputs**, not only weights, to their defined permitted purposes; they also separately restrict hosted model/derivative services. Precomputation does not remove output restrictions. The published license includes professional/customer-scope and end-user-use clauses that must be checked against the participant agreement actually accepted. This task has not verified a public-display permission or an exception for this project. Confirm the intended interactive preview/output publication with the accepted participant terms or Prior Labs before publishing the payload. This notice does not assert a legal permission or relicense model outputs as MIT.
