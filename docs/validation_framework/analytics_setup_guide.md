# Analytics Setup Guide

## Google Analytics 4 (Free)

1. Go to analytics.google.com
2. Create property
3. Get tracking ID (G-XXXXXXXXXX)
4. Add to landing page <head>:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Hotjar (Free tier: 35 sessions/day)

1. Sign up at hotjar.com
2. Get site ID
3. Add to landing page:

```html
<script>
  (function(h,o,t,j,a,r){
    h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
    h._hjSettings={hjid:YOUR_SITE_ID,hjsv:6};
    a=o.getElementsByTagName('head')[0];
    r=o.createElement('script');r.async=1;
    r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
    a.appendChild(r);
  })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
</script>
```

## Event Tracking

Add to each CTA button:

```javascript
// Primary CTA
gtag('event', 'click', {
  'event_category': 'CTA',
  'event_label': 'Primary - Get Early Access'
});

// Secondary CTA  
gtag('event', 'click', {
  'event_category': 'CTA',
  'event_label': 'Secondary - Join Waitlist'
});

// Tertiary CTA
gtag('event', 'click', {
  'event_category': 'CTA',
  'event_label': 'Tertiary - Schedule Demo'
});
```

## What to Monitor Daily

1. **Visits:** Total and unique
2. **Conversion rate:** CTA clicks / visits
3. **Bounce rate:** <70% is good
4. **Time on page:** >60 sec is good
5. **Top sources:** Where traffic comes from
6. **Heatmaps:** Where users look/click

Update metrics_dashboard.csv daily.
