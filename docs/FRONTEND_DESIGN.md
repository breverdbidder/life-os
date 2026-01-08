# FRONTEND DESIGN SKILL: Anti-Generic UI Protocol

## PURPOSE
Prevents AI from generating generic Bootstrap/Tailwind default interfaces. Enforces distinctive, branded, professional aesthetics for BidDeed.AI and Life OS applications.

## CORE PRINCIPLE
**"If it looks like a template, it's wrong."**

---

## DESIGN PHILOSOPHY

### The Problem
ShadCN/UI and Tailwind CSS have created a "sea of sameness" across web applications:
- Generic blue primary buttons
- Standard card layouts with rounded corners
- Predictable gradient backgrounds
- Indistinguishable from thousands of other apps

### The Solution
Every interface must be **bespoke** to the domain:
- **BidDeed.AI**: Professional, data-driven, legal/financial aesthetic
- **Life OS**: Minimalist, productivity-focused, ADHD-optimized layout
- **Zoning Analyst AI**: Technical, document-centric, authority-focused design

---

## MANDATORY DESIGN CONSTRAINTS

### 1. Color Systems (NEVER Use Generic Values)

**❌ PROHIBITED:**
```css
/* Generic Tailwind defaults */
--primary: #3b82f6;  /* Blue 500 */
--secondary: #6b7280; /* Gray 500 */
--accent: #8b5cf6;   /* Violet 500 */
```

**✅ REQUIRED:**
Use project-specific theme files:
- `/brevard-bidder-landing/styles/theme.css` (BidDeed.AI)
- `/life-os/styles/theme.css` (Life OS)
- Define using OKLCH color space for perceptual uniformity

**Example BidDeed.AI Palette:**
```css
:root {
  /* Professional Foreclosure/Legal Aesthetic */
  --primary: oklch(0.45 0.12 250);     /* Deep navy blue */
  --secondary: oklch(0.65 0.08 30);    /* Muted gold/amber */
  --accent: oklch(0.55 0.15 220);      /* Professional teal */
  --background: oklch(0.98 0.002 250); /* Off-white, slight blue tint */
  --foreground: oklch(0.25 0.01 250);  /* Near-black with blue undertone */
  --destructive: oklch(0.50 0.20 25);  /* Professional red (not bright) */
  --success: oklch(0.60 0.15 150);     /* Professional green */
  --warning: oklch(0.70 0.18 80);      /* Amber warning */
  
  /* Data Visualization Colors */
  --chart-1: oklch(0.45 0.12 250);
  --chart-2: oklch(0.55 0.15 220);
  --chart-3: oklch(0.65 0.12 200);
  --chart-4: oklch(0.60 0.18 30);
  --chart-5: oklch(0.50 0.10 180);
}
```

**Example Life OS Palette:**
```css
:root {
  /* Minimalist ADHD-Optimized Aesthetic */
  --primary: oklch(0.40 0.08 270);     /* Deep purple (focus) */
  --secondary: oklch(0.70 0.05 270);   /* Light purple (calm) */
  --accent: oklch(0.65 0.18 150);      /* Energizing green */
  --background: oklch(0.99 0 0);       /* Pure white (minimal distraction) */
  --foreground: oklch(0.20 0 0);       /* Pure black (maximum contrast) */
  --muted: oklch(0.85 0.01 270);       /* Very light purple tint */
  
  /* Task State Colors */
  --initiated: oklch(0.75 0.08 60);    /* Amber */
  --in-progress: oklch(0.60 0.15 220); /* Blue */
  --completed: oklch(0.60 0.18 150);   /* Green */
  --abandoned: oklch(0.50 0.15 10);    /* Red */
  --blocked: oklch(0.45 0.10 30);      /* Orange */
}
```

### 2. Typography (Semantic and Purposeful)

**❌ PROHIBITED:**
- Using Inter/Roboto/Helvetica without justification
- Inconsistent font weights (300, 400, 500, 600, 700 all in one app)
- Arbitrary font sizes (text-sm, text-base, text-lg without system)

