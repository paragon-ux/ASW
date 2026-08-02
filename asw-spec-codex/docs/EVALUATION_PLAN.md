# Evaluation Plan

## Objective

Test whether structured application signals improve recognition and continuation after asynchronous Windows application activity compared with common alternatives.

## Baselines

1. Polling.
2. Filesystem watching alone.
3. Ordinary Windows notification text.
4. Repeated visual observation.
5. ASW structured signals.

## Required scenario classes

- build/test completion or failure;
- external file/save/artifact changes;
- UI dialog/permission/control availability;
- render/export completion;
- process crash/restart.

## Metrics

- unnecessary observations/tool calls;
- transition-to-correct-response latency;
- application/event attribution accuracy;
- missed useful signal rate;
- duplicate signal rate;
- false-positive signal rate;
- continuation success after interruption;
- agent token/tool cost.

## Pre-registration

Before comparative runs, record scenario fixtures, implementation version, agent/model version when applicable, repetitions, tool budget, metric calculation, thresholds, and failure criteria.
