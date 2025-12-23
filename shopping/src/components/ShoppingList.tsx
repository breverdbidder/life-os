/**
 * Life OS Shopping List Component
 * Integrates with Instacart via the shopping worker API
 * 
 * Usage in Life OS chat.html:
 * <ShoppingList items={parsedItems} store="costco" />
 */

import React, { useState } from 'react';

interface ShoppingItem {
  name: string;
  quantity?: number;
  unit?: string;
  brand?: string;
  category?: string;
}

interface ShoppingListProps {
  items?: ShoppingItem[];
  rawText?: string;
  store?: 'costco' | 'walmart' | 'any';
  title?: string;
  onSuccess?: (url: string) => void;
  onError?: (error: string) => void;
}

// Worker API endpoint (Cloudflare Pages)
const SHOPPING_API = 'https://life-os-aiy.pages.dev/api/shopping';

export function ShoppingList({ 
  items, 
  rawText, 
  store = 'any',
  title,
  onSuccess,
  onError
}: ShoppingListProps) {
  const [loading, setLoading] = useState(false);
  const [instacartUrl, setInstacartUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [parsedItems, setParsedItems] = useState<ShoppingItem[]>(items || []);

  // Parse raw text if provided
  const parseText = async () => {
    if (!rawText) return;
    
    try {
      const response = await fetch(`${SHOPPING_API}/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: rawText })
      });
      
      const data = await response.json();
      if (data.success) {
        setParsedItems(data.items);
      }
    } catch (err) {
      console.error('Parse error:', err);
    }
  };

  // Create Instacart shopping list
  const createList = async () => {
    setLoading(true);
    setError(null);

    const listTitle = title || `${store === 'costco' ? 'Costco' : store === 'walmart' ? 'Walmart' : ''} Shopping List - ${new Date().toLocaleDateString()}`;

    try {
      const response = await fetch(`${SHOPPING_API}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: listTitle,
          items: rawText,
          structured_items: rawText ? undefined : parsedItems,
          store,
          log_to_supabase: true
        })
      });

      const data = await response.json();
      
      if (data.success && data.url) {
        setInstacartUrl(data.url);
        if (data.items) setParsedItems(data.items);
        onSuccess?.(data.url);
      } else {
        throw new Error(data.error || 'Failed to create list');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Store badge colors
  const storeColors = {
    costco: 'bg-red-600',
    walmart: 'bg-blue-600',
    any: 'bg-gray-600'
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 max-w-md">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          🛒 Shopping List
        </h3>
        {store !== 'any' && (
          <span className={`${storeColors[store]} text-white text-xs px-2 py-1 rounded`}>
            {store.charAt(0).toUpperCase() + store.slice(1)}
          </span>
        )}
      </div>

      {/* Items List */}
      {parsedItems.length > 0 && (
        <ul className="mb-4 space-y-2">
          {parsedItems.map((item, idx) => (
            <li key={idx} className="flex items-center text-sm text-gray-700">
              <span className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center mr-2 text-xs">
                {item.quantity || 1}
              </span>
              <span>{item.name}</span>
              {item.brand && (
                <span className="text-gray-400 text-xs ml-1">({item.brand})</span>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Success - Instacart Link */}
      {instacartUrl && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
          <p className="text-sm text-green-700 mb-2">✅ List created!</p>
          <a 
            href={instacartUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
              <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
            </svg>
            Open in Instacart
          </a>
        </div>
      )}

      {/* Action Button */}
      {!instacartUrl && (
        <button
          onClick={createList}
          disabled={loading || (parsedItems.length === 0 && !rawText)}
          className={`
            w-full py-2 px-4 rounded font-medium transition-colors
            ${loading 
              ? 'bg-gray-300 cursor-not-allowed' 
              : 'bg-orange-500 hover:bg-orange-600 text-white'
            }
          `}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating...
            </span>
          ) : (
            '🛒 Send to Instacart'
          )}
        </button>
      )}

      {/* Footer note */}
      <p className="text-xs text-gray-400 mt-3 text-center">
        Opens Instacart to complete your order
      </p>
    </div>
  );
}

export default ShoppingList;
