/**
 * Bitcoin Price Alert Cloudflare Worker
 * Monitors BTC price and sends Telegram alerts on ±$500 changes
 */

// Configuration - Set these in Worker environment variables
const CONFIG = {
  TELEGRAM_BOT_TOKEN: '', // Set in environment
  TELEGRAM_CHAT_ID: '', // Set in environment
  PRICE_DELTA_USD: 500,
  POLL_INTERVAL_MS: 30000, // 30 seconds
  BINANCE_API_BASE: 'https://api.binance.com/api/v3',
  SYMBOL: 'BTCUSDT'
};

// State management using KV storage
class StateManager {
  constructor(kv) {
    this.kv = kv;
  }

  async getState() {
    try {
      const state = await this.kv.get('bot_state', 'json');
      return state || {
        last_alert_price: null,
        alert_history: []
      };
    } catch (error) {
      console.error('Error getting state:', error);
      return {
        last_alert_price: null,
        alert_history: []
      };
    }
  }

  async saveState(state) {
    try {
      await this.kv.put('bot_state', JSON.stringify(state));
    } catch (error) {
      console.error('Error saving state:', error);
    }
  }
}

// Binance API client
class BinanceClient {
  constructor() {
    this.baseUrl = CONFIG.BINANCE_API_BASE;
  }

  async getCurrentPrice() {
    try {
      // Try multiple APIs for better reliability
      const apis = [
        'https://api.coinbase.com/v2/exchange-rates?currency=BTC',
        'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
        'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
      ];
      
      for (const apiUrl of apis) {
        try {
          const response = await fetch(apiUrl, {
            headers: {
              'User-Agent': 'BTC-Alert-Bot/1.0'
            }
          });
          
          if (!response.ok) {
            console.log(`API ${apiUrl} returned ${response.status}, trying next...`);
            continue;
          }
          
          const data = await response.json();
          
          // Parse different API response formats
          if (apiUrl.includes('coinbase')) {
            return parseFloat(data.data.rates.USD);
          } else if (apiUrl.includes('coingecko')) {
            return parseFloat(data.bitcoin.usd);
          } else if (apiUrl.includes('binance')) {
            return parseFloat(data.price);
          }
        } catch (error) {
          console.log(`Error with API ${apiUrl}:`, error.message);
          continue;
        }
      }
      
      throw new Error('All price APIs failed');
    } catch (error) {
      console.error('Error fetching price:', error);
      throw error;
    }
  }

  async getKlines(interval = '1h', limit = 24) {
    try {
      const response = await fetch(
        `${this.baseUrl}/klines?symbol=${CONFIG.SYMBOL}&interval=${interval}&limit=${limit}`
      );
      if (!response.ok) {
        throw new Error(`Binance API error: ${response.status}`);
      }
      const data = await response.json();
      return data.map(kline => ({
        timestamp: kline[0],
        close: parseFloat(kline[4])
      }));
    } catch (error) {
      console.error('Error fetching klines:', error);
      throw error;
    }
  }
}

// Telegram notification service
class TelegramNotifier {
  constructor(botToken, chatId) {
    this.botToken = botToken;
    this.chatId = chatId;
    this.baseUrl = `https://api.telegram.org/bot${botToken}`;
  }

