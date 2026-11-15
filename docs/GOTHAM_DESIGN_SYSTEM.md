# CareerBridge — Gotham Edition Design System

## Direction

CareerBridge uses a restrained Gotham-inspired Art Deco language: architectural geometry, editorial headings and premium career-technology surfaces. It is an original visual system and does not use Batman/DC characters, logos or imagery.

Brand line: **A city of opportunities. A bridge to your future.**

## Tokens

| Token | Value | Use |
|---|---|---|
| Midnight Ink | `#07151B` | Sidebar, primary dark actions, assistant user messages |
| Deep Gotham Teal | `#102831` | Navigation and dark information surfaces |
| Slate Teal | `#193943` | Secondary dark surfaces and selected states |
| Antique Gold | `#D8B46C` | Rules, focus rings, active accents and restrained highlights |
| Muted Brass | `#A58B5C` | Secondary borders and labels |
| Warm Ivory | `#F2EBDD` | Application background and editorial surfaces |
| Mist | `#D6DFDC` | Neutral supporting tone |
| Charcoal | `#24343B` | Body text |
| Success / Pending / Error / Info | `#3C987A` / `#D8A64F` / `#C86B68` / `#7299B5` | State communication |

Typography uses Cormorant Garamond (with Georgia fallback) for display headings and Inter (with system fallback) for interface text. Cinzel is intentionally not required by the current implementation so the interface does not depend on another font download.

## Component rules

- Sidebar: Midnight Ink, compact navigation, Antique Gold active rule.
- Page shell: Warm Ivory, consistent content edge and responsive padding.
- Cards: Warm Ivory/white surfaces, restrained 1px teal line and soft shadow.
- Primary actions: Midnight Ink with ivory text.
- Secondary actions: transparent ivory surface with Muted Brass border.
- Destructive actions: Error tone and explicit confirmation where consequential.
- Focus: visible Antique Gold outline.
- Assistant: readable two-column desktop workspace, single-column mobile layout, internal conversation scrolling only.
- Responsive behavior: sidebar/navigation and grids collapse at 900px; forms and cards remain readable at 640px.

## Implementation

- Global tokens: `frontend/src/index.css`.
- Shared application shell and page styling: `frontend/src/App.css`.
- Existing pages retain their API calls, Redux state, authorization and data rendering.
- Reduced-motion preference is honored by disabling nonessential transitions and animations.

## Verification

Automated frontend tests and production build are the acceptance gate for CSS regressions. Browser screenshots remain outstanding when browser automation is unavailable; they must be captured manually at desktop, tablet and mobile widths before submission.
