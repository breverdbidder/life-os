# THEME DESIGN SYSTEM

## Overview
This document defines the design system for all BidDeed.AI and Life OS user-facing applications. It ensures visual consistency, brand recognition, and accessibility compliance across all interfaces.

---

## DESIGN PHILOSOPHY

### Core Principles

1. **No Generic Defaults**: Every interface must be distinguishable from template designs
2. **Domain-Specific Aesthetics**: Colors and typography reflect the product's purpose
3. **Mathematical Rigor**: Spacing, typography, and color systems follow strict scales
4. **Accessibility First**: WCAG AAA compliance is mandatory, not optional

### Design System Goals

- **Brand Recognition**: Users should identify BidDeed.AI/Life OS instantly
- **Professional Trust**: Visual design conveys authority and reliability
- **Cognitive Load Reduction**: Clean, hierarchical layouts reduce decision fatigue
- **Performance**: Lightweight CSS, minimal JS for animations

---

## COLOR SYSTEMS

### BidDeed.AI Palette

**Theme: Professional Foreclosure/Legal/Financial**

```css
/* /brevard-bidder-landing/styles/theme.css */
:root {
  /* Primary Colors - Professional Navy */
  --background: oklch(0.98 0.002 250);      /* Off-white with blue tint */
  --foreground: oklch(0.25 0.01 250);       /* Near-black with blue undertone */
  
  /* Card & Surface Colors */
  --card: oklch(0.99 0.001 250);            /* Slightly warmer than background */
  --card-foreground: oklch(0.25 0.01 250);  /* Same as foreground */
  --popover: oklch(0.99 0.001 250);
  --popover-foreground: oklch(0.25 0.01 250);
  
  /* Brand Colors */
  --primary: oklch(0.45 0.12 250);          /* Deep navy blue (trust, authority) */
  --primary-foreground: oklch(1.0 0 0);     /* Pure white */
  --secondary: oklch(0.65 0.08 30);         /* Muted gold/amber (wealth, caution) */
  --secondary-foreground: oklch(0.20 0.01 30);
  --accent: oklch(0.55 0.15 220);           /* Professional teal (data, insight) */
  --accent-foreground: oklch(1.0 0 0);
  
  /* UI State Colors */
  --muted: oklch(0.92 0.01 250);            /* Light blue-gray */
  --muted-foreground: oklch(0.50 0.02 250); /* Mid-tone for secondary text */
  --border: oklch(0.88 0.01 250);           /* Subtle border color */
  --input: oklch(0.92 0.01 250);            /* Input field background */
  --ring: oklch(0.45 0.12 250);             /* Focus ring (matches primary) */
  
  /* Semantic Colors */
  --destructive: oklch(0.50 0.20 25);       /* Professional red (not bright) */
  --destructive-foreground: oklch(1.0 0 0);
  --success: oklch(0.60 0.15 150);          /* Professional green */
  --success-foreground: oklch(1.0 0 0);
  --warning: oklch(0.70 0.18 80);           /* Amber warning */
  --warning-foreground: oklch(0.20 0.01 80);
  
  /* Data Visualization (5-color scale) */
  --chart-1: oklch(0.45 0.12 250);  /* Primary - Navy */
  --chart-2: oklch(0.55 0.15 220);  /* Accent - Teal */
  --chart-3: oklch(0.65 0.12 200);  /* Light Blue */
  --chart-4: oklch(0.60 0.18 30);   /* Gold */
  --chart-5: oklch(0.50 0.10 180);  /* Cyan */
}

.dark {
  /* Dark Mode - High Contrast for Data Readability */
  --background: oklch(0.15 0.01 250);
  --foreground: oklch(0.95 0.001 250);
  
  --card: oklch(0.18 0.01 250);
  --card-foreground: oklch(0.95 0.001 250);
  
  --primary: oklch(0.60 0.15 240);          /* Brighter blue for dark mode */
  --primary-foreground: oklch(0.10 0.01 250);
  
  --secondary: oklch(0.70 0.12 40);         /* Brighter gold */
  --secondary-foreground: oklch(0.15 0.01 40);
  
  --accent: oklch(0.65 0.18 210);           /* Brighter teal */
  --accent-foreground: oklch(0.10 0.01 210);
  
  /* ... continue dark mode colors */
}
```

**Color Usage Guidelines:**