  async sendMessage(text) {
    try {
      const response = await fetch(`${this.baseUrl}/sendMessage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chat_id: this.chatId,
          text: text,
          parse_mode: 'HTML'
        })
      });

      if (!response.ok) {
        throw new Error(`Telegram API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending Telegram message:', error);
      throw error;
    }
  }

  async sendChart(chartData, caption) {
    // For Cloudflare Workers, we'll send a text-based chart
    // since generating images requires more complex setup
    const textChart = this.generateTextChart(chartData);
    const message = `${caption}\n\n<pre>${textChart}</pre>`;
    return await this.sendMessage(message);
  }

  generateTextChart(chartData) {
    if (!chartData || chartData.length === 0) return 'No chart data available';
    
    const prices = chartData.map(d => d.close);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min;
    
    let chart = 'BTC Price Chart (24h):\n';
    chart += '━'.repeat(30) + '\n';
    
    // Simple ASCII chart
    for (let i = 0; i < Math.min(chartData.length, 12); i++) {
      const price = prices[i];
      const normalized = range > 0 ? (price - min) / range : 0.5;
      const barLength = Math.round(normalized * 20);
      const bar = '█'.repeat(barLength) + '░'.repeat(20 - barLength);
      const timestamp = new Date(chartData[i].timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
      chart += `${timestamp} ${bar} $${price.toFixed(0)}\n`;
    }
    
    return chart;
  }
}

// Main bot logic
class BitcoinAlertBot {
  constructor(env) {
    this.env = env;
    this.stateManager = new StateManager(env.BTC_ALERT_KV);
    this.binanceClient = new BinanceClient();
    this.telegramNotifier = new TelegramNotifier(
      env.TELEGRAM_BOT_TOKEN,
      env.TELEGRAM_CHAT_ID
    );
    
    // Update config from environment
    CONFIG.TELEGRAM_BOT_TOKEN = env.TELEGRAM_BOT_TOKEN;
    CONFIG.TELEGRAM_CHAT_ID = env.TELEGRAM_CHAT_ID;
    CONFIG.PRICE_DELTA_USD = parseFloat(env.PRICE_DELTA_USD) || 500;
  }

  formatUSD(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  buildTelegramCaption(currentPrice, baselinePrice, priceChange, direction) {
    const changePercent = ((Math.abs(priceChange) / baselinePrice) * 100).toFixed(2);
    const emoji = direction === 'up' ? '🚀📈' : '📉💥';
    const directionText = direction === 'up' ? 'INCREASED' : 'DECREASED';
    
    return `
${emoji} <b>BTC PRICE ALERT</b> ${emoji}

💰 <b>Current Price:</b> ${this.formatUSD(currentPrice)}
📊 <b>Previous Alert:</b> ${this.formatUSD(baselinePrice)}
${direction === 'up' ? '⬆️' : '⬇️'} <b>Change:</b> ${this.formatUSD(Math.abs(priceChange))} (${changePercent}%)

🔔 Bitcoin has <b>${directionText}</b> by more than ${this.formatUSD(CONFIG.PRICE_DELTA_USD)} since the last alert!

⏰ <b>Time:</b> ${new Date().toLocaleString('en-US', { timeZone: 'UTC' })} UTC
📈 <b>Symbol:</b> ${CONFIG.SYMBOL}
    `.trim();
  }

  async checkPriceAndAlert() {
    try {
      console.log('Checking Bitcoin price...');
      
      // Get current state
      const state = await this.stateManager.getState();
      
      // Get current price
      const currentPrice = await this.binanceClient.getCurrentPrice();
      console.log(`Current BTC price: ${this.formatUSD(currentPrice)}`);
      
      // Initialize baseline if not set
      if (!state.last_alert_price) {
        state.last_alert_price = currentPrice;
        await this.stateManager.saveState(state);
        console.log(`Baseline price set to: ${this.formatUSD(currentPrice)}`);
        return { success: true, message: 'Baseline initialized', price: currentPrice };
      }
      
      // Check for significant price change
      const priceChange = currentPrice - state.last_alert_price;
      const absChange = Math.abs(priceChange);
      
      console.log(`Price change: ${this.formatUSD(priceChange)} (threshold: ${this.formatUSD(CONFIG.PRICE_DELTA_USD)})`);
      
      if (absChange >= CONFIG.PRICE_DELTA_USD) {
        const direction = priceChange > 0 ? 'up' : 'down';
        console.log(`Alert triggered! Price moved ${direction} by ${this.formatUSD(absChange)}`);
        
        // Get chart data
        const chartData = await this.binanceClient.getKlines('1h', 24);
        
        // Build caption
        const caption = this.buildTelegramCaption(
          currentPrice,
          state.last_alert_price,
          priceChange,
          direction
        );
        
        // Send notification
        if (this.env.DRY_RUN === '1') {
          console.log('DRY RUN - Would send alert:');
          console.log(caption);
        } else {
          await this.telegramNotifier.sendChart(chartData, caption);
          console.log('Alert sent successfully!');
        }
        
        // Update state
        state.last_alert_price = currentPrice;
        state.alert_history.push({
          timestamp: Date.now(),
          price: currentPrice,
          change: priceChange,
          direction: direction
        });
        
        // Keep only last 10 alerts
        if (state.alert_history.length > 10) {
          state.alert_history = state.alert_history.slice(-10);
        }
        
        await this.stateManager.saveState(state);
        
        return {
          success: true,
          message: 'Alert sent',
          price: currentPrice,
          change: priceChange,
          direction: direction
        };
      }
      
      return {
        success: true,
        message: 'No alert needed',
        price: currentPrice,
        change: priceChange
      };
      
    } catch (error) {
      console.error('Error in checkPriceAndAlert:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// Cloudflare Worker event handlers
export default {
  async fetch(request, env, ctx) {
    // Handle HTTP requests (for manual triggers or status checks)
    const url = new URL(request.url);
    
    if (url.pathname === '/status') {
      const stateManager = new StateManager(env.BTC_ALERT_KV);
      const state = await stateManager.getState();
      
      return new Response(JSON.stringify({
        status: 'running',
        last_alert_price: state.last_alert_price,
        alert_history: state.alert_history.slice(-5) // Last 5 alerts
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (url.pathname === '/check') {
      const bot = new BitcoinAlertBot(env);
      const result = await bot.checkPriceAndAlert();
      
      return new Response(JSON.stringify(result), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Bitcoin Price Alert Bot - Use /status or /check endpoints', {
      status: 200
    });
  },

  async scheduled(controller, env, ctx) {
    // Handle scheduled events (cron triggers)
    console.log('Scheduled check triggered');
    
    const bot = new BitcoinAlertBot(env);
    const result = await bot.checkPriceAndAlert();
    
    console.log('Scheduled check result:', result);
  }
};