**✅ REQUIRED:**

**Typography Scale (BidDeed.AI):**
```css
:root {
  /* Display - Headings */
  --font-display: 'Outfit', sans-serif;  /* Modern, professional, geometric */
  --font-body: 'Inter', sans-serif;       /* Readable, neutral, data-focused */
  --font-mono: 'JetBrains Mono', monospace; /* Code and technical data */
  
  /* Size Scale (1.250 - Major Third) */
  --text-xs: 0.64rem;   /* 10.24px - Micro labels */
  --text-sm: 0.80rem;   /* 12.8px - Captions, metadata */
  --text-base: 1rem;    /* 16px - Body text */
  --text-lg: 1.25rem;   /* 20px - Subheadings */
  --text-xl: 1.563rem;  /* 25px - H3 */
  --text-2xl: 1.953rem; /* 31.25px - H2 */
  --text-3xl: 2.441rem; /* 39px - H1 */
  --text-4xl: 3.052rem; /* 48.83px - Hero display */
  
  /* Weight System */
  --font-normal: 400;   /* Body text only */
  --font-medium: 500;   /* Subheadings, emphasized text */
  --font-semibold: 600; /* Headings, buttons */
  --font-bold: 700;     /* Hero text, critical CTAs only */
}
```

**Typography Scale (Life OS):**
```css
:root {
  /* Minimalist ADHD-Optimized */
  --font-display: 'Geist', sans-serif;   /* Clean, modern, minimal */
  --font-body: 'Geist', sans-serif;      /* Same for consistency */
  --font-mono: 'Geist Mono', monospace;  /* Code/timestamps */
  
  /* Simplified Size Scale */
  --text-sm: 0.875rem;  /* 14px - Metadata */
  --text-base: 1rem;    /* 16px - Primary text */
  --text-lg: 1.125rem;  /* 18px - Subheadings */
  --text-xl: 1.5rem;    /* 24px - Headings */
  --text-2xl: 2rem;     /* 32px - Page titles */
  
  /* Weight System (Minimal) */
  --font-normal: 400;   /* All body text */
  --font-semibold: 600; /* Headings only */
}
```

### 3. Layout Patterns (Asymmetry and Hierarchy)

**❌ PROHIBITED LAYOUTS:**
- Standard centered container with max-w-7xl
- Symmetric 50/50 splits
- Predictable hero sections with centered text
- Generic card grids (3 columns, equal heights)

**✅ REQUIRED LAYOUTS:**

