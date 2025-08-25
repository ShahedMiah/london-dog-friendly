#!/usr/bin/env python3
"""
Production BringFido.com London Dog-Friendly Venue Scraper
Scrapes all 800+ venues: restaurants, hotels, attractions, services
"""

import csv
import time
import json
import re
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright
import random
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BringFidoProductionScraper:
    def __init__(self):
        self.base_url = "https://www.bringfido.ca"
        self.all_venues = []
        self.failed_urls = []
        
        # Category mappings - updated based on test results
        self.categories = {
            'restaurants': {
                'url': '/restaurant/city/london_gb/',
                'category_id': '139',
                'expected_count': 121  # Updated from test results
            },
            'hotels': {
                'url': '/lodging/city/london_gb/',
                'category_id': '193',
                'expected_count': 658
            },
            'attractions': {
                'url': '/attraction/city/london_gb/',
                'category_id': '229',
                'expected_count': 44
            },
            'services': {
                'url': '/resource/city/london_gb/',
                'category_id': '77',
                'expected_count': 8
            }
        }

    def wait_random(self, min_seconds=2, max_seconds=5):
        """Random delay to be respectful to the server"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def extract_venue_links_from_listing(self, page, category_name):
        """Extract all venue links from a category listing page"""
        venue_links = []
        current_page = 1
        
        logger.info(f"Extracting {category_name} venue links...")
        
        while True:
            try:
                # Wait for page to load
                page.wait_for_load_state('networkidle', timeout=30000)
                self.wait_random(2, 4)
                
                # Updated selector based on successful test
                links_found = []
                
                # Use the pattern that worked in our test
                if category_name == 'restaurants':
                    heading_links = page.query_selector_all('h2 a[href*="/restaurant/"]')
                elif category_name == 'hotels':
                    heading_links = page.query_selector_all('h2 a[href*="/lodging/"]')
                elif category_name == 'attractions':
                    heading_links = page.query_selector_all('h2 a[href*="/attraction/"]')
                elif category_name == 'services':
                    heading_links = page.query_selector_all('h2 a[href*="/resource/"]')
                else:
                    heading_links = []
                
                logger.info(f"Found {len(heading_links)} heading links")
                
                for element in heading_links:
                    try:
                        href = element.get_attribute('href')
                        title = element.inner_text().strip()
                        
                        if href and title:
                            full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                            
                            # Avoid duplicate links
                            if full_url not in [link['url'] for link in links_found]:
                                links_found.append({
                                    'url': full_url,
                                    'title': title,
                                    'category': category_name
                                })
                    except Exception as e:
                        logger.debug(f"Error processing link: {e}")
                        continue
                
                venue_links.extend(links_found)
                logger.info(f"Page {current_page}: Found {len(links_found)} {category_name} links")
                
                # Look for "See More Results" link
                try:
                    next_link = page.query_selector('a:has-text("See More Results")')
                    
                    if next_link and len(links_found) > 0:
                        next_url = next_link.get_attribute('href')
                        if next_url:
                            next_url = next_url if next_url.startswith('http') else f"{self.base_url}{next_url}"
                            logger.info(f"Navigating to next page: {next_url}")
                            page.goto(next_url)
                            current_page += 1
                            continue
                    
                except Exception as e:
                    logger.info(f"No more pages found for {category_name}: {e}")
                
                break
                
            except Exception as e:
                logger.error(f"Error extracting {category_name} links from page {current_page}: {e}")
                break
        
        logger.info(f"Total {category_name} links found: {len(venue_links)}")
        return venue_links

    def extract_venue_details(self, page, venue_url, category):
        """Extract detailed information from a venue page"""
        try:
            logger.info(f"Extracting details from: {venue_url}")
            page.goto(venue_url, timeout=30000)
            page.wait_for_load_state('networkidle', timeout=20000)
            self.wait_random(1, 3)
            
            # Extract venue data using JavaScript - same as successful test
            venue_data = page.evaluate("""
                () => {
                    const data = {
                        name: '',
                        address: '',
                        phone: '',
                        email: '',
                        website: '',
                        description: '',
                        latitude: '',
                        longitude: '',
                        rating: '',
                        review_count: ''
                    };
                    
                    // Get name from h1
                    const nameEl = document.querySelector('h1');
                    if (nameEl) data.name = nameEl.textContent.trim();
                    
                    // Get address - look for location button or address info
                    const addressElements = document.querySelectorAll('button, div, span, p');
                    for (let el of addressElements) {
                        const text = el.textContent || '';
                        if (text.includes('London') && (text.includes('UK') || text.includes('United Kingdom'))) {
                            data.address = text.trim();
                            break;
                        }
                    }
                    
                    // Get phone
                    const phoneEl = document.querySelector('a[href^="tel:"]');
                    if (phoneEl) {
                        data.phone = phoneEl.textContent.trim();
                    }
                    
                    // Get email
                    const emailEl = document.querySelector('a[href^="mailto:"]');
                    if (emailEl) {
                        data.email = emailEl.href.replace('mailto:', '');
                    }
                    
                    // Get website - look for external links
                    const websiteLinks = document.querySelectorAll('a[href^="http"]');
                    for (let link of websiteLinks) {
                        const href = link.href;
                        if (!href.includes('bringfido') && 
                            !href.includes('facebook') && 
                            !href.includes('twitter') && 
                            !href.includes('instagram') &&
                            !href.includes('booking.com') &&
                            !href.includes('airbnb')) {
                            data.website = href;
                            break;
                        }
                    }
                    
                    // Get description from paragraphs
                    const paragraphs = document.querySelectorAll('p');
                    for (let p of paragraphs) {
                        const text = p.textContent.trim();
                        if (text.length > 50 && 
                            (text.toLowerCase().includes('dog') || 
                             text.toLowerCase().includes('pet') ||
                             text.toLowerCase().includes('restaurant') ||
                             text.toLowerCase().includes('bar') ||
                             text.toLowerCase().includes('food') ||
                             text.toLowerCase().includes('hotel') ||
                             text.toLowerCase().includes('attraction'))) {
                            data.description = text;
                            break;
                        }
                    }
                    
                    // Try to extract coordinates from scripts or data attributes
                    const scripts = document.querySelectorAll('script');
                    for (let script of scripts) {
                        const content = script.textContent || '';
                        
                        // Look for latitude/longitude in various formats
                        const latMatch = content.match(/["']?latitude["']?\\s*[:\\=]\\s*([0-9.-]+)/i);
                        const lngMatch = content.match(/["']?longitude["']?\\s*[:\\=]\\s*([0-9.-]+)/i);
                        
                        if (latMatch && lngMatch) {
                            data.latitude = latMatch[1];
                            data.longitude = lngMatch[1];
                            break;
                        }
                        
                        // Alternative patterns
                        const coordMatch = content.match(/([0-9.-]+),\\s*([0-9.-]+)/);
                        if (coordMatch && coordMatch[1].includes('.') && coordMatch[2].includes('.')) {
                            // Validate these look like London coordinates
                            const lat = parseFloat(coordMatch[1]);
                            const lng = parseFloat(coordMatch[2]);
                            if (lat > 51 && lat < 52 && lng > -1 && lng < 1) {
                                data.latitude = coordMatch[1];
                                data.longitude = coordMatch[2];
                                break;
                            }
                        }
                    }
                    
                    return data;
                }
            """)
            
            # Get venue ID from URL
            venue_id = venue_url.split('/')[-1] if '/' in venue_url else ''
            
            # Add additional metadata
            venue_data['venue_id'] = venue_id
            venue_data['url'] = venue_url
            venue_data['category'] = category
            
            # Clean and validate data
            if venue_data['description'] and len(venue_data['description']) > 1500:
                venue_data['description'] = venue_data['description'][:1500] + '...'
                
            return venue_data
            
        except Exception as e:
            logger.error(f"Error extracting details from {venue_url}: {e}")
            self.failed_urls.append(venue_url)
            return None

    def format_for_csv(self, venues_data):
        """Format scraped data to match existing CSV structure"""
        formatted_data = []
        
        for i, venue in enumerate(venues_data, start=8000):  # Start from 8000 to avoid conflicts
            
            # Parse address components
            address = venue.get('address', '')
            address_parts = [part.strip() for part in address.split(',') if part.strip()]
            
            street = address_parts[0] if address_parts else ''
            city = 'London'
            region = 'Greater London'
            country = 'United Kingdom'
            zip_code = ''
            
            # Extract UK postcode using regex
            postcode_pattern = r'[A-Z]{1,2}\\d{1,2}[A-Z]?\\s?\\d[A-Z]{2}'
            postcode_match = re.search(postcode_pattern, address)
            if postcode_match:
                zip_code = postcode_match.group().strip()
            
            # Determine category ID
            category_id = '139'  # Default to restaurant
            if venue.get('category') == 'hotels':
                category_id = '193'
            elif venue.get('category') == 'attractions':
                category_id = '229'
            elif venue.get('category') == 'services':
                category_id = '77'
            
            formatted_venue = {
                'ID': i,
                'post_title': venue.get('name', '')[:255],  # Limit length
                'post_content': venue.get('description', '')[:2000],  # Limit length
                'post_status': 'publish',
                'post_author': 1,
                'post_type': 'gd_place',
                'post_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'post_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'post_tags': '',
                'post_category': category_id,
                'default_category': '',
                'featured': 0,
                'street': street[:255] if street else '',
                'street2': '',
                'city': city,
                'region': region,
                'country': country,
                'zip': zip_code,
                'latitude': venue.get('latitude', ''),
                'longitude': venue.get('longitude', ''),
                'phone': venue.get('phone', ''),
                'payment_types': '',
                'neighbourhood': '',
                'ratings': venue.get('rating', ''),
                'package_id': 1,
                'expire_date': '0000-00-00',
                'business_hours': '',
                'email': venue.get('email', ''),
                'terms_conditions': 1,
                'does_your_business_have_any_of_the_following': '',
                'website': venue.get('website', ''),
                'how_to_support': '',
                'cause_description': '',
                'verified': 0,
                'claimed': 0,
                'facebook': '',
                'instagram': '',
                'official_review_url': venue.get('url', ''),
                'tiktok': '',
                'cf1': '',
                'service_2_description': '',
                'cf4': '',
                'cf5': '',
                'cf2': '',
                'service_1_description': venue.get('description', '')[:100] + '...' if len(venue.get('description', '')) > 100 else venue.get('description', ''),
                'service_4_description': '',
                'service_5_description': '',
                'special_offers': '',
                'to_verify_your_ownership_please_upload_any_of_the_': '',
                'would_you_like_to_display_services__products': 0,
                'would_you_like_to_add_cah': 0,
                'post_images': ''
            }
            
            formatted_data.append(formatted_venue)
        
        return formatted_data

    def scrape_category(self, page, category_name, category_info):
        """Scrape all venues from a specific category"""
        logger.info(f"Starting {category_name} scraping...")
        
        try:
            # Navigate to category page
            category_url = f"{self.base_url}{category_info['url']}"
            logger.info(f"Navigating to: {category_url}")
            page.goto(category_url, timeout=30000)
            
            # Extract all venue links from listing pages
            venue_links = self.extract_venue_links_from_listing(page, category_name)
            
            if not venue_links:
                logger.warning(f"No venue links found for {category_name}")
                return []
            
            logger.info(f"Found {len(venue_links)} {category_name} to process")
            
            # Extract details from each venue (ALL venues, not limited)
            venues_data = []
            total_venues = len(venue_links)
            
            for i, venue_link in enumerate(venue_links, 1):
                logger.info(f"Processing {category_name} {i}/{total_venues}: {venue_link['title']}")
                
                venue_data = self.extract_venue_details(page, venue_link['url'], category_name)
                if venue_data:
                    # Add title from listing if name wasn't found on detail page
                    if not venue_data.get('name'):
                        venue_data['name'] = venue_link['title']
                    venues_data.append(venue_data)
                
                # Be respectful with delays
                self.wait_random(3, 6)
                
                # Save progress every 25 venues to avoid losing data
                if i % 25 == 0:
                    self.save_progress(venues_data, f"{category_name}_progress_{i}")
                    logger.info(f"Progress checkpoint: {i}/{total_venues} {category_name} completed")
            
            logger.info(f"Completed {category_name}: {len(venues_data)} venues extracted")
            return venues_data
            
        except Exception as e:
            logger.error(f"Error scraping {category_name}: {e}")
            return []

    def save_progress(self, venues_data, filename_suffix=""):
        """Save current progress to avoid losing data"""
        if not venues_data:
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/Users/shahed.miah/Projects/Dog Friendly Research/bringfido_progress_{filename_suffix}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(venues_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Progress saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def run_production_scrape(self):
        """Run the complete production scraping process for all categories"""
        logger.info("🚀 Starting PRODUCTION BringFido scrape for all 800+ venues...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,  # Run headless for production efficiency
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            page = browser.new_page()
            
            # Set longer timeouts for production
            page.set_default_timeout(45000)
            
            try:
                all_venues = []
                
                # Process each category
                for category_name, category_info in self.categories.items():
                    logger.info(f"\\n{'='*60}")
                    logger.info(f"🎯 PROCESSING CATEGORY: {category_name.upper()}")
                    logger.info(f"📊 Expected venues: {category_info['expected_count']}")
                    logger.info(f"{'='*60}")
                    
                    start_time = datetime.now()
                    venues = self.scrape_category(page, category_name, category_info)
                    end_time = datetime.now()
                    
                    logger.info(f"⏱️  {category_name} completed in: {end_time - start_time}")
                    logger.info(f"✅ {len(venues)} {category_name} venues collected")
                    
                    all_venues.extend(venues)
                    
                    # Save progress after each category
                    self.save_progress(all_venues, f"after_{category_name}")
                    
                    logger.info(f"📈 Total venues collected so far: {len(all_venues)}")
                    
                    # Longer break between categories to be respectful
                    logger.info("😴 Taking break between categories...")
                    self.wait_random(10, 20)
                
                # Format and save final complete dataset
                if all_venues:
                    logger.info(f"\\n🔄 Formatting {len(all_venues)} venues for final CSV...")
                    formatted_data = self.format_for_csv(all_venues)
                    
                    # Save the complete production dataset
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_file = f"/Users/shahed.miah/Projects/Dog Friendly Research/bringfido_PRODUCTION_COMPLETE_{timestamp}.csv"
                    
                    # Get fieldnames from existing CSV
                    existing_csv = '/Users/shahed.miah/Projects/Dog Friendly Research/gd_place_2508250852_561054b5 - gd_place_2508250852_561054b5.csv.csv'
                    
                    try:
                        with open(existing_csv, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            fieldnames = reader.fieldnames
                    except:
                        fieldnames = list(formatted_data[0].keys()) if formatted_data else []
                    
                    # Write complete production dataset
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(formatted_data)
                    
                    logger.info(f"🎉 PRODUCTION dataset saved: {output_file}")
                    logger.info(f"📊 Total venues scraped: {len(formatted_data)}")
                    
                    # Create mega combined file with existing data
                    try:
                        combined_file = f"/Users/shahed.miah/Projects/Dog Friendly Research/MEGA_COMBINED_DATASET_{timestamp}.csv"
                        
                        existing_data = []
                        with open(existing_csv, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            existing_data = list(reader)
                        
                        mega_data = existing_data + formatted_data
                        
                        with open(combined_file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(mega_data)
                        
                        logger.info(f"🚀 MEGA combined dataset created: {combined_file}")
                        logger.info(f"📈 Total entries in mega dataset: {len(mega_data)}")
                        logger.info(f"🎯 Original entries: {len(existing_data)}")
                        logger.info(f"🆕 New BringFido entries: {len(formatted_data)}")
                        
                    except Exception as e:
                        logger.error(f"Could not create combined file: {e}")
                
                else:
                    logger.warning("❌ No venues were scraped!")
                
                # Final report
                logger.info(f"\\n{'='*60}")
                logger.info("📋 FINAL PRODUCTION SCRAPE REPORT")
                logger.info(f"{'='*60}")
                
                category_counts = {}
                for venue in all_venues:
                    cat = venue.get('category', 'unknown')
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                
                for category, count in category_counts.items():
                    expected = self.categories.get(category, {}).get('expected_count', 0)
                    logger.info(f"📊 {category.capitalize()}: {count} venues (expected: {expected})")
                
                logger.info(f"🎉 TOTAL SCRAPED: {len(all_venues)} venues")
                
                # Report failed URLs
                if self.failed_urls:
                    logger.warning(f"⚠️  Failed to scrape {len(self.failed_urls)} URLs:")
                    for url in self.failed_urls[:10]:  # Show first 10 only
                        logger.warning(f"   ❌ {url}")
                    if len(self.failed_urls) > 10:
                        logger.warning(f"   ... and {len(self.failed_urls) - 10} more")
                
                logger.info("🏁 Production scrape completed!")
                
            except Exception as e:
                logger.error(f"💥 Error in production scraping process: {e}")
                # Save whatever we have collected so far
                if self.all_venues:
                    self.save_progress(self.all_venues, "emergency_backup")
            
            finally:
                browser.close()

def main():
    """Main function"""
    logger.info("🎬 Starting BringFido Production Scraper...")
    scraper = BringFidoProductionScraper()
    scraper.run_production_scrape()
    logger.info("🎭 Production scraper finished!")

if __name__ == "__main__":
    main()