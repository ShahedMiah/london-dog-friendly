# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data research project focused on dog-friendly businesses and organisations in London. The repository contains structured data about various establishments including pubs, grooming services, charities, and other dog-friendly venues.

## Development Environment

### Python Setup
- Virtual environment located in `venv/` directory
- Activate with: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt` (if requirements.txt exists)

### Key Python Scripts
- `extract_current_data.py` - Manual data entry script for BringFido restaurant data
- `scrape_bringfido.py` - Automated web scraper for BringFido.com using Playwright
- `scrape_bringfido_complete.py` - Complete scraping implementation with enhanced error handling

### Running Scripts
```bash
# Activate virtual environment
source venv/bin/activate

# Run data extraction
python3 extract_current_data.py

# Run web scraping (requires Playwright installation)
python3 scrape_bringfido.py
```

### Playwright Setup
```bash
# Install Playwright browsers (if needed)
playwright install
```

## Data Architecture

### CSV Data Structure
The project uses WordPress/GeoDirectory export format with these critical fields:
- **Core Business**: `post_title`, `post_content`, `post_type`, `post_category`
- **Location**: `street`, `city`, `region`, `country`, `latitude`, `longitude`, `zip`
- **Contact**: `phone`, `email`, `website`
- **Business Details**: `business_hours` (JSON format), `payment_types`, `ratings`
- **Social Media**: `facebook`, `instagram`, `tiktok`
- **Services**: `service_1_description` through `service_5_description`, `cf1`-`cf5`
- **Media**: `post_images` (pipe-separated URLs with metadata)

### Data Categories
- Category 139: Restaurants/Food establishments
- Category 193: Charities/Support organisations
- Category 195: Animal rescue/care services

### Key Data Files
- `gd_place_*.csv` - Original dataset (~40 entries)
- `bringfido_*.csv` - Scraped restaurant data from BringFido
- `combined_dog_friendly_data_*.csv` - Merged datasets with timestamps

## Data Processing Workflow

### 1. Web Scraping
```bash
python3 scrape_bringfido.py
```
- Extracts restaurant data from BringFido.com
- Handles pagination and individual venue pages
- Formats data to match existing CSV structure
- Includes rate limiting and error handling

### 2. Data Extraction
```bash
python3 extract_current_data.py
```
- Manual data entry for specific venues
- Generates timestamped output files
- Creates combined datasets automatically

### 3. Data Validation
- Check latitude/longitude coordinates are valid
- Verify business hours JSON format
- Validate category assignments
- Ensure required fields are populated

## File Access Permissions

The project has restricted file system permissions configured in `.claude/settings.local.json`:
- **Allowed**: Directory listing, text file reading, file writing
- **Playwright**: Browser automation and navigation permitted
- **Python**: Script execution allowed

## Data Sources and Expansion

### Primary Source: BringFido.com
- **Target**: 800+ London venues across categories
- **Method**: Automated Playwright scraping
- **Rate Limiting**: Respectful delays between requests
- **Output**: Structured CSV matching project format

### Secondary Sources
See `HOW_TO_EXPAND_DATASET.md` for comprehensive expansion strategies including:
- Google Places API integration
- Social media mining techniques
- Local council database integration
- Manual research methodologies

## Data Quality Standards

### Location Data
- Latitude/longitude coordinates must be decimal format
- Address components properly parsed into separate fields
- London-specific region/country standardisation

### Business Information
- Complete contact details where available
- Structured business hours in JSON format
- Verified website URLs and social media links
- Accurate category assignment based on business type

### Content Standards
- Dog-friendly specific descriptions
- Clear service offerings in dedicated fields
- Professional business descriptions
- Image URLs with proper metadata formatting