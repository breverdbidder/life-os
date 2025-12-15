// pwa-register.js - PWA Registration for BidDeed.AI
// Add to index.html: <script src="/pwa-register.js"></script>

(function() {
  'use strict';

  // Check if service workers are supported
  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] Service Workers not supported');
    return;
  }

  // Register service worker
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });
      
      console.log('[PWA] Service Worker registered:', registration.scope);

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('[PWA] New Service Worker installing...');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New content available, show update prompt
            showUpdatePrompt();
          }
        });
      });

    } catch (error) {
      console.error('[PWA] Service Worker registration failed:', error);
    }
  });

  // Handle update prompt
  function showUpdatePrompt() {
    const updateBanner = document.createElement('div');
    updateBanner.id = 'pwa-update-banner';
    updateBanner.innerHTML = `
      <style>
        #pwa-update-banner {
          position: fixed;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 16px 24px;
          border-radius: 12px;
          box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
          display: flex;
          align-items: center;
          gap: 16px;
          z-index: 10000;
          font-family: system-ui, -apple-system, sans-serif;
          animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
          from { transform: translateX(-50%) translateY(100px); opacity: 0; }
          to { transform: translateX(-50%) translateY(0); opacity: 1; }
        }
        #pwa-update-banner button {
          background: white;
          color: #667eea;
          border: none;
          padding: 8px 16px;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s;
        }
        #pwa-update-banner button:hover {
          transform: scale(1.05);
        }
        #pwa-update-banner .dismiss {
          background: transparent;
          color: white;
          opacity: 0.8;
        }
      </style>
      <span>🚀 New version available!</span>
      <button onclick="window.location.reload()">Update</button>
      <button class="dismiss" onclick="this.parentElement.remove()">Later</button>
    `;
    document.body.appendChild(updateBanner);
  }

  // Install prompt handling (Add to Home Screen)
  let deferredPrompt;
  
  window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA] beforeinstallprompt fired');
    e.preventDefault();
    deferredPrompt = e;
    
    // Show custom install button after delay
    setTimeout(() => {
      if (deferredPrompt) {
        showInstallPrompt();
      }
    }, 30000); // Show after 30 seconds
  });

  function showInstallPrompt() {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return;
    }

    const installBanner = document.createElement('div');
    installBanner.id = 'pwa-install-banner';
    installBanner.innerHTML = `
      <style>
        #pwa-install-banner {
          position: fixed;
          bottom: 20px;
          right: 20px;
          background: #1a1a2e;
          border: 1px solid #667eea;
          color: white;
          padding: 20px;
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          max-width: 320px;
          z-index: 10000;
          font-family: system-ui, -apple-system, sans-serif;
          animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
          from { transform: translateX(100px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        #pwa-install-banner h4 {
          margin: 0 0 8px 0;
          font-size: 18px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        #pwa-install-banner p {
          margin: 0 0 16px 0;
          font-size: 14px;
          opacity: 0.8;
          line-height: 1.4;
        }
        #pwa-install-banner .actions {
          display: flex;
          gap: 12px;
        }
        #pwa-install-banner button {
          flex: 1;
          padding: 10px 16px;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        #pwa-install-banner .install-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
        }
        #pwa-install-banner .install-btn:hover {
          transform: scale(1.02);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        #pwa-install-banner .dismiss-btn {
          background: transparent;
          color: #667eea;
          border: 1px solid #667eea;
        }
      </style>
      <h4>📱 Install BidDeed.AI</h4>
      <p>Add to your home screen for instant access to foreclosure intelligence, offline support, and push notifications.</p>
      <div class="actions">
        <button class="dismiss-btn" onclick="this.closest('#pwa-install-banner').remove()">Not Now</button>
        <button class="install-btn" id="pwa-install-btn">Install</button>
      </div>
    `;
    document.body.appendChild(installBanner);

    document.getElementById('pwa-install-btn').addEventListener('click', async () => {
      if (!deferredPrompt) return;
      
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log('[PWA] Install prompt outcome:', outcome);
      
      deferredPrompt = null;
      installBanner.remove();
    });
  }

  // Track install success
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed successfully');
    deferredPrompt = null;
    
    // Track in analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'pwa_install', { event_category: 'PWA' });
    }
  });

  // Check if running as PWA
  if (window.matchMedia('(display-mode: standalone)').matches) {
    console.log('[PWA] Running in standalone mode');
    document.body.classList.add('pwa-standalone');
  }

  // Push notification permission request
  window.requestPushPermission = async function() {
    if (!('PushManager' in window)) {
      console.log('[PWA] Push notifications not supported');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        console.log('[PWA] Push notification permission granted');
        await subscribeToPush();
        return true;
      }
      return false;
    } catch (error) {
      console.error('[PWA] Push permission error:', error);
      return false;
    }
  };

  async function subscribeToPush() {
    const registration = await navigator.serviceWorker.ready;
    
    // For production, use your VAPID public key
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        // Replace with your VAPID public key
        'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U'
      )
    });

    console.log('[PWA] Push subscription:', subscription);
    
    // Send subscription to your server
    // await fetch('/api/push/subscribe', {
    //   method: 'POST',
    //   body: JSON.stringify(subscription),
    //   headers: { 'Content-Type': 'application/json' }
    // });
  }

  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

})();
