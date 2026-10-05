# Archived invitation prototype

`invitation.py` is retained for historical completeness. It is not imported by the active build, served by the live site or connected to Loops. It does not send email. Its .eml test text still contains superseded fixed-CST wording.

To inspect its CLI in the original root-import context, use `PYTHONPATH=. python3 legacy/invitation.py --help`. Its main config-loading path assumes the original working layout; this archive is not a supported production entrypoint. Do not connect it to a sender or use its hardcoded time text without a separately scoped implementation and tests.
