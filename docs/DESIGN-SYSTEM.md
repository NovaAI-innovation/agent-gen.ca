# Design System — agent-gen.ca v2

## Overview

The v2 design system is built on Tailwind v4 with semantic CSS custom properties, a dark-first cyber-futuristic palette, and accessible primitive components. All tokens are defined as CSS custom properties in `globals.css` and consumed via Tailwind utility classes.

## Token architecture

Tokens follow a three-layer hierarchy:

1. **Primitives** — raw color, spacing, and typography values. Never used directly in components.
2. **Semantic tokens** — purpose-named aliases of primitives (e.g. `--surface-page`, `--text-primary`, `--feedback-danger`). Used in components.
3. **Component tokens** — derived locally within component variants (e.g. button variants).

### Surfaces

| Token | Value | Usage |
|-------|-------|-------|
| `--surface-page` | void (near-black) | Page background |
| `--surface-elevated` | slate-950 | Cards, panels, modals |
| `--surface-muted` | slate-900 | Inputs, disabled areas |
| `--surface-hover` | slate-800 | Hover state background |
| `--surface-accent` | slate-800 | Accent-toned surfaces |

### Text

| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | text-100 (94% lightness) | Headings, body |
| `--text-secondary` | text-300 (77% lightness) | Subtitles, labels |
| `--text-muted` | text-500 (58% lightness) | Placeholders, hints |
| `--text-on-action` | void | Text on action backgrounds |

### Actions

| Token | Value | Usage |
|-------|-------|-------|
| `--action-primary` | cyan-500 | Primary buttons, links |
| `--action-primary-fg` | void | Text on primary |
| `--action-primary-hover` | cyan-400 | Hover state |
| `--action-secondary` | slate-800 | Secondary buttons |
| `--action-secondary-fg` | text-100 | Text on secondary |

### Feedback / status

| Token | Value | Usage |
|-------|-------|-------|
| `--feedback-success` | lime-500 | Success states |
| `--feedback-success-muted` | lime-500 at 15% opacity | Success backgrounds |
| `--feedback-warning` | amber-500 | Warning states |
| `--feedback-warning-muted` | amber-500 at 15% opacity | Warning backgrounds |
| `--feedback-danger` | red-500 | Error, destructive |
| `--feedback-danger-muted` | red-500 at 15% opacity | Error backgrounds |
| `--feedback-info` | cyan-500 | Informational |
| `--feedback-info-muted` | cyan-500 at 15% opacity | Info backgrounds |

### Borders

| Token | Value | Usage |
|-------|-------|-------|
| `--border-subtle` | slate-800 | Default borders |
| `--border-strong` | slate-700 | Emphasized borders |
| `--border-focus` | cyan-400 | Focus rings |
| `--border-error` | red-400 | Error state borders |

### Category accents

| Token | Usage |
|-------|-------|
| `--accent-mcp` | MCP server listings |
| `--accent-skill` | Agent skill listings |
| `--accent-agent` | Custom agent listings |
| `--accent-pack` | Pack listings |

### Typography scale

| Token | Value |
|-------|-------|
| `--font-size-xs` | 0.75rem (12px) |
| `--font-size-sm` | 0.875rem (14px) |
| `--font-size-base` | 1rem (16px) |
| `--font-size-lg` | 1.125rem (18px) |
| `--font-size-xl` | 1.25rem (20px) |
| `--font-size-2xl` | 1.5rem (24px) |
| `--font-size-3xl` | 1.875rem (30px) |
| `--font-size-4xl` | 2.25rem (36px) |

### Spacing scale (4px base)

| Token | Value |
|-------|-------|
| `--space-1` | 0.25rem (4px) |
| `--space-2` | 0.5rem (8px) |
| `--space-3` | 0.75rem (12px) |
| `--space-4` | 1rem (16px) |
| `--space-5` | 1.25rem (20px) |
| `--space-6` | 1.5rem (24px) |
| `--space-8` | 2rem (32px) |
| `--space-10` | 2.5rem (40px) |
| `--space-12` | 3rem (48px) |

