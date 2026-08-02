# Phase 8 evaluation harness

The harness is additive to the committed ASW core. It freezes a profile,
records independent controller ground truth, runs the five declared observer
conditions, persists raw JSONL, and rebuilds a deterministic aggregate.

From this extension directory:

```powershell
python -m evaluation.validate
python -m unittest discover -s evaluation/tests -v
python -m evaluation.run --run-id <new-run-id>
python -m evaluation.validate --run evaluation/results/<run-id>
python -m evaluation.aggregate evaluation/results/<run-id>
python -m evaluation.report evaluation/results/<run-id>
```

The default ASW condition imports the sibling accepted core and uses its
public/service boundary (`ASWService.emit_event` and
`AgentAPI.open_signal_stream`). A missing core is an execution blocker; the
harness does not silently substitute a benchmark-only ASW implementation.