**BidDeed.AI Landing Page:**
```
┌─────────────────────────────────────────────┐
│ ASYMMETRIC HERO (60/40 split)              │
│ ┌──────────────────────┐ ┌──────────────┐  │
│ │ Text-heavy left      │ │ Data viz     │  │
│ │ (Main message)       │ │ (Trust cue)  │  │
│ └──────────────────────┘ └──────────────┘  │
├─────────────────────────────────────────────┤
│ MASONRY FEATURE GRID (not equal heights)   │
│ ┌──────┐ ┌──────────┐ ┌──────┐            │
│ │  A   │ │    B     │ │  C   │            │
│ │      │ │          │ │      │            │
│ └──────┘ │          │ └──────┘            │
│          └──────────┘                      │
├─────────────────────────────────────────────┤
│ DATA-DRIVEN SECTION (technical dominance)  │
│ ┌─────────────────────────────────────┐    │
│ │ Table/Chart (70% width)             │    │
│ │ ┌────────────────┐ ┌──────────┐    │    │
│ │ │ Metrics        │ │ Sidebar  │    │    │
│ └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**Life OS Dashboard:**
```
┌─────────────────────────────────────────────┐
│ SIDEBAR (Fixed, 280px)  │ MAIN CONTENT     │
│ ┌──────────────────┐    │ ┌──────────────┐ │
│ │ Task States      │    │ │ Active Task  │ │
│ │ - Initiated      │    │ │              │ │
│ │ - In Progress    │    │ └──────────────┘ │
│ │ - Completed      │    │ ┌──────────────┐ │
│ └──────────────────┘    │ │ Context      │ │
│ ┌──────────────────┐    │ │ Timeline     │ │
│ │ Quick Stats      │    │ └──────────────┘ │
│ └──────────────────┘    │                  │
└─────────────────────────────────────────────┘
```

### 4. Spacing System (Mathematical Rigor)

**❌ PROHIBITED:**
- Random spacing (p-3, p-4, p-6 without system)
- Inconsistent gaps between sections

**✅ REQUIRED:**

Use 4px base unit (Tailwind default) but apply consistently:

```css
:root {
  /* Spacing Scale (Powers of 2 + Golden Ratio adjustments) */
  --space-1: 0.25rem;  /* 4px - Tiny gaps */
  --space-2: 0.5rem;   /* 8px - Compact spacing */
  --space-3: 0.75rem;  /* 12px - Small spacing */
  --space-4: 1rem;     /* 16px - Base spacing */
  --space-6: 1.5rem;   /* 24px - Medium spacing */
  --space-8: 2rem;     /* 32px - Large spacing */
  --space-12: 3rem;    /* 48px - Section spacing */
  --space-16: 4rem;    /* 64px - Hero spacing */
  --space-24: 6rem;    /* 96px - Major section breaks */
}
```

**Application Rules:**
- Inside components: `space-4` (16px)
- Between components: `space-8` (32px)
- Between sections: `space-16` or `space-24` (64px or 96px)

### 5. Component States (Micro-interactions)

**❌ PROHIBITED:**
- Default Tailwind transitions (duration-200)
- No hover states
- Instant state changes

**✅ REQUIRED:**

**Button States:**
```tsx
<button className="
  bg-primary text-primary-foreground
  px-6 py-3 rounded-lg
  font-semibold tracking-tight
  
  /* Hover state */
  hover:bg-primary/90
  hover:shadow-lg
  hover:scale-[1.02]
  
  /* Active state */
  active:scale-[0.98]
  active:shadow-sm
  
  /* Focus state (keyboard navigation) */
  focus-visible:outline-none
  focus-visible:ring-2
  focus-visible:ring-primary
  focus-visible:ring-offset-2
  
  /* Transitions */
  transition-all duration-150 ease-out
">
  Action Button
</button>
```

**Card Hover Effects:**
```tsx
<div className="
  bg-card border border-border
  rounded-xl p-6
  
  /* Subtle elevation on hover */
  hover:shadow-xl
  hover:border-primary/20
  hover:-translate-y-1
  
  /* Smooth transition */
  transition-all duration-200 ease-out
">
  Card Content
