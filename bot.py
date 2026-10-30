import os
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "@KuliMemeBot")

def get_token_age(created_timestamp):
    if not created_timestamp:
        return "Baru lahir 🐣"
    now = time.time() * 1000
    diff_hours = (now - created_timestamp) / (1000 * 60 * 60)
    if diff_hours < 1:
        return f"{int(diff_hours * 60)} menit lalu ⚡"
    return f"{diff_hours:.1f} jam lalu ⏰"

async def call_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🚨 Masukin Contract Address (CA)-nya dulu, bro! Contoh: /call <CA>")
        return
    
    ca = context.args[0]
    loading_msg = await update.message.reply_text("🔍 Lagi ngintip dompet whale sama ngecek koin micinnya... Sabar ya ☕")

    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
        response = requests.get(url).json()
        
        pairs = response.get("pairs", [])
        if not pairs:
            await loading_msg.edit_text("❌ Waduh, koinnya ga ketemu atau belum ada likuiditas. Cek lagi CA-nya!")
            return
        
        pair = pairs[0]
        name = pair.get("baseToken", {}).get("name", "Unknown Gem")
        symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
        dex = pair.get("dexId", "unknown")
        
        mc = pair.get("marketCap", pair.get("fdv", 0))
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        volume_1h = pair.get("volume", {}).get("h1", 0)
        txns_1h = pair.get("txns", {}).get("h1", {"buys": 0, "sells": 0})
        
        created_at = pair.get("pairCreatedAt")
        age = get_token_age(created_at)

        # Cek apakah dari pump.fun atau udah graduate
        is_pump = "pump" in dex.lower() or "raydium" in dex.lower()
        status_label = "🚀 GEMINI PUMP-RADAR (Degen Mode)" if is_pump else "💎 RADAR-CLIMBER"

        # Format teks dengan desain lucu / estetika ala grup call
        text = f"""{status_label}
------------------------------------
🪙 **{name}** (`${symbol}`)
🔥 **Vibe:** Potensi terbang / nyangkut di pucuk wkwk
------------------------------------
⏱ **Umur:** {age}
💰 **Market Cap:** `${mc:,.0f}`
💧 **Likuiditas:** `${liquidity:,.0f}`
📊 **Vol 1 Jam:** `${volume_1h:,.0f}` ({txns_1h.get('buys', 0)} hijau 🟢 / {txns_1h.get('sells', 0)} merah 🔴)

🔗 **Ngedumel / Beli di sini:** 
https://trade.padre.gg/trade/solana/{ca}

📄 **Contract Address (CA):**
`{ca}`

⚠️ **Pesan Sponsor Emak-emak:**
Jangan pakai uang beras! Kalau boncos, jangan nangis di pojokan ya cuy. 

*Bukan saran finansial. DYOR & LFG!* 🎰"""

        await loading_msg.edit_text(text, parse_mode="Markdown")

    except Exception as e:
        await loading_msg.edit_text(f"❌ Yah error cuy: {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("call", call_token))
    print("Bot siap tempur...")
    app.run_polling()

if __name__ == "__main__":
    main()
