
# Character Chatbot Monitoring Design System

This document outlines the design tokens, component classes, and visual patterns used in the Character Chatbot Monitoring application. Use this guide to maintain consistency across the application and when creating new features.

## 1. Color Palette

The application uses CSS variables for theming, supporting both Light and Dark modes.

### Theme Variables

| Variable | Light Mode (Default) | Dark Mode | Description |
|:---|:---|:---|:---|
| `--bg-primary` | `#ffffff` | `#0a0a0a` | Main background color (Body) |
| `--bg-secondary` | `#f9fafb` | `#121212` | Secondary background (Sidebar) |
| `--bg-card` | `#ffffff` | `#1a1a1a` | Card background |
| `--text-primary` | `#111827` | `#ffffff` | Primary text color |
| `--text-secondary` | `#6b7280` | `#a3a3a3` | Secondary text (subtitles) |
| `--border-primary` | `#e5e7eb` | `#262626` | Primary border color |
| `--state-hover-bg` | `#f3f4f6` | `rgba(255,255,255, 0.05)` | Hover state background |
| `--accent-coral` | `#ef4444` | `#ef4444` | Accent Color (Coral) |
| `--accent-mint` | `#10b981` | `#10b981` | Accent Color (Mint) |
| `--accent-blue` | `#3b82f6` | `#3b82f6` | Accent Color (Blue) |

### Gradients
Used for buttons and special text effects.
- **Start**: `--gradient-start`
- **Mid**: `--gradient-mid1`, `--gradient-mid2`, `--gradient-mid3`
- **End**: `--gradient-end`

## 2. Typography

**Font Family**: `'Pretendard Variable', 'Pretendard', system-ui, sans-serif`
**Headings/Special**: `'Galmuri11', sans-serif` (Used for sidebar items, crawl buttons, titles)

| Class | Usage | Style |
|:---|:---|:---|
| `.page-title` | Page Header | 2xl, Semibold, Galmuri11 |
| `.section-title` | Section Header | sm, Semibold |
| `.form-label` | Input Label | sm, Medium |
| `.menu-item` | Sidebar Item | 13px, Galmuri11 |

## 3. Component Classes

### Layout
- **`.app-container`**: Flex container for Sidebar + Main Content.
- **`.app-sidebar`**: Fixed sidebar (w-60). Handles mobile slide-in.
- **`.app-main-content`**: Main content area (ml-60).
- **`.main-content-wrapper`**: Max width container (max-w-6xl).

### Buttons
- **`.btn-primary`**: Standard action button.
  - Light: Black bg, White text.
  - Dark: Dark gray bg, White text.
- **`.crawl-button`**: Special animated gradient button for actions.
  - Animation: `gradient-flow` (continuous diagonal movement).

### Cards
- **`.card`**: Basic container. White/Dark bg, Bordered.
- **`.card--hoverable`**: Adds border transition on hover.
- **`.stat-card`**: Dashboard statistic card.

### Forms
- **`.form-input`**: Standard text input.
- **`.form-select`**: Dropdown select.

### Data Display
- **`.data-table`**: Standard table style.
- **`.ranking-list`**: List styling for rankings.
- **`.character-card`**: Card for character profiles (includes rank badge, tags).
- **`.bookmark-card`**: Card for saved links (includes thumbnail, summary).

## 4. Visual Effects

### Glassmorphism
Use the `.glass` class to apply a backdrop blur effect.
- **Light**: White opacity 0.8
- **Dark**: Black opacity 0.8

### Glow Effects
- **`.glow`**: Blue glow box-shadow.
- **`.glow-coral`**: Red glow.
- **`.glow-mint`**: Green glow.

### Fade Masks
- **`.mask-linear-fade`**: Applies a left-to-right fade out mask (useful for overflowing text/tags).

## 5. Utilities

### Scrollbar Hiding
Use `.scrollbar-hide` to hide scrollbars while preserving scroll functionality (cross-browser compatible).
```css
.scrollbar-hide {
  -ms-overflow-style: none; /* IE/Edge */
  scrollbar-width: none;    /* Firefox */
}
.scrollbar-hide::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}
```

## 6. Iconography
- **`.force-white-icon`**: Forces SVG icons to be white (useful for dark mode overrides or dark backgrounds).

## Usage Example

```tsx
<div className="card p-6">
  <h2 className="section-title mb-4">Card Title</h2>
  <div className="flex gap-2">
    <button className="btn-primary">Action</button>
    <button className="crawl-button">Animated Action</button>
  </div>
</div>
```