</div>
```

---

## DOMAIN-SPECIFIC DESIGN RULES

### BidDeed.AI (Foreclosure Auction Intelligence)

**Visual Language:**
- Professional, data-driven, trustworthy
- Heavy use of tables, charts, metrics
- Legal/financial color palette (navy, gold, teal)
- High information density (investors want data)

**Component Priorities:**
1. Data tables with sorting/filtering
2. Property comparison cards (side-by-side)
3. ML confidence indicators (badges, progress bars)
4. Alert states for critical information (lien priority warnings)

**Typography Hierarchy:**
- Headings: `font-display` (Outfit) for authority
- Body: `font-body` (Inter) for readability
- Data: `font-mono` (JetBrains Mono) for precision

### Life OS (ADHD Task Management)

**Visual Language:**
- Minimalist, distraction-free, calm
- Clear task state differentiation (color-coded)
- High contrast for focus (pure white bg, pure black text)
- Generous whitespace (reduces cognitive load)

**Component Priorities:**
1. Task cards with clear state indicators
2. Countdown timers (visual urgency cues)
3. Progress bars (completion visualization)
4. Intervention alerts (gentle, non-intrusive)

**Typography Hierarchy:**
- All text: `font-body` (Geist) for consistency
- Emphasis: `font-semibold` only (no bold)
- Timestamps: `font-mono` (Geist Mono)

### Zoning Analyst AI (Site Plan Development)

**Visual Language:**
- Technical, authoritative, document-centric
- Legal framework emphasis
- High readability for long-form content
- Professional color palette (navy, gray, green for approval states)

**Component Priorities:**
1. Document upload/viewer
2. Jurisdiction selector (dropdown with search)
3. Zoning code reference tables
4. Approval workflow visualization (stages)

**Typography Hierarchy:**
- Headings: `font-display` for authority
- Body: `font-body` for long-form reading
- Code references: `font-mono` for legal citations

---

## ANTI-PATTERN DETECTION

### Red Flags During Code Review

If you see ANY of these, REJECT the code:

1. **Generic Colors:**
   ```tsx
   className="bg-blue-500"  // ❌ WRONG - Use theme variables
   className="bg-primary"   // ✅ CORRECT
   ```

2. **Inconsistent Spacing:**
   ```tsx
   <div className="p-5">     // ❌ WRONG - Not in our scale
   <div className="p-4">     // ✅ CORRECT - Uses space-4
   ```

3. **Missing Hover States:**
   ```tsx
   <button className="bg-primary"> // ❌ WRONG - No interaction
   <button className="bg-primary hover:bg-primary/90 hover:shadow-lg"> // ✅ CORRECT
   ```

4. **Generic Fonts:**
   ```tsx
   className="font-sans"    // ❌ WRONG - Generic
   className="font-display" // ✅ CORRECT - Semantic
   ```

5. **Symmetric Layouts:**
   ```tsx
   <div className="grid grid-cols-2"> // ❌ WRONG - Boring 50/50
   <div className="grid grid-cols-[1.618fr_1fr]"> // ✅ CORRECT - Golden ratio
   ```

---

## CODE GENERATION RULES

### Before Generating ANY UI Code:

1. **Load Theme File**: Always read `/styles/theme.css` first
2. **Confirm Domain**: BidDeed.AI, Life OS, or Zoning Analyst?
3. **Check Existing Components**: Reuse patterns from `shared/ui/`
4. **Design Rationale**: Write 1 sentence explaining design choice

### During Code Generation:

**Include in Every Component:**
```tsx
/**
 * ComponentName
 * 
 * Domain: [BidDeed.AI | Life OS | Zoning Analyst AI]
 * Purpose: [One sentence describing what this component does]
 * Design Rationale: [One sentence explaining design choices]
 */
```

**Example:**
```tsx
/**
 * PropertyComparisonCard
 * 
 * Domain: BidDeed.AI
 * Purpose: Side-by-side comparison of foreclosure properties with ML scores
 * Design Rationale: Asymmetric layout (60/40) with primary property emphasized,
 * uses masonry grid to reflect data hierarchy, navy/teal color scheme for
 * professional financial aesthetic
 */
export function PropertyComparisonCard({ properties }: Props) {
  // Component implementation
}
```

### After Code Generation:

**Self-Review Checklist:**
- [ ] Uses theme CSS variables (no hardcoded colors)
- [ ] Follows spacing scale (no arbitrary values)
- [ ] Has hover/focus/active states
- [ ] Uses semantic font classes
- [ ] Has design rationale comment
- [ ] Passes WCAG AAA contrast check
- [ ] Uses asymmetric/hierarchical layout
- [ ] No generic Tailwind defaults

---

## ACCESSIBILITY REQUIREMENTS

### Contrast Ratios (WCAG AAA)

**Text Sizes:**
- Body text (16px+): 7:1 contrast ratio
- Large text (24px+): 4.5:1 contrast ratio

**Interactive Elements:**
- Buttons: 4.5:1 minimum
- Form inputs: 3:1 minimum for borders

**Automated Check:**
Use `oklch()` color space which ensures perceptual uniformity. All theme colors MUST pass contrast checks.

### Keyboard Navigation

**Every interactive element MUST have:**
```tsx
focus-visible:outline-none
focus-visible:ring-2
focus-visible:ring-primary
focus-visible:ring-offset-2
```

### Screen Reader Support

**Semantic HTML:**
```tsx
<button> // ✅ CORRECT - Accessible by default
<div onClick={...}> // ❌ WRONG - Not keyboard accessible
```

**ARIA Labels for Icon-Only Buttons:**
```tsx
<button aria-label="Delete property">
  <TrashIcon />
