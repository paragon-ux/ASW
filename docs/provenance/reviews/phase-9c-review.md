[P1] Disclose that Layer B efficiency values are scripted, not measured runtime effects — docs/WHITEPAPER.md:281

`ScriptedContinuationAgent.continue_from()` deterministically assigns one observation call and 20 ms when a structured subject exists, versus two calls and 40 ms otherwise. The paper presents the resulting 50% latency and call improvements as empirical continuation results without explaining this assignment, which can mislead readers into interpreting the latency as independently measured execution time.

[P1] Remove the claim that Phase 8 generated real transitions — docs/WHITEPAPER.md:21

The harness uses deterministic in-memory `ControlledProbe` timelines rather than live process, filesystem, or UI transitions. Although the ASW condition exercises the committed service/reducer/agent path, describing the evaluation as using “controlled real transitions” contradicts section 7.2 and the harness. `docs/WHITEPAPER_SPEC.md:39` preserves the same inaccurate requirement.

[P2] Correct the Layer B repetition unit — docs/WHITEPAPER.md:278

Layer B used three repetitions per primary scenario, not per primary class. Each primary class contains two scenarios, producing six trials per condition in each class, as shown in the frozen report. The current wording understates the class-level sample count and prevents exact reconstruction of the table.

[P2] Define the observation-count contract behind the 50% result — docs/WHITEPAPER.md:314

The harness counts ordinary-notification receipt and parsing as two observations while counting the ASW stream result as one; ASW subscription setup and controlled event publication are not included. Because this operational definition mechanically determines the reported one-versus-two comparison, it must be stated near the methodology or results for the “observation effort” claim to be interpretable and reproducible.

[P2] Make the evaluation reproduction reference independently resolvable — docs/WHITEPAPER.md:386

The release repository contains sanitized anchors and the frozen aggregate, but the commands require a separate evaluation package containing the harness, profile, ground truth, and raw records. The paper supplies only a sibling-directory reference and no public origin or evaluation revision, so a research reader cannot acquire the exact package needed to run the documented commands.

[P3] Correct the random-delay upper bound — docs/WHITEPAPER.md:231

The controller calls `randint(min, max - 1)`, so generated delays are 500–1999 ms. Saying the range runs “from 500 to 2000 ms” implies that 2000 ms is attainable; describe it as `[500, 2000)` or 500–1999 ms.

Overall assessment: Phase 9C is not ready for sign-off. The frozen headline numbers, baseline selection, primary gate threshold, negative crash/restart result, controlled-scope limitations, zero-model Layer A statement, and external-LLM disclaimer otherwise align with the inspected evidence. I found no clear new normative requirement in the canonical whitepaper during the completed inspection.

Material test gaps: no automated check compares methodology prose with harness contracts, verifies repetition units and delay bounds, explains metric-counting semantics, distinguishes assigned from measured Layer B latency, or proves that the reproduction instructions work from a public clean checkout. No files were modified.