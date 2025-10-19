# Cloudflare Workers Setup Guide

## Prerequisites
1. Cloudflare account (free tier is sufficient)
2. Node.js installed on your machine
3. Your Telegram bot token: `8287038518:AAEbJHuRW3uAIDOvSccWtX8CYHaL77QiAIM`
4. Your Telegram chat ID

## Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

## Step 2: Login to Cloudflare

```bash
wrangler login
```

This will open a browser window to authenticate with Cloudflare.

## Step 3: Create KV Namespace

```bash
wrangler kv:namespace create "BTC_ALERT_KV"
```

Copy the namespace ID from the output and update `wrangler.toml`:
```toml
[[kv_namespaces]]
binding = "BTC_ALERT_KV"
id = "your-actual-namespace-id-here"
```

## Step 4: Set Environment Variables

Set your Telegram credentials as secrets:

```bash
wrangler secret put TELEGRAM_BOT_TOKEN
# Enter: 8287038518:AAEbJHuRW3uAIDOvSccWtX8CYHaL77QiAIM

wrangler secret put TELEGRAM_CHAT_ID
# Enter your chat ID (get it from @userinfobot on Telegram)
```

## Step 5: Deploy the Worker

```bash
wrangler deploy
```

## Step 6: Test the Deployment

After deployment, you can test your worker:

1. **Check status**: Visit `https://btc-price-alert-bot.your-subdomain.workers.dev/status`
2. **Manual check**: Visit `https://btc-price-alert-bot.your-subdomain.workers.dev/check`

## Step 7: Monitor Logs

```bash
wrangler tail
```

## Configuration Options

### Environment Variables (in wrangler.toml)
- `PRICE_DELTA_USD`: Alert threshold (default: 500)
- `DRY_RUN`: Set to "1" for testing without sending messages

### Cron Schedule
The worker runs every 30 seconds by default. To change this, modify the cron expression in `wrangler.toml`:

```toml
[triggers]
crons = ["*/30 * * * *"]  # Every 30 seconds
# crons = ["*/60 * * * *"]  # Every minute
# crons = ["0 */5 * * *"]   # Every 5 minutes
```

## Free Tier Limits
- 100,000 requests per day
- 10ms CPU time per request
- 1,000 KV operations per day
- More than enough for this bot!

## Troubleshooting

### Check Worker Logs
```bash
wrangler tail
```

### Test Locally
```bash
wrangler dev --local
```

### Update Secrets
```bash
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put TELEGRAM_CHAT_ID
```

### View KV Data
```bash
wrangler kv:key list --namespace-id=your-namespace-id
wrangler kv:key get "bot_state" --namespace-id=your-namespace-id
```

## Features

✅ **Real-time monitoring**: Checks Bitcoin price every 30 seconds  
✅ **Persistent state**: Uses Cloudflare KV to remember last alert price  
✅ **Text-based charts**: Sends ASCII charts in Telegram messages  
✅ **Error handling**: Robust error handling and logging  
✅ **Free hosting**: Runs on Cloudflare's free tier  
✅ **Instant deployment**: Deploy with a single command  

## API Endpoints

- `GET /status` - Check bot status and recent alerts
- `GET /check` - Manually trigger a price check
- Scheduled execution every 30 seconds via cron triggers

Your Bitcoin price alert bot will now run 24/7 on Cloudflare's global network! 🚀