</button>
```

---

## DESIGN SYSTEM MAINTENANCE

### When Adding New Colors

1. Generate in OKLCH color space using TweakCN
2. Test contrast ratios: https://www.whocanuse.com/
3. Document in `theme.css` with comments
4. Update Figma/design system (if applicable)

### When Adding New Components

1. Check `shared/ui/` for existing patterns
2. Document design rationale in component file
3. Add to Storybook (if BidDeed.AI has one)
4. Update FRONTEND_DESIGN.md with new pattern

### When Updating Existing Components

1. Verify theme consistency across all variants
2. Test hover/focus/active states
3. Check responsive behavior (mobile, tablet, desktop)
4. Update documentation if API changes

---

## INTEGRATION WITH KING MODE

When ULTRATHINK is triggered:

**PHASE 4: Component Architecture** should include:

```markdown
### UI/UX Design

**Color Palette:**
- Primary use case: [Button actions, links]
- Secondary use case: [Backgrounds, borders]
- Accent use case: [Highlights, badges]

**Typography:**
- Display font: [Headings, hero text]
- Body font: [Paragraphs, descriptions]
- Mono font: [Code, data, timestamps]

**Layout Strategy:**
- Asymmetric hero: [60/40 split, text-heavy left]
- Component grid: [Masonry, not equal heights]
- Spacing: [16px inside, 32px between, 64px sections]

**Micro-interactions:**
- Button hover: [Scale 1.02, shadow-lg, bg opacity 90%]
- Card hover: [Translate -4px, shadow-xl, border accent]
```

---

## TWEAKCN WORKFLOW

### Step-by-Step Process

1. **Visit TweakCN**: https://tweakcn.com/
2. **Select Base Preset**: Choose from preset themes
3. **Customize for Domain**:
   - BidDeed.AI: Navy/teal/gold palette
   - Life OS: Purple/green minimalist
   - Zoning Analyst: Navy/gray/green professional
4. **Export CSS Variables**: Click "Copy Code"
5. **Paste to `theme.css`**: Replace `:root` block
6. **Test Accessibility**: Run contrast checker
7. **Commit to GitHub**: `git add styles/theme.css && git commit`

### TweakCN Features to Use

- **Color Mode Toggle**: Generate light AND dark themes
- **OKLCH Support**: Ensure perceptual uniformity
- **Tailwind v4**: Use latest version
- **Preset Library**: Start from curated themes
- **Live Preview**: See changes in real-time

---

## EXAMPLE: BIDDEED.AI LANDING PAGE DESIGN

### Before (Generic)

```tsx
// ❌ GENERIC BOOTSTRAP LOOK
<div className="container mx-auto max-w-7xl px-4 py-16">
  <div className="grid grid-cols-2 gap-8">
    <div>
      <h1 className="text-4xl font-bold text-blue-600">
        BidDeed.AI
      </h1>
      <p className="text-gray-600 mt-4">
        Foreclosure auction intelligence platform
      </p>
      <button className="bg-blue-500 text-white px-6 py-3 rounded mt-6">
        Get Started
      </button>
    </div>
    <div>
      <img src="/hero.jpg" alt="Hero" />
    </div>
  </div>
