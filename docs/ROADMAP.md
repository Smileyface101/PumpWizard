# Roadmap

PumpWizard Runner is a local application. Users import a strategy configuration, while the application independently acquires data, builds research history, evaluates the rule set, and records positions locally. PumpWizard itself is not a runtime dependency.

## M0: downloadable foundation — current

The repository has a tested Python package, native desktop shell, local strategy library, CLI, version display, and GitHub Actions builds for Windows, macOS, and Linux. Release artifacts are produced from tagged source. The app is deliberately not executable as a trading bot yet.

## M1: strategy compatibility

Extract the shared deterministic decision core and define a complete strategy package contract: engine version, feature/data semantics, effective parameters, policy overlays, and exact import rules. Existing handoffs may carry simulation configuration, public telemetry, and trial metadata; they need a compatibility mapping before they can be executed locally.

The acceptance rule is exact: given the same normalized observations, clock, configuration, and portfolio state, the reference and runner must produce the same feature values, decisions, reasons, and scheduled actions.

## M2: independent research

Add local discovery, market normalization, observation storage, token memory, ownership evidence, FX handling, migrations, shared peer cohorts, and warm-up health. The app must build the required history locally and remain usable while PumpWizard is unreachable.

## M3: real execution alpha

Add a local signer, one verified Pump/PumpSwap route set, an intent/order state machine, transaction validation, quote checks, actual balance reconciliation, restart recovery, and automatic or manual closing. The initial alpha supports one explicitly named strategy compatibility level.

## M4: public strategy coverage

Support the current base styles, research families, policy overlays, multiple strategy instances, and shared-mint reservations. No strategy is advertised as portable until parity tests cover it.

## M5: stable 1.0

Add signed platform packages, local backup and restore, upgrade recovery, onboarding, complete position history, and a documented release matrix. Stable release assets are retained; failed builds do not replace a working release.

## Release policy

Development builds use a distinct prerelease version and are labelled by what they can do. Stable releases include platform-specific runnable assets, checksums, source commit, app version, engine versions, and database schema version. Assets are published from tags, remain immutable after publication, and use GitHub artifact attestations where available.

