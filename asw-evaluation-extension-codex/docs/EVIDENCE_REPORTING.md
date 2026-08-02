# Evidence and Reporting

## Evidence hierarchy

1. frozen machine-readable profile;
2. controller ground-truth JSONL;
3. raw trial-result JSONL;
4. deterministic aggregate JSON;
5. human-readable result report.

The report summarizes evidence; it is not the evidence authority.

## Required result report sections

- repository commit and environment;
- hypothesis and frozen thresholds;
- scenario implementations;
- baseline implementations;
- Layer A results by scenario/condition;
- best-baseline selection output;
- Layer B agent continuation results;
- failures/exclusions and reasons;
- threshold audit;
- final classification: `SUPPORTED`, `NOT_SUPPORTED`, or `INCONCLUSIVE`;
- reproducibility commands.

Do not omit negative results.

## Claims

A `SUPPORTED` result supports the bounded RFC 0001 MVP proposition only. It does not establish universal application coverage, universal agent benefit, or cross-platform generality.
