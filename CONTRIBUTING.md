# Contributing

Keep strategy logic deterministic and versioned. A configuration may select supported behavior and parameters; it must not execute arbitrary code or access secrets.

Run the test suite and linter before submitting a pull request. Do not commit database files, provider credentials, keys, signed transactions, or market data whose redistribution is not permitted.

New strategy support requires input fixtures and parity tests against its declared reference implementation. New execution routes require transaction validation and recovery tests before a user-facing capability claim.

