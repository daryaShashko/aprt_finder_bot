# AI Apartment Hunter Bot 🏠

An advanced Telegram bot that monitors rental listings on OLX.pl for real estate in the Tricity area (Gdańsk, Gdynia, Sopot), uses **Google Gemini AI** to analyze the details, and sends structured notifications.

## Features ✨

- **Automated Monitoring**: Checks for new ads every 15 minutes (configurable).
- **Smart Filtering**: Uses `BeautifulSoup` to scrape ad content.
- **AI Analysis**: **Google Gemini 1.5 Flash** extracts:
  - Total Monthly Cost (Rent + Admin + Utilities)
  - Security Deposit
  - Pet Policy (Allowed/Not Allowed)
  - Brief Summary in Russian
- **Duplicate Prevention**: SQLite database tracks seen ads to prevent repeat notifications.
- **Direct Links**: Provides quick access to the original OLX listing.

## Prerequisites 🛠️

- **Python 3.8+**
- **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
- **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))

## Setup ⚙️

1. **Clone the repository** (if applicable) or navigate to the project folder.

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
    ```bash
    deactivate # To deactivate the virtual environment
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration:**
    - Copy `.env.example` to `.env`:
      ```bash
      cp .env.example .env
      ```
    - Edit `.env` and fill in your details:
      ```ini
      TELEGRAM_BOT_TOKEN=your_telegram_bot_token
      GOOGLE_API_KEY=your_gemini_api_key
      OLX_URL=https://www.olx.pl/d/nieruchomosci/mieszkania/wynajem/gdansk/...
      CHECK_INTERVAL=15
      USER_ID=your_telegram_user_id
      ```
      *(Run the bot and send `/start` to get your `USER_ID`)*

## Running the Bot 🚀

Ensure your virtual environment is activated, then run:

```bash
python bot.py
```

## Commands 💬

- `/start` - Initialize the bot and get your User ID.
- `/check` - Manually trigger a check for new ads immediately (useful for testing).

## Project Structure 📂

- `bot.py`: Main entry point, handles Telegram commands and scheduling.
- `scraper.py`: Handles fetching and parsing data from OLX.
- `ai_agent.py`: Interfaces with Google Gemini for text analysis.
- `database.py`: Manages SQLite database for tracking seen ads.
