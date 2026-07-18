# Implementation Guard

The baseline records source hashes, behavior statement signatures, file scope,
dirty state, and required commands. The receipt compares them after the UI
change.

Allowed UI files may change only within the approved screen contract.
Protected files may not change. A behavior signature change is a failed guard
even when it occurs inside an allowed UI file.

Static verification does not run native commands automatically. Execute every
required command separately and attach the real result to the handoff. Treat
golden or screenshot comparison as framework-local semantic evidence, not
cross-framework pixel identity.

Human review remains required for subjective aesthetic quality. Automated
simulator or emulator checks do not equal physical-device VoiceOver or TalkBack
certification.