| Color Variable | Use Case | Example |
|----------------|----------|---------|
| `--primary` | CTAs, links, primary actions | "Schedule Demo" button |
| `--secondary` | Secondary actions, badges | "Learn More" button, "Premium" badge |
| `--accent` | Highlights, hover states | Card hover border, active tab |
| `--success` | Positive states, confirmations | "Property verified" indicator |
| `--warning` | Caution states, alerts | "Lien priority warning" |
| `--destructive` | Errors, deletions | "Delete property" action |

### Life OS Palette

**Theme: Minimalist ADHD-Optimized**

```css
/* /life-os/styles/theme.css */
:root {
  /* Extreme Contrast for Focus */
  --background: oklch(0.99 0 0);            /* Pure white */
  --foreground: oklch(0.20 0 0);            /* Pure black */
  
  /* Minimal Surface Variation */
  --card: oklch(0.98 0 0);
  --card-foreground: oklch(0.20 0 0);
  
  /* Brand Colors - Purple Focus Theme */
  --primary: oklch(0.40 0.08 270);          /* Deep purple (focus, calm) */
  --primary-foreground: oklch(1.0 0 0);
  --secondary: oklch(0.70 0.05 270);        /* Light purple (secondary actions) */
  --secondary-foreground: oklch(0.25 0.01 270);
  --accent: oklch(0.65 0.18 150);           /* Energizing green (completion) */
  --accent-foreground: oklch(1.0 0 0);
  
  /* Muted - Very Subtle */
  --muted: oklch(0.85 0.01 270);            /* Very light purple tint */
  --muted-foreground: oklch(0.50 0.02 270);
  
  /* Task State Colors */
  --initiated: oklch(0.75 0.08 60);         /* Amber - Starting */
  --in-progress: oklch(0.60 0.15 220);      /* Blue - Active */
  --completed: oklch(0.60 0.18 150);        /* Green - Done */
  --abandoned: oklch(0.50 0.15 10);         /* Red - Dropped */
  --blocked: oklch(0.45 0.10 30);           /* Orange - Stuck */
  --deferred: oklch(0.55 0.05 270);         /* Purple - Later */
}

.dark {
  /* Dark Mode - High Contrast Maintained */
  --background: oklch(0.12 0 0);            /* Near-black */
  --foreground: oklch(0.98 0 0);            /* Off-white */
  /* ... continue with high contrast adjustments */
}
```

**Color Usage Guidelines:**

| Color Variable | Use Case | Example |
|----------------|----------|---------|
| `--primary` | Primary actions, focus states | "Start Task" button |
| `--accent` | Completion indicators | Checkmark icons, progress bars |
| `--initiated` | Task state: Started but not active | Task card border |
| `--in-progress` | Task state: Currently working on | Active task highlight |
| `--completed` | Task state: Finished | Completed task checkmark |
| `--abandoned` | Task state: Gave up | Strikethrough text |
| `--blocked` | Task state: Cannot proceed | Warning indicator |

### Zoning Analyst AI Palette

**Theme: Professional Technical/Legal**

```css
/* /spd-site-plan-dev/styles/theme.css */
:root {
  /* Professional Document-Centric */
  --background: oklch(0.97 0.001 220);      /* Very light blue-gray */
  --foreground: oklch(0.22 0.01 220);       /* Dark blue-gray */
  
  /* Brand Colors - Technical Authority */
  --primary: oklch(0.42 0.10 240);          /* Deep blue (authority) */
  --primary-foreground: oklch(1.0 0 0);
  --secondary: oklch(0.60 0.05 220);        /* Slate gray (neutral) */
  --secondary-foreground: oklch(0.98 0 0);
  --accent: oklch(0.58 0.15 150);           /* Professional green (approval) */
  --accent-foreground: oklch(1.0 0 0);
  
  /* Approval State Colors */
  --approved: oklch(0.60 0.15 150);         /* Green */
  --pending: oklch(0.68 0.12 80);           /* Amber */
  --rejected: oklch(0.48 0.18 25);          /* Red */
  --under-review: oklch(0.55 0.10 220);     /* Blue */
}
```

---

## TYPOGRAPHY SYSTEM

### BidDeed.AI Typography