### Radii

| Token | Value |
|-------|-------|
| `--radius-sm` | 0.5rem |
| `--radius-md` | 0.75rem |
| `--radius-lg` | 1rem |
| `--radius-xl` | 1.25rem |
| `--radius-full` | 9999px |

### Motion

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | 120ms | Micro-interactions |
| `--duration-normal` | 200ms | Standard transitions |
| `--duration-slow` | 350ms | Page transitions |
| `--ease-out` | cubic-bezier(0.16, 1, 0.3, 1) | Exit animations |
| `--ease-in-out` | cubic-bezier(0.45, 0, 0.55, 1) | Balanced motion |

### Focus ring

| Token | Value |
|-------|-------|
| `--ring-width` | 2px |
| `--ring-offset` | 2px |
| `--ring-color` | border-focus (cyan-400) |

### Shadows

| Token | Value |
|-------|-------|
| `--shadow-neon` | 0 0 12px primary at 35% |
| `--shadow-elevated` | 0 4px 24px black at 40% |

## Components

### Button

File: `frontend/src/components/ui/Button.tsx`

Variants: `primary`, `secondary`, `ghost`, `danger`
Sizes: `sm`, `md`, `lg`, `icon`
Props: `loading` (shows spinner, disables button), `asChild` (Radix Slot)

Accessibility:
- Focus-visible ring on all variants
- `disabled` and `aria-disabled` when loading or disabled
- `aria-busy` when loading
- Minimum 44px touch target on `md` and `lg` sizes

### Field

File: `frontend/src/components/ui/Field.tsx`

Wraps any input with a label, error message, and hint text. Links them via `aria-describedby`, `aria-invalid`, and `aria-required`.

Includes styled `Input` and `Textarea` sub-components with focus, error, and disabled states.

### StatusBadge

File: `frontend/src/components/ui/StatusBadge.tsx`

Statuses: `draft`, `pending`, `approved`, `published`, `rejected`, `suspended`, `active`, `expired`, `error`, `scanning`

Each status has a colored dot indicator (animated pulse for active states) and accessible `role="status"`.

### Alert

File: `frontend/src/components/ui/Alert.tsx`

Variants: `info`, `success`, `warning`, `danger`
Props: `title`, `onDismiss` (adds close button)

Includes inline SVG icons and `role="alert"` for screen readers.

### Panel

File: `frontend/src/components/ui/Panel.tsx`

Tones: `default`, `accent`, `muted`
Padding: `none`, `sm`, `md`, `lg`

Container with glassmorphism border and backdrop blur.

### Skeleton

File: `frontend/src/components/ui/Skeleton.tsx`

Animations: `pulse`, `shimmer`, `none`
Props: `width`, `height`, `circle`

Includes composite layouts: `CardSkeleton` for marketplace cards, `RowSkeleton` for table rows.

## Accessibility requirements

All primitives must:
- Support keyboard navigation (`Tab`, `Shift+Tab`, `Enter`, `Space`)
- Show visible focus indicators (`focus-visible` ring using `--ring-*` tokens)
- Meet WCAG 2.2 AA contrast ratios (4.5:1 for text, 3:1 for large text and UI components)
- Respect `prefers-reduced-motion` (already in globals.css)
- Provide appropriate ARIA attributes (`role`, `aria-label`, `aria-describedby`, `aria-invalid`, `aria-busy`)
- Maintain minimum 44x44px touch targets for interactive elements

## Fonts

- **Display headings:** Chakra Petch (`--font-display`)
- **Body text:** Manrope (`--font-body`)
- **Monospace / code:** JetBrains Mono (`--font-mono`)

## Responsive breakpoints

Standard Tailwind breakpoints. Test at 320px, 768px, 1024px, and 1440px.
