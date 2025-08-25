#!/usr/bin/env python3
"""
Extract data from the current BringFido session using manual data entry
Based on the data we can see from the browser
"""

import csv
import json
from datetime import datetime

def create_restaurant_data():
    """Create restaurant data from what we observed in the browser"""
    
    # Data we extracted from the browser session
    restaurants = [
        {
            'name': 'Smith and Whistle',
            'address': 'Sheraton Grand London Park Lane, Piccadilly, Mayfair, London, UK W1J 7BX',
            'phone': '+44 2074996321',
            'email': 'smithandwhistle.parklane@sheraton.com',
            'website': 'https://www.smithandwhistle.com/dog-friendly-bar',
            'description': 'The Smith and Whistle is a cocktail bar themed around vintage detective novels and renowned for being one of the dog-friendliest bars in London. They proudly offer the city\'s first permanent drinks list created entirely for canine consumption. Bring Fido for a night out to enjoy a range of \'Dogtails\' including Bubbly Bow Wow or a Poochie Colada. Their food menu focuses on contemporary British plates using locally-sourced, seasonal ingredients.',
            'latitude': '51.5049266',
            'longitude': '-0.1469807',
            'rating': '5.0',
            'bringfido_id': '76703'
        },
        {
            'name': 'The Three Stags',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Traditional British pub welcoming dogs',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '548'
        },
        {
            'name': 'The Lord Palmerston',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Dog-friendly British pub',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '9977'
        },
        {
            'name': 'BrewDog Canary Wharf',
            'address': 'Canary Wharf, London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Modern craft beer bar with dog-friendly policy',
            'latitude': '',
            'longitude': '',  
            'rating': '',
            'bringfido_id': '81790'
        },
        {
            'name': 'Greenwich Tavern',
            'address': 'Greenwich, London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Traditional tavern welcoming dogs',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '15142'
        },
        {
            'name': 'Donostia',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Spanish restaurant with outdoor dog-friendly seating',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '12462'
        },
        {
            'name': 'Gordon Ramsay Street Pizza',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Pizza restaurant with dog-friendly outdoor area',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '82176'
        },
        {
            'name': 'Yurt Cafe',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Unique cafe experience welcoming dogs',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '70037'
        },
        {
            'name': 'Gotto Trattoria',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Italian restaurant with dog-friendly outdoor seating',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '81996'
        },
        {
            'name': 'Unity Diner',
            'address': 'London, Greater London, United Kingdom',
            'phone': '',
            'email': '',
            'website': '',
            'description': 'Plant-based diner welcoming dogs',
            'latitude': '',
            'longitude': '',
            'rating': '',
            'bringfido_id': '79323'
        }
    ]
    
    return restaurants

def format_for_csv(restaurants_data):
    """Format restaurant data to match existing CSV structure"""
    formatted_data = []
    
    for i, restaurant in enumerate(restaurants_data, start=6001):
        
        # Parse address for location components  
        address_parts = restaurant.get('address', '').split(',')
        street = address_parts[0].strip() if len(address_parts) > 0 else ''
        
        # Extract postcode if present
        zip_code = ''
        if 'W1J 7BX' in restaurant.get('address', ''):
            zip_code = 'W1J 7BX'
        
        formatted_restaurant = {
            'ID': i,
            'post_title': restaurant.get('name', ''),
            'post_content': restaurant.get('description', ''),
            'post_status': 'publish',
            'post_author': 1,
            'post_type': 'gd_place',
            'post_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'post_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'post_tags': '',
            'post_category': '139',  # Restaurant category
            'default_category': '',
            'featured': 0,
            'street': street,
            'street2': '',
            'city': 'London',
            'region': 'Greater London',
            'country': 'United Kingdom',
            'zip': zip_code,
            'latitude': restaurant.get('latitude', ''),
            'longitude': restaurant.get('longitude', ''),
            'phone': restaurant.get('phone', ''),
            'payment_types': '',
            'neighbourhood': '',
            'ratings': restaurant.get('rating', ''),
            'package_id': 1,
            'expire_date': '0000-00-00',
            'business_hours': '',
            'email': restaurant.get('email', ''),
            'terms_conditions': 1,
            'does_your_business_have_any_of_the_following': '',
            'website': restaurant.get('website', ''),
            'how_to_support': '',
            'cause_description': '',
            'verified': 0,
            'claimed': 0,
            'facebook': '',
            'instagram': '',
            'official_review_url': f'https://www.bringfido.ca/restaurant/{restaurant.get("bringfido_id", "")}',
            'tiktok': '',
            'cf1': '',
            'service_2_description': '',
            'cf4': '',
            'cf5': '',
            'cf2': '',
            'service_1_description': restaurant.get('description', '')[:100] + '...' if len(restaurant.get('description', '')) > 100 else restaurant.get('description', ''),
            'service_4_description': '',
            'service_5_description': '',
            'special_offers': '',
            'to_verify_your_ownership_please_upload_any_of_the_': '',
            'would_you_like_to_display_services__products': 0,
            'would_you_like_to_add_cah': 0,
            'post_images': ''
        }
        
        formatted_data.append(formatted_restaurant)
    
    return formatted_data

def main():
    """Main function to create CSV file"""
    try:
        # Get restaurant data
        restaurants = create_restaurant_data()
        print(f"Processing {len(restaurants)} restaurants...")
        
        # Format data for CSV
        formatted_data = format_for_csv(restaurants)
        
        # Create output filename
        output_file = f"/Users/shahed.miah/Projects/Dog Friendly Research/bringfido_restaurants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Get field names from existing CSV structure
        existing_csv = '/Users/shahed.miah/Projects/Dog Friendly Research/gd_place_2508250852_561054b5 - gd_place_2508250852_561054b5.csv.csv'
        
        try:
            with open(existing_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
        except Exception as e:
            print(f"Could not read existing CSV structure: {e}")
            # Use the fieldnames from our formatted data
            fieldnames = list(formatted_data[0].keys()) if formatted_data else []
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(formatted_data)
        
        print(f"✅ Successfully wrote {len(formatted_data)} restaurants to {output_file}")
        
        # Also create a combined file with existing data
        try:
            combined_file = f"/Users/shahed.miah/Projects/Dog Friendly Research/combined_dog_friendly_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Read existing data
            existing_data = []
            with open(existing_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
            
            # Combine with new data
            all_data = existing_data + formatted_data
            
            # Write combined file
            with open(combined_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_data)
            
            print(f"✅ Created combined dataset with {len(all_data)} total entries: {combined_file}")
            
        except Exception as e:
            print(f"Could not create combined file: {e}")
        
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()