```css
:root {
  /* Font Families */
  --font-display: 'Outfit', sans-serif;      /* Headings - Geometric, modern */
  --font-body: 'Inter', sans-serif;          /* Body - Neutral, readable */
  --font-mono: 'JetBrains Mono', monospace;  /* Code/Data - Technical */
  
  /* Type Scale (1.250 - Major Third) */
  --text-xs: 0.64rem;     /* 10.24px - Micro labels */
  --text-sm: 0.80rem;     /* 12.8px - Captions, metadata */
  --text-base: 1rem;      /* 16px - Body text */
  --text-lg: 1.25rem;     /* 20px - Subheadings */
  --text-xl: 1.563rem;    /* 25px - H3 */
  --text-2xl: 1.953rem;   /* 31.25px - H2 */
  --text-3xl: 2.441rem;   /* 39px - H1 */
  --text-4xl: 3.052rem;   /* 48.83px - Hero display */
  
  /* Font Weights */
  --font-normal: 400;     /* Body text only */
  --font-medium: 500;     /* Subheadings, emphasized text */
  --font-semibold: 600;   /* Headings, buttons */
  --font-bold: 700;       /* Hero text, critical CTAs only */
  
  /* Line Heights */
  --leading-tight: 1.25;  /* Headings */
  --leading-normal: 1.5;  /* Body text */
  --leading-relaxed: 1.75; /* Long-form content */
  
  /* Letter Spacing */
  --tracking-tight: -0.015em;  /* Large headings */
  --tracking-normal: 0em;       /* Body text */
  --tracking-wide: 0.025em;     /* Buttons, labels */
}
```

**Typography Usage:**

```tsx
// Hero Heading
<h1 className="font-display text-4xl md:text-5xl font-bold leading-tight tracking-tight">
  Agentic AI for Foreclosure Intelligence
</h1>

// Subheading
<h2 className="font-display text-2xl font-semibold leading-tight">
  12-Stage Autonomous Pipeline
</h2>

// Body Text
<p className="font-body text-base leading-normal">
  The Everest Ascent™ methodology combines ML predictions with real-time
  lien discovery to calculate optimal maximum bids.
</p>

// Data/Metric
<span className="font-mono text-sm text-muted-foreground">
  64.4% ML Accuracy
</span>
```

### Life OS Typography

```css
:root {
  /* Font Families - Minimal Consistency */
  --font-display: 'Geist', sans-serif;   /* All text */
  --font-body: 'Geist', sans-serif;      /* Same for simplicity */
  --font-mono: 'Geist Mono', monospace;  /* Timestamps, code */
  
  /* Simplified Type Scale */
  --text-sm: 0.875rem;  /* 14px - Metadata */
  --text-base: 1rem;    /* 16px - Primary text */
  --text-lg: 1.125rem;  /* 18px - Subheadings */
  --text-xl: 1.5rem;    /* 24px - Headings */
  --text-2xl: 2rem;     /* 32px - Page titles */
  
  /* Font Weights - Minimal */
  --font-normal: 400;   /* All body text */
  --font-semibold: 600; /* Headings only */
}
```

---

## SPACING SYSTEM

### Base Unit: 4px (Tailwind Default)

```css
:root {
  /* Spacing Scale (Powers of 2 + Golden Ratio) */
  --space-1: 0.25rem;   /* 4px - Tiny gaps (icon padding) */
  --space-2: 0.5rem;    /* 8px - Compact spacing (button padding) */
  --space-3: 0.75rem;   /* 12px - Small spacing (form fields) */
  --space-4: 1rem;      /* 16px - Base spacing (component padding) */
  --space-6: 1.5rem;    /* 24px - Medium spacing (card padding) */
  --space-8: 2rem;      /* 32px - Large spacing (section gaps) */
  --space-12: 3rem;     /* 48px - Section spacing */
  --space-16: 4rem;     /* 64px - Major section breaks */
  --space-24: 6rem;     /* 96px - Hero section spacing */
}
```

### Spacing Application Rules

| Context | Spacing Variable | Tailwind Class |
|---------|------------------|----------------|
| Inside components | `space-4` (16px) | `p-4` or `px-4 py-4` |
| Between components | `space-8` (32px) | `space-y-8` or `gap-8` |
| Between sections | `space-16` (64px) | `py-16` |
| Hero sections | `space-24` (96px) | `py-24` |

