# Metrics and Frozen MVP Thresholds

## Layer A metrics

Required per trial:

- `detected`: correct transition recognized;
- `detection_latency_ms`: observer recognition time minus ground-truth transition time;
- `observation_count`: polls/queries/events consumed to reach recognition;
- `missed`: no correct recognition within scenario deadline;
- `duplicate_count`: extra recognized instances of the same ground-truth useful transition;
- `false_positive_count`: recognized transitions with no matching ground truth;
- `application_attribution_correct` when applicable;
- `kind_correct`;
- `subject_correct` when applicable;
- `localization_correct` when structured localization is expected;
- `continuation_ready`: observer output contains enough information for the scripted continuation rule.

## Layer B metrics

Required:

- continuation success;
- agent tool-call count;
- total observation/read calls;
- input/output token usage when available;
- time from ground-truth transition to correct continuation;
- incorrect-action count.

## Frozen MVP thresholds

The ASW MVP proposition is **supported** only if all correctness floors pass and the efficiency criterion passes.

### Correctness floors

Across the three primary scenario classes:

- ASW detection success rate: **>= 98%**;
- ASW duplicate useful-signal rate: **<= 2%**;
- ASW false-positive useful-signal rate: **<= 2%**;
- application attribution accuracy where applicable: **>= 98%**;
- kind accuracy: **>= 98%**;
- no replay/access/authorization violation may occur during evaluation.

### Efficiency criterion — Layer A

For at least **2 of the 3 primary scenario classes**, ASW MUST reduce median `observation_count` by **>= 30%** versus the mechanically selected best applicable non-ASW baseline, while not reducing detection success by more than **2 percentage points**.

### Agent continuation criterion — Layer B

Across the three primary scenario classes combined:

- ASW continuation success MUST be non-inferior to the selected best baseline by more than **5 percentage points**; and
- ASW MUST reduce median agent observation/read tool calls by **>= 20%** OR reduce median transition-to-correct-continuation time by **>= 20%**.

The efficiency criterion is satisfied by either agent cost or continuation latency because different agent environments may price polling versus waiting differently.

## Interpretation

- All floors + efficiency criteria pass → `SUPPORTED`.
- Any correctness floor fails → `NOT_SUPPORTED`.
- Correctness passes but efficiency evidence is below threshold → `INCONCLUSIVE_OR_NOT_SUPPORTED` as declared by the summary; do not claim the MVP proposition is validated.

Thresholds MUST NOT be changed after comparative runs begin.
