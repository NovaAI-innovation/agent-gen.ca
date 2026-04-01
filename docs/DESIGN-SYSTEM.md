# agent-gen.ca Design System (Shadcn + Cyber-Futuristic)

## 🎨 Design Tokens

### Colors (Tailwind + CSS Vars)
```css
:root {
  /* Core */
  --background: 10 10 10;     /* #0a0a0a */
  --surface: 26 26 26;        /* #1a1a1a */
  --glass: 0 0% 100%;         /* rgba(255,255,255,0.1) */
  --text: 0 0% 100%;          /* #ffffff */
  --text-secondary: 0 0% 69%; /* #b0b0b0 */
  
  /* Neon */
  --neon-cyan: 189 100% 60%;  /* #00f5ff */
  --neon-magenta: 330 100% 64%; /* #ff00ff */
  --neon-lime: 150 100% 54%;  /* #39ff14 */
  
  /* Glows */
  --glow-cyan: 189 100% 60% / 0.3;
  --glow-magenta: 330 100% 64% / 0.3;
  --glow-lime: 150 100% 54% / 0.3;
}
```

### Typography
```css
/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Inter', sans-serif;
}

/* Sizes */
--font-xs: 0.75rem;
--font-sm: 0.875rem;
--font-base: 1rem;
--font-lg: 1.125rem;
--font-xl: 1.25rem;
--font-2xl: 1.5rem;
--font-3xl: 1.875rem;
--font-4xl: 2.25rem;
```

### Spacing (8pt Scale)
```css
--space-xs: 0.25rem;  /* 4px */
--space-sm: 0.5rem;   /* 8px */
--space-md: 1rem;     /* 16px */
--space-lg: 1.5rem;   /* 24px */
--space-xl: 2rem;     /* 32px */
--space-2xl: 3rem;    /* 48px */
```

### Shadows & Effects
```css
/* Glassmorphism */
.glass {
  background: rgb(var(--glass) / 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgb(var(--glass) / 0.2);
}

/* Neon Glow */
.neon-cyan { 
  box-shadow: 0 0 20px rgb(var(--neon-cyan) / 0.5);
}
.neon-magenta { 
  box-shadow: 0 0 20px rgb(var(--neon-magenta) / 0.5);
}
.neon-lime { 
  box-shadow: 0 0 20px rgb(var(--neon-lime) / 0.5);
}

/* Terminal Scanline */
@keyframes scanline {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.terminal { animation: scanline 3s infinite; }
```

## 🧩 Shadcn Component Overrides

### Button (Neon Variants)
```tsx
import { Button } from '@/components/ui/button'

// Usage
<Button className="neon-cyan bg-gradient-to-r from-cyan-400 to-blue-500 text-black font-mono shadow-lg hover:shadow-cyan-500/50">
  Deploy Agent
</Button>

<Button variant="ghost" className="text-cyan-400 hover:text-white hover:neon-cyan border-cyan-400/30">
  Connect Wallet
</Button>
```

### Card (Glassmorphism)
```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

<Card className="glass border-0 neon-cyan backdrop-blur-xl">
  <CardHeader>
    <CardTitle className="text-2xl font-mono text-cyan-400">Agent Marketplace</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Input (Terminal Style)
```tsx
import { Input } from '@/components/ui/input'

<Input 
  className="bg-black/50 border-cyan-500/50 text-mono font-mono placeholder:text-cyan-400/50 focus:border-cyan-400 focus:neon-cyan"
  placeholder="Enter agent prompt..."
/>
```

### Badge (Neon Labels)
```tsx
import { Badge } from '@/components/ui/badge'

<Badge className="bg-gradient-to-r from-lime-400 to-emerald-500 text-black font-mono neon-lime">
  Live
</Badge>
<Badge className="bg-magenta-500/20 text-magenta-400 border-magenta-500/30 neon-magenta">
  Premium
</Badge>
```

## ⚙️ Tailwind Config (tailwind.config.js)
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        cyan: { 400: '#00f5ff' },
        magenta: { 500: '#ff00ff' },
        lime: { 400: '#39ff14' },
      },
      fontFamily: {
        mono: ['JetBrains Mono'],
        sans: ['Inter'],
      },
      backdropBlur: {
        xs: '2px',
      }
    }
  },
  plugins: [require('@tailwindcss/typography')],
}
```

## 🎭 Global CSS (globals.css)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

@layer base {
  :root {
    /* CSS Vars from tokens above */
  }
  
  * { @apply border-border; }
  body { 
    @apply bg-background text-foreground font-sans; 
  }
}

@layer components {
  .glass { /* Glassmorphism */ }
  .neon-cyan, .neon-magenta, .neon-lime { /* Glows */ }
  .terminal { /* Scanline */ }
}
```

## 📱 Responsive Breakpoints
```css
/* Tailwind defaults + custom */
--breakpoint-xs: 475px;
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

**Production Ready for Next.js 15 + Shadcn/UI** ✅
**Copy to frontend/lib/utils.ts, tailwind.config.js, globals.css**