</div>
```

### After (Bespoke BidDeed.AI)

```tsx
// ✅ BESPOKE PROFESSIONAL DESIGN
<div className="relative overflow-hidden bg-background">
  {/* Asymmetric Hero - 60/40 Split */}
  <div className="max-w-[1600px] mx-auto px-8 py-24">
    <div className="grid grid-cols-[1.5fr_1fr] gap-16 items-center">
      {/* Text-Heavy Left (60%) */}
      <div className="space-y-8">
        <div className="inline-block px-4 py-2 bg-secondary/10 border border-secondary/20 rounded-full">
          <span className="text-sm font-medium text-secondary">
            The Everest Ascent™ Methodology
          </span>
        </div>
        
        <h1 className="font-display text-5xl md:text-6xl font-bold text-foreground leading-tight">
          Agentic AI for{" "}
          <span className="text-primary">Foreclosure</span>{" "}
          Auction Intelligence
        </h1>
        
        <p className="text-lg text-muted-foreground leading-relaxed">
          12-stage autonomous pipeline analyzes properties, predicts outcomes,
          and calculates optimal maximum bids using XGBoost ML and real-time
          lien discovery—saving investors $100K+ annually.
        </p>
        
        <div className="flex gap-4">
          <button className="
            bg-primary text-primary-foreground
            px-8 py-4 rounded-lg
            font-semibold tracking-tight
            hover:bg-primary/90 hover:shadow-xl hover:scale-[1.02]
            active:scale-[0.98]
            transition-all duration-150 ease-out
          ">
            Schedule Demo
          </button>
          
          <button className="
            bg-secondary/10 text-secondary
            px-8 py-4 rounded-lg
            font-semibold tracking-tight border border-secondary/20
            hover:bg-secondary/20 hover:border-secondary/40
            transition-all duration-150 ease-out
          ">
            View Documentation
          </button>
        </div>
      </div>
      
      {/* Data Visualization Right (40%) */}
      <div className="relative">
        <div className="bg-card border border-border rounded-2xl p-8 shadow-2xl">
          <div className="space-y-6">
            {/* ML Accuracy Metric */}
            <div className="flex justify-between items-center">
              <span className="font-mono text-sm text-muted-foreground">
                ML Prediction Accuracy
              </span>
              <span className="font-display text-3xl font-bold text-primary">
                64.4%
              </span>
            </div>
            
            {/* ROI Metric */}
            <div className="flex justify-between items-center">
              <span className="font-mono text-sm text-muted-foreground">
                Annual ROI (Internal Use)
              </span>
              <span className="font-display text-3xl font-bold text-success">
                100x
              </span>
            </div>
            
            {/* Cost Savings */}
            <div className="flex justify-between items-center">
              <span className="font-mono text-sm text-muted-foreground">
                Monthly Cost Savings
              </span>
              <span className="font-display text-3xl font-bold text-secondary">
                $2,500
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## FINAL DIRECTIVES

### For Every UI Component:

1. **No Generic Defaults**: If it looks like a template, redesign it
2. **Theme First**: Always load `theme.css` variables
3. **Asymmetry**: Avoid 50/50 splits, use golden ratio (1.618:1)
4. **Micro-interactions**: Every button needs hover/focus/active states
5. **Accessibility**: WCAG AAA compliance is non-negotiable
6. **Design Rationale**: One sentence explaining why this design

### For Every Color Choice:

1. **Use Theme Variables**: `bg-primary`, never `bg-blue-500`
2. **OKLCH Space**: Generate colors in TweakCN using OKLCH
3. **Contrast Check**: Verify 7:1 ratio for body text
4. **Domain Alignment**: Navy/teal/gold for BidDeed.AI, purple/green for Life OS

### For Every Layout:

1. **Hierarchical**: Emphasize primary content (60%+ width)
2. **Masonry Grids**: Not equal heights, reflect importance
3. **Spacing Scale**: Use 4/8/16/24px increments only
4. **Breakpoints**: Mobile-first, tablet (768px), desktop (1024px), wide (1536px)

---

**The goal is not perfection—it's distinctiveness. Every interface should be recognizable as BidDeed.AI or Life OS at a glance, not mistaken for a generic template.**