**Example:**
```tsx
<section className="py-24"> {/* Hero spacing */}
  <div className="space-y-16"> {/* Section spacing */}
    <div className="bg-card p-6 space-y-4"> {/* Component spacing */}
      <h2>Heading</h2>
      <p>Body text</p>
    </div>
  </div>
</section>
```

---

## LAYOUT PATTERNS

### Asymmetric Hero (60/40 Split)

**BidDeed.AI Landing Page:**

```tsx
<div className="max-w-[1600px] mx-auto px-8 py-24">
  <div className="grid grid-cols-[1.5fr_1fr] gap-16 items-center">
    {/* Text-Heavy Left (60%) */}
    <div className="space-y-8">
      {/* Primary content */}
    </div>
    
    {/* Visual Right (40%) */}
    <div>
      {/* Data visualization, screenshot, etc. */}
    </div>
  </div>
</div>
```

### Masonry Grid (Variable Heights)

**Feature Sections:**

```tsx
<div className="grid grid-cols-3 gap-8 auto-rows-auto">
  <div className="row-span-2"> {/* Tall card */}
    {/* Feature A */}
  </div>
  <div> {/* Standard height */}
    {/* Feature B */}
  </div>
  <div className="row-span-2"> {/* Tall card */}
    {/* Feature C */}
  </div>
  <div className="col-span-2"> {/* Wide card */}
    {/* Feature D */}
  </div>
</div>
```

### Sidebar + Main Content (Life OS)

```tsx
<div className="flex h-screen">
  {/* Fixed Sidebar */}
  <aside className="w-[280px] border-r border-border bg-card p-6">
    {/* Navigation, stats */}
  </aside>
  
  {/* Main Content */}
  <main className="flex-1 p-8 overflow-y-auto">
    {/* Active task, timeline */}
  </main>
</div>
```

---

## COMPONENT STATES

### Button States

```tsx
<button className="
  /* Base State */
  bg-primary text-primary-foreground
  px-6 py-3 rounded-lg
  font-semibold tracking-tight
  
  /* Hover State */
  hover:bg-primary/90
  hover:shadow-lg
  hover:scale-[1.02]
  
  /* Active State */
  active:scale-[0.98]
  active:shadow-sm
  
  /* Focus State (Keyboard Navigation) */
  focus-visible:outline-none
  focus-visible:ring-2
  focus-visible:ring-primary
  focus-visible:ring-offset-2
  
  /* Disabled State */
  disabled:opacity-50
  disabled:cursor-not-allowed
  disabled:hover:scale-100
  
  /* Transitions */
  transition-all duration-150 ease-out
">
  Primary Action
</button>
```

### Card Hover Effects

```tsx
<div className="
  /* Base State */
  bg-card border border-border
  rounded-xl p-6
  
  /* Hover State */
  hover:shadow-xl
  hover:border-primary/20
  hover:-translate-y-1
  
  /* Transition */
  transition-all duration-200 ease-out
">
  Card Content
</div>
```

### Input Focus States

```tsx
<input className="
  /* Base State */
  bg-input border border-border
  px-4 py-2 rounded-lg
  
  /* Focus State */
  focus:outline-none
  focus:ring-2
  focus:ring-primary
  focus:border-primary
  
  /* Transition */
  transition-all duration-150
" />
```

---

## TWEAKCN WORKFLOW

### Step-by-Step Process

#### 1. Visit TweakCN
```
https://tweakcn.com/
```

#### 2. Select Domain

- **BidDeed.AI**: Professional foreclosure/legal theme
- **Life OS**: Minimalist ADHD-optimized theme
- **Zoning Analyst AI**: Technical document-centric theme

#### 3. Choose Base Preset

**For BidDeed.AI:**
- Look for: Navy/teal/gold combinations
- Keywords: "Professional", "Corporate", "Financial"
- Avoid: Bright colors, playful themes

**For Life OS:**
- Look for: Minimal, high-contrast themes
- Keywords: "Clean", "Minimalist", "Simple"
- Avoid: Complex gradients, multiple accent colors

**For Zoning Analyst AI:**
- Look for: Technical, document-focused themes
- Keywords: "Legal", "Document", "Professional"
- Avoid: Vibrant colors, casual aesthetics

#### 4. Customize Colors

**TweakCN Editor:**
- Select OKLCH color mode (for perceptual uniformity)
- Adjust primary/secondary/accent colors
- Test contrast ratios (aim for 7:1 for body text)
- Generate light AND dark mode variants

