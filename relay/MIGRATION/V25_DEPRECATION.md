# Engineering Relay V2.5 deprecation notice

Status: **READ_ONLY_HISTORY**

V3 became the selected relay protocol at 2026-09-22T11:33:02.656127Z.

The preserved V2.5 tree remains at `agents/relay/**` with cutover digest:

```text
sha256:799ee8d10056ed7e66122b8b6626e3ed0d4bb3b645167d6a6d5dea1c3d9759f8
```

After cutover:
- existing V2.5 files remain inspectable as migration/history evidence;
- new relay authority must be written through V3 objects and commands;
- do not append new DISC/QSET/QUAL/TC/checkpoint/projection authority to the legacy tree;
- any change to the preserved legacy tree invalidates V3 cutover conformance until explicitly reconciled.
