# Kópia skillov pre Claude Code

Tento priečinok je **generovaný**. Neupravuj ho ručne.

Zdroj skillov je `.agents/skills/` (spoločný pre Codex aj Claude). Claude Code hľadá skilly iba tu,
preto sa kopírujú. Po zmene skillu v `.agents/skills/` spusti:

```bash
python scripts/sync_claude_skills.py
```

Test `tests/test_claude_skills.py` zlyhá, keď sa kópia rozíde so zdrojom.
