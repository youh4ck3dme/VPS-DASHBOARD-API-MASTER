# CarScraper Pro - Blueprint (Google Colab MVP)

Overview
- CarScraper Pro is a Colab-based prototype to fetch car listings (e.g., from Bazoš.sk), parse key attributes, and use Gemini AI to assess deal viability.
- MVP focus: end-to-end data flow from scraping to AI analysis to a consumable output.

Architecture
- Scraper module (requests + BeautifulSoup)
- Parser module (dedicated parsers for title, price, description, link, location, date)
- AI analysis module (Gemini API)
- Data layer (Pandas DataFrame, optional CSV export)
- Output module (print/Telegram notification)
- Security module (API key placeholders; secrets managed via Colab secrets)

Data Model (CarListing)
- title: string
- price: int (EUR)
- description: string
- link: string (URL)
- location: string
- date_posted: string/date
- ai_verdict: string (optional)
- ai_estimated_value: string (optional)
- ai_reason: string (optional)

Workflow (Colab MVP)
- Step 1: Load inputs (category, min_price, max_price)
- Step 2: Scrape listings from target site
- Step 3: Parse each listing into CarListing objects
- Step 4: For each listing, call Gemini API to analyze deal viability
- Step 5: Compute simple profitability metric (estimated_value - price)
- Step 6: Output results (DataFrame display; optional export to CSV)
- Step 7: Optional: Push alerts to Telegram or email

API Keys and Secrets
- Use Colab secrets for real API keys
- Placeholder: GOEOGLE_API_KEY (rename to match real secret key)
- Gemini integration uses OpenAI-like prompt-based API

Non-functional considerations
- Rate limits and polite scraping (delay between requests)
- Basic error handling and retries
- Minimal logging (to stdout and a log cell)
- Output for reproducibility

Deliverables
- CarScraper_Pro_blueprint.md (this document)
- CarScraper_Pro_PROMPT.md (Mega-Prompt for Gemini)
- Optional: CarScraper_Pro_COLAB_TEMPLATE.md (Colab notebook skeleton)