**Key Adjustments:**
```
Primary Color:
- BidDeed.AI: Deep navy (oklch 0.45 0.12 250)
- Life OS: Deep purple (oklch 0.40 0.08 270)
- Zoning Analyst: Deep blue (oklch 0.42 0.10 240)

Secondary Color:
- BidDeed.AI: Muted gold (oklch 0.65 0.08 30)
- Life OS: Light purple (oklch 0.70 0.05 270)
- Zoning Analyst: Slate gray (oklch 0.60 0.05 220)

Accent Color:
- BidDeed.AI: Professional teal (oklch 0.55 0.15 220)
- Life OS: Energizing green (oklch 0.65 0.18 150)
- Zoning Analyst: Professional green (oklch 0.58 0.15 150)
```

#### 5. Export CSS Variables

**Click "Copy Code" in TweakCN**

You'll get output like:
```css
:root {
  --background: oklch(0.98 0.002 250);
  --foreground: oklch(0.25 0.01 250);
  --primary: oklch(0.45 0.12 250);
  /* ... more variables */
}
```

#### 6. Paste to Theme File

**For BidDeed.AI:**
```bash
# File: /brevard-bidder-landing/styles/theme.css
# Replace entire :root block with TweakCN output
```

**For Life OS:**
```bash
# File: /life-os/styles/theme.css
# Replace entire :root block with TweakCN output
```

**For Zoning Analyst AI:**
```bash
# File: /spd-site-plan-dev/styles/theme.css
# Replace entire :root block with TweakCN output
```

#### 7. Test Accessibility

**Run Contrast Checks:**
```bash
# Install contrast checker
npm install -D axe-core

# Or use online tool:
# https://www.whocanuse.com/
```

**Test Combinations:**
- `--foreground` on `--background` (body text)
- `--primary-foreground` on `--primary` (buttons)
- `--muted-foreground` on `--muted` (secondary text)

**Target Ratios:**
- Body text (16px): **7:1** (WCAG AAA)
- Large text (24px): **4.5:1** (WCAG AAA)

#### 8. Commit to GitHub

```bash
# Add theme file
git add styles/theme.css

# Commit with descriptive message
git commit -m "feat: update theme colors for [domain] brand identity"

# Push to trigger deployment
git push origin main
```

#### 9. Deploy to Cloudflare Pages

**Auto-deployment triggers on push to main:**
- BidDeed.AI: https://brevard-bidder-landing.pages.dev
- Life OS: https://life-os-aiy.pages.dev
- Zoning Analyst AI: (future deployment URL)

### TweakCN Features to Leverage

| Feature | Use Case | Benefit |
|---------|----------|---------|
| **OKLCH Color Mode** | Generate perceptually uniform colors | Ensures consistent brightness across hues |
| **Light/Dark Toggle** | Generate both modes simultaneously | Maintains brand consistency across themes |
| **Contrast Checker** | Built-in WCAG validation | Catch accessibility issues early |
| **Live Preview** | Real-time component rendering | See changes before exporting |
| **Preset Library** | Start from curated themes | Saves time, ensures quality baseline |
| **Export Code** | One-click CSS variable export | No manual color picking required |

---

## ACCESSIBILITY COMPLIANCE

### WCAG AAA Standards

**Text Contrast:**
- Normal text (16px): **7:1** minimum
- Large text (24px+): **4.5:1** minimum

**Interactive Elements:**
- Buttons: **4.5:1** minimum
- Form borders: **3:1** minimum

### Color Blindness Considerations

**Test with Color Blindness Simulators:**
- https://www.color-blindness.com/coblis-color-blindness-simulator/
- Check all 3 types: Protanopia, Deuteranopia, Tritanopia

**Design Rules:**
- Never rely on color alone (use icons + color)
- Ensure sufficient contrast in grayscale
- Use patterns/textures for critical distinctions

### Keyboard Navigation

**Focus Indicators (Always Visible):**
```tsx
focus-visible:outline-none
focus-visible:ring-2
focus-visible:ring-primary
focus-visible:ring-offset-2
```

**Tab Order:**
- Logical flow (top to bottom, left to right)
- Skip links for long navigation
- No keyboard traps

### Screen Reader Support

