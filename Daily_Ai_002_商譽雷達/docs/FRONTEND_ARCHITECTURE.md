# Sentinel ECXIP Frontend Architecture

## Overview

The Sentinel ECXIP frontend is a vanilla JavaScript SPA (Single Page Application) featuring Apple Frosted Glass design with comprehensive i18n support.

## Technology Stack

- **Vanilla JavaScript** (no frameworks) using IIFE module pattern
- **CSS3** with CSS custom properties for theming
- **Apple Frosted Glass** (glassmorphism) design language
- **i18n Framework** for multi-language support

## Project Structure

```
frontend/
├── public/
│   └── index.html              # Main HTML with data-i18n attributes
├── i18n/
│   ├── index.js                # I18n engine (t(), setLocale(), events)
│   ├── zh-TW.js                # Traditional Chinese (260+ keys)
│   └── en-US.js                # English (260+ keys)
└── src/
    ├── app.js                  # Main entry point, navigation, initialization
    ├── data/
    │   └── mockData.js         # Simulated review data, crisis scenarios
    ├── services/
    │   ├── api.js              # REST API client with mock fallback
    │   └── websocket.js        # WebSocket manager with auto-reconnect
    ├── stores/
    │   └── dashboardStore.js   # Reactive state management (pub/sub)
    ├── styles/
    │   └── app.css             # Complete stylesheet (Apple Frosted Glass)
    └── components/
        ├── shared/
        │   ├── utils.js        # Utility functions
        │   └── languageSwitcher.js  # Language toggle widget
        ├── dashboard/
        │   └── metrics.js      # Metric cards, risk bars, circular charts
        ├── voc/
        │   └── voiceStream.js  # Real-time voice stream, action modals
        ├── cx/
        │   └── journeyMap.js   # Customer journey diagnostic map
        ├── brand-manager/
        │   └── aiTerminal.js   # AI terminal, crisis scenarios, SOP/PR/Legal tabs
        ├── sandbox/
        │   └── nlpSandbox.js   # NLP text analysis sandbox
        └── executive/
            ├── morningBrief.js     # Executive briefing center
            ├── storeRanking.js     # Store ranking table
            ├── predictionPanel.js  # 7-day forecast panels
            └── learningPanel.js    # AI learning memory panel
```

## Architecture Patterns

### Module Pattern (IIFE)
All components use the IIFE (Immediately Invoked Function Expression) pattern:
```javascript
var ComponentName = (function() {
  // Private state and methods
  function init() { ... }
  function publicMethod() { ... }
  
  // Public API
  return { init, publicMethod };
})();
```

### State Management
DashboardStore provides reactive state management with observer pattern:
```javascript
// Subscribe to state changes
DashboardStore.subscribe(function(state, prevState) { ... });
// Update state
DashboardStore.setSelectedStore('xinyi');
```

### i18n Integration
```javascript
// Static text in HTML
<span data-i18n="nav.dashboard">品牌決策總覽</span>

// Dynamic text in JavaScript
el.textContent = I18n.t('voc.processReview');

// Parameterized text
I18n.t('dashboard.riskValue', { value: 42 })

// Listen for locale changes
I18nEvents.on('localeChanged', function() { reRender(); });
```

### API Service Layer
```javascript
// Auto-fallback to mock data when backend is unavailable
ApiService.executive.getMorningBrief()
  .then(data => render(data))
  .catch(() => loadMockData());
```

## Component Communication

Components communicate through the shared DashboardStore and direct DOM manipulation:

```
User Action → Component → DashboardStore.setState()
                                ↓
                        Subscribers notified
                                ↓
                        Other components re-render
```

## Navigation

Single-page navigation using scroll-to-section with smooth behavior:
- 8 navigation items in sidebar
- Active state tracking
- Sections: Dashboard, Morning Brief, Store Ranking, Predictions, Learning, Journey, Voice Stream, Sandbox

## Design System

### Color Tokens
- Primary: #0071e3 (Apple Blue)
- Success: #34c759 (Green)
- Warning: #ff9500 (Amber)
- Danger: #ff3b30 (Red)
- Purple: #af52de (Violet)

### Glassmorphism
- Background: rgba(255, 255, 255, 0.65)
- Backdrop filter: blur(25px)
- Border: 1px solid rgba(0, 0, 0, 0.08)
- Box shadow: subtle elevation

## Adding New Components

1. Create component file in appropriate subdirectory
2. Use IIFE pattern for encapsulation
3. Export public init() method
4. Add <script> tag to index.html
5. Call init() from app.js initAll()
6. Add translation keys to zh-TW.js and en-US.js
```
