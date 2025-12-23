/**
 * Life OS - Instacart Shopping List Integration
 * Uses Instacart Developer Platform API to create shoppable lists
 * 
 * Stack: TypeScript + Cloudflare Workers
 * API: https://connect.instacart.com/idp/v1/products/products_link
 */

interface LineItem {
  name: string;
  quantity?: number;
  unit?: string;
  display_text?: string;
  brand_filters?: string[];
}

interface ShoppingListRequest {
  title: string;
  line_items: LineItem[];
  image_url?: string;
  link_type?: string;
  landing_page_configuration?: {
    partner_linkback_url?: string;
    enable_pantry_items?: boolean;
  };
}

interface InstacartResponse {
  products_link_url: string;
  expires_at?: string;
}

interface ShoppingItem {
  name: string;
  quantity?: number;
  unit?: string;
  brand?: string;
  category?: string;
}

// Costco-specific product mappings for better matching
const COSTCO_PRODUCT_MAPPINGS: Record<string, { name: string; brand?: string; unit?: string }> = {
  'foilrite heavy duty pans': {
    name: 'Heavy Duty Aluminum Pans with Lids',
    brand: 'Foilrite',
    unit: 'pack'
  },
  'softsoap hand soap': {
    name: 'Liquid Hand Soap Refill',
    brand: 'Softsoap',
    unit: 'bottle'
  },
  'sugar in the raw': {
    name: 'Turbinado Raw Cane Sugar',
    brand: 'Sugar in the Raw'
  },
  'coffee-mate original powder': {
    name: 'Coffee Creamer Powder Original',
    brand: 'Coffee-mate',
    unit: 'oz'
  },
  'coffee mate powder': {
    name: 'Coffee Creamer Powder Original',
    brand: 'Coffee-mate',
    unit: 'oz'
  }
};

export class InstacartClient {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, isDev = false) {
    this.apiKey = apiKey;
    this.baseUrl = isDev 
      ? 'https://connect.dev.instacart.tools'
      : 'https://connect.instacart.com';
  }

  /**
   * Parse natural language shopping list into structured items
   */
  parseShoppingList(rawList: string): ShoppingItem[] {
    const lines = rawList.split('\n').filter(line => line.trim());
    const items: ShoppingItem[] = [];

    for (const line of lines) {
      const cleanLine = line.replace(/^[-•*]\s*/, '').trim();
      if (!cleanLine) continue;

      // Parse quantity patterns like "5 packs", "(2)", "x3"
      const qtyMatch = cleanLine.match(/\((\d+)\)|x(\d+)|(\d+)\s*(pack|box|bottle|gallon|lb|oz|count)s?/i);
      let quantity = 1;
      let unit: string | undefined;

      if (qtyMatch) {
        quantity = parseInt(qtyMatch[1] || qtyMatch[2] || qtyMatch[3]) || 1;
        unit = qtyMatch[4]?.toLowerCase();
      }

      // Remove quantity from name
      let name = cleanLine
        .replace(/\((\d+)\)/g, '')
        .replace(/x\d+/gi, '')
        .replace(/\d+\s*(pack|box|bottle|gallon|lb|oz|count)s?/gi, '')
        .trim();

      // Check for Costco product mappings
      const mappingKey = Object.keys(COSTCO_PRODUCT_MAPPINGS)
        .find(key => name.toLowerCase().includes(key));

      if (mappingKey) {
        const mapping = COSTCO_PRODUCT_MAPPINGS[mappingKey];
        items.push({
          name: mapping.name,
          quantity,
          unit: mapping.unit || unit,
          brand: mapping.brand
        });
      } else {
        items.push({ name, quantity, unit });
      }
    }

    return items;
  }

  /**
   * Convert shopping items to Instacart line items format
   */
  private toLineItems(items: ShoppingItem[]): LineItem[] {
    return items.map(item => {
      const lineItem: LineItem = {
        name: item.name,
        quantity: item.quantity || 1
      };

      if (item.unit) {
        lineItem.unit = item.unit;
      }

      if (item.brand) {
        lineItem.brand_filters = [item.brand];
      }

      // Create display text for user clarity
      const parts = [];
      if (item.quantity && item.quantity > 1) parts.push(`${item.quantity}`);
      if (item.unit) parts.push(item.unit);
      parts.push(item.name);
      if (item.brand) parts.push(`(${item.brand})`);
      lineItem.display_text = parts.join(' ');

      return lineItem;
    });
  }

  /**
   * Create a shopping list on Instacart and return the shareable URL
   */
  async createShoppingList(
    title: string,
    items: ShoppingItem[],
    options: {
      imageUrl?: string;
      linkbackUrl?: string;
      enablePantry?: boolean;
    } = {}
  ): Promise<InstacartResponse> {
    const request: ShoppingListRequest = {
      title,
      line_items: this.toLineItems(items),
      link_type: 'shopping_list'
    };

    if (options.imageUrl) {
      request.image_url = options.imageUrl;
    }

    if (options.linkbackUrl || options.enablePantry !== undefined) {
      request.landing_page_configuration = {};
      if (options.linkbackUrl) {
        request.landing_page_configuration.partner_linkback_url = options.linkbackUrl;
      }
      if (options.enablePantry !== undefined) {
        request.landing_page_configuration.enable_pantry_items = options.enablePantry;
      }
    }

    const response = await fetch(`${this.baseUrl}/idp/v1/products/products_link`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Instacart API error (${response.status}): ${errorText}`);
    }

    return response.json();
  }

  /**
   * Create shopping list from raw text input
   */
  async createFromText(
    title: string,
    rawList: string,
    options: {
      imageUrl?: string;
      linkbackUrl?: string;
      enablePantry?: boolean;
    } = {}
  ): Promise<{ url: string; items: ShoppingItem[]; expiresAt?: string }> {
    const items = this.parseShoppingList(rawList);
    const result = await this.createShoppingList(title, items, options);
    
    return {
      url: result.products_link_url,
      items,
      expiresAt: result.expires_at
    };
  }
}

// Export for Cloudflare Workers
export default InstacartClient;
