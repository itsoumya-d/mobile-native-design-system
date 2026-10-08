# Token parity failure fixture

Run from a clean checkout with Python 3.10 or newer; no packages, credentials,
mobile SDKs, network requests, or repository writes are needed:

```sh
python fixtures/token-parity/check.py
```

The script generates all four native adapters in a temporary directory twice,
checks byte stability and source parity, then deliberately:

- Changes a generated spacing value **and updates its manifest hash**.
- Empties the manifest's artifact list.
- Sets Android's minimum touch target to one logical unit.

Each invalid case must exit nonzero. The fixture itself exits zero only when
all expected successes and rejections occur. Its final JSON summarizes those
checks. Temporary files are removed automatically.

This is a compiler/guard fixture. It does not launch an app, test device
accessibility, or establish production application behavior. The existing
native fixture workflows separately compile and test their platform examples.
