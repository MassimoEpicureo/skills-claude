# skills-claude

A collection of Claude skills.

## Skills

### `skills/frontend-design`
Guidance for distinctive, intentional visual design when building or reshaping UI
(aesthetic direction, typography, layout). Pure-text guidance, no scripts.

- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design)

### `skills/ui-ux-pro-max`
UI/UX design intelligence for web and mobile: 50+ styles, 161 color palettes,
57 font pairings, 161 product types, 99 UX guidelines, and 25 chart types across
10 stacks. Ships with a local, offline CSV search engine.

Example:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "fintech dashboard modern" --design-system
```

- Source: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- Only the main `ui-ux-pro-max` skill is included (the upstream repo also bundles
  additional sub-skills and an installer CLI, which are not included here).

## Security note

Both skills were reviewed before being added. No malicious code was found:
the `ui-ux-pro-max` scripts only perform local CSV processing (no network calls,
no shell execution beyond invoking `npx shadcn`/local validators, no credential
access). See each skill's upstream `LICENSE` for licensing.