**Semantic HTML:**
```tsx
<main>      // ✅ Main content
<nav>       // ✅ Navigation
<article>   // ✅ Self-contained content
<section>   // ✅ Thematic grouping
<aside>     // ✅ Sidebar content
<div>       // ❌ Non-semantic, use sparingly
```

**ARIA Labels:**
```tsx
// Icon-only button
<button aria-label="Delete property">
  <TrashIcon />
</button>

// Status indicator
<div role="status" aria-live="polite">
  Property analysis complete
</div>
```

---

## MAINTENANCE CHECKLIST

### Adding New Colors

- [ ] Generate in OKLCH color space via TweakCN
- [ ] Test contrast ratios (WCAG AAA)
- [ ] Document in `theme.css` with comment
- [ ] Update THEME.md usage guidelines
- [ ] Test in light AND dark mode
- [ ] Verify color blindness accessibility

### Adding New Components

- [ ] Check `shared/ui/` for existing patterns
- [ ] Document design rationale in component file
- [ ] Include hover/focus/active states
- [ ] Test keyboard navigation
- [ ] Verify responsive behavior (mobile, tablet, desktop)
- [ ] Update Storybook (if applicable)

### Updating Existing Components

- [ ] Verify theme consistency across all variants
- [ ] Test all interactive states
- [ ] Check responsive breakpoints
- [ ] Update tests if API changed
- [ ] Document breaking changes

---

## DESIGN SYSTEM FILES

### File Structure

```
/brevard-bidder-landing/
  ├── styles/
  │   ├── theme.css           # BidDeed.AI color system
  │   └── globals.css         # Base Tailwind imports
  ├── components/
  │   ├── ui/                 # Shadcn/ui primitives
  │   └── custom/             # Domain-specific components
  └── docs/
      ├── THEME.md            # This file
      ├── FRONTEND_DESIGN.md  # Design rules
      └── KING_MODE.md        # Architectural planning

/life-os/
  ├── styles/
  │   ├── theme.css           # Life OS color system
  │   └── globals.css
  ├── components/
  │   ├── ui/
  │   └── tasks/              # Task-specific components
  └── docs/
      ├── THEME.md
      ├── FRONTEND_DESIGN.md
      └── KING_MODE.md
```

### Importing Theme

**In `globals.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Import theme variables */
@import './theme.css';

@layer base {
  body {
    @apply bg-background text-foreground;
    font-family: var(--font-body);
  }
  
  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display);
  }
  
  code, pre {
    font-family: var(--font-mono);
  }
}
```

**In React Components:**
```tsx
import '@/styles/globals.css'  // Automatically includes theme.css

export function Component() {
  return (
    <button className="bg-primary text-primary-foreground">
      Uses Theme Variables
    </button>
  )
}
```

---

## INTEGRATION WITH AI ARCHITECT RULES

When Claude AI generates UI code, it **MUST**:

1. **Load Theme First**: Always read `styles/theme.css` before generating components
2. **Use Theme Variables**: Never use hardcoded Tailwind colors (no `bg-blue-500`)
3. **Follow FRONTEND_DESIGN.md**: Apply anti-generic UI rules
4. **Document Rationale**: Include design rationale comment in every component
5. **Self-Check**: Verify contrast ratios, hover states, accessibility before outputting

**Example Component Header:**
```tsx
/**
 * PropertyCard
 * 
 * Domain: BidDeed.AI
 * Purpose: Display foreclosure property with ML prediction and max bid
 * Design Rationale: Asymmetric layout emphasizes property photo (60%),
 * uses navy/teal color scheme for professional aesthetic, includes hover
 * state for interactive exploration
 */
export function PropertyCard({ property }: PropertyCardProps) {
  // Component implementation using theme variables
}
```

---

## RESOURCES

### Design Tools
- **TweakCN**: https://tweakcn.com/
- **Who Can Use**: https://www.whocanuse.com/ (Contrast checker)
- **Color Blindness Simulator**: https://www.color-blindness.com/coblis-color-blindness-simulator/

### Typography
- **Outfit (Display)**: https://fonts.google.com/specimen/Outfit
- **Inter (Body)**: https://fonts.google.com/specimen/Inter
- **JetBrains Mono (Code)**: https://fonts.google.com/specimen/JetBrains+Mono
- **Geist (Life OS)**: https://vercel.com/font

### Documentation
- **Shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG22/quickref/

---

**This design system is a living document. Update it when adding new patterns, colors, or components.**
