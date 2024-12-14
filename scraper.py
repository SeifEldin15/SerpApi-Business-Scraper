import requests
import time
import json
import os
from urllib.parse import urlparse
from serpapi import GoogleSearch
from pathlib import Path
import urllib.request
import hashlib

# Add this list at the top of the file
AUSTRALIAN_LOCATIONS = [
    # New South Wales
    'Sydney, New South Wales, Australia',
    'Newcastle, New South Wales, Australia',
    'Wollongong, New South Wales, Australia',
    'Central Coast, New South Wales, Australia',
    'Port Macquarie, New South Wales, Australia',
    'Coffs Harbour, New South Wales, Australia',
    'Wagga Wagga, New South Wales, Australia',
    'Albury, New South Wales, Australia',
    'Dubbo, New South Wales, Australia',
    'Tamworth, New South Wales, Australia',
    'Orange, New South Wales, Australia',
    'Bathurst, New South Wales, Australia',

    # Victoria
    'Melbourne, Victoria, Australia',
    'Geelong, Victoria, Australia',
    'Ballarat, Victoria, Australia',
    'Bendigo, Victoria, Australia',
    'Shepparton, Victoria, Australia',
    'Mildura, Victoria, Australia',
    'Warrnambool, Victoria, Australia',
    'Wodonga, Victoria, Australia',

    # Queensland
    'Brisbane, Queensland, Australia',
    'Gold Coast, Queensland, Australia',
    'Sunshine Coast, Queensland, Australia',
    'Townsville, Queensland, Australia',
    'Cairns, Queensland, Australia',
    'Toowoomba, Queensland, Australia',
    'Mackay, Queensland, Australia',
    'Rockhampton, Queensland, Australia',
    'Bundaberg, Queensland, Australia',
    'Hervey Bay, Queensland, Australia',

    # Western Australia
    'Perth, Western Australia, Australia',
    'Mandurah, Western Australia, Australia',
    'Bunbury, Western Australia, Australia',
    'Geraldton, Western Australia, Australia',
    'Kalgoorlie, Western Australia, Australia',
    'Albany, Western Australia, Australia',
    'Broome, Western Australia, Australia',

    # South Australia
    'Adelaide, South Australia, Australia',
    'Mount Gambier, South Australia, Australia',
    'Whyalla, South Australia, Australia',
    'Port Augusta, South Australia, Australia',
    'Port Lincoln, South Australia, Australia',
    'Murray Bridge, South Australia, Australia',

    # Tasmania
    'Hobart, Tasmania, Australia',
    'Launceston, Tasmania, Australia',
    'Devonport, Tasmania, Australia',
    'Burnie, Tasmania, Australia',

    # Northern Territory
    'Darwin, Northern Territory, Australia',
    'Alice Springs, Northern Territory, Australia',
    'Katherine, Northern Territory, Australia',

    # Australian Capital Territory
    'Canberra, Australian Capital Territory, Australia',
    'Belconnen, Australian Capital Territory, Australia',
    'Tuggeranong, Australian Capital Territory, Australia'
]

def download_image(url, folder_path, business_name):
    """Helper function to download an image and save it with a unique filename"""
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        # Create a unique filename using hash of URL
        hash_object = hashlib.md5(url.encode())
        file_ext = Path(urlparse(url).path).suffix or '.jpg'
        filename = f"{business_name}_{hash_object.hexdigest()[:8]}{file_ext}"
        filepath = Path(folder_path) / filename

        # Download with requests instead of urllib
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes

        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return str(filepath)
    except Exception as e:
        print(f"Failed to download image {url}: {str(e)}")
        return None

def search_places(query, api_key, output_file='yeah tghis is it.txt'):
    url = 'https://serpapi.com/search.json'
    total_results = []
    
    # Create base images folder
    base_folder = Path('venue_images')
    base_folder.mkdir(exist_ok=True)
    
    for location in AUSTRALIAN_LOCATIONS:
        print(f"\nSearching in {location}...")
        start = 0
        no_results_count = 0
        
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Results for {location}\n")
            f.write(f"{'='*50}\n\n")
        
        while True:
            params = {
                'q': query,
                'location': location,
                'hl': 'en',
                'gl': 'AU',
                'api_key': api_key,
                'engine': 'google_local',
                'type': 'search',
                'start': start,
                'num': 100  # Request more results per page if possible
            }
            
            print(f"Fetching results {start+1}-{start+20}...")
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'error' in data:
                    print(f"Error: {data['error']}")
                    break
                    
                local_results = data.get('local_results', [])
                
                if not local_results:
                    no_results_count += 1
                    print(f"No results on this page. Empty page count: {no_results_count}")
                    if no_results_count >= 3:
                        print("Multiple empty pages received. Ending search.")
                        break
                    time.sleep(2)
                    start += 20
                    continue
                
                no_results_count = 0
                
                with open(output_file, 'a', encoding='utf-8') as f:
                    for result in local_results:
                        if isinstance(result, dict):
                            place_info = {
                                'name': result.get('title'),
                                'address': result.get('address'),
                                'full_address': result.get('complete_address', ''),
                                'street_address': result.get('street_address', ''),
                                'locality': result.get('locality', ''),
                                'region': result.get('region', ''),
                                'postal_code': result.get('postal_code', ''),
                                'latitude': result.get('gps_coordinates', {}).get('latitude', ''),
                                'longitude': result.get('gps_coordinates', {}).get('longitude', ''),
                                'rating': result.get('rating'),
                                'reviews': result.get('reviews'),
                                'phone': result.get('phone'),
                                'category': result.get('type'),
                                'website': result.get('website'),
                                'additional_links': result.get('links', []),
                                'business_website': result.get('service_options', {}).get('website', ''),
                                'hours': result.get('hours'),
                                'thumbnail': result.get('thumbnail'),
                                'photos': result.get('photos', []),
                                'price': result.get('price', ''),
                                'gps_coordinates': result.get('gps_coordinates', {}),
                                'place_id': result.get('place_id', ''),
                                'google_maps_link': f"https://www.google.com/maps/place/?q=place_id:{result.get('place_id')}" if result.get('place_id') else None,
                                'all_photos': result.get('images', []) if result.get('images') else result.get('photos', []),
                            }
                            
                            # Add additional images search for each place
                            try:
                                image_params = {
                                    "q": f"{place_info['name']} {place_info['address']}",
                                    "engine": "google_images",
                                    "api_key": api_key,
                                    "num": 10  # Get up to 10 images per place
                                }
                                image_search = GoogleSearch(image_params)
                                image_results = image_search.get_dict()
                                
                                # Add images to place_info
                                if 'images_results' in image_results:
                                    place_info['additional_images'] = [
                                        {
                                            'thumbnail': img.get('thumbnail'),
                                            'original': img.get('original'),
                                            'source': img.get('source')
                                        }
                                        for img in image_results['images_results'][:10]
                                    ]
                                time.sleep(2)  # Respect rate limits
                            except Exception as e:
                                print(f"Error fetching additional images: {str(e)}")
                                place_info['additional_images'] = []
                            
                            if place_info['name'] and place_info['address']:
                                total_results.append(place_info)
                                
                                # Create a folder for this business
                                business_name = "".join(x for x in place_info['name'] if x.isalnum() or x in (' ', '-', '_'))
                                business_folder = base_folder / business_name
                                business_folder.mkdir(exist_ok=True)
                                
                                # Download and store image paths
                                downloaded_images = []
                                
                                # Download thumbnail
                                if place_info['thumbnail']:
                                    img_path = download_image(place_info['thumbnail'], business_folder, business_name)
                                    if img_path:
                                        downloaded_images.append(img_path)
                                
                                # Download photos
                                if place_info['photos']:
                                    for photo in place_info['photos']:
                                        if isinstance(photo, dict) and 'image' in photo:
                                            img_path = download_image(photo['image'], business_folder, business_name)
                                            if img_path:
                                                downloaded_images.append(img_path)
                                
                                # Download additional images
                                if place_info.get('additional_images'):
                                    for img in place_info['additional_images']:
                                        if img.get('original'):
                                            img_path = download_image(img['original'], business_folder, business_name)
                                            if img_path:
                                                downloaded_images.append(img_path)
                                
                                # Add downloaded image paths to place_info
                                place_info['downloaded_images'] = downloaded_images
                                
                                # Write business info to file
                                f.write(f"Name: {place_info['name']}\n")
                                f.write(f"Address: {place_info['address']}\n")
                                if place_info['rating']:
                                    f.write(f"Rating: {place_info['rating']}\n")
                                if place_info['reviews']:
                                    f.write(f"Reviews: {place_info['reviews']}\n")
                                if place_info['price']:
                                    f.write(f"Price: {place_info['price']}\n")
                                if place_info['phone']:
                                    f.write(f"Phone: {place_info['phone']}\n")
                                if place_info['category']:
                                    f.write(f"Category: {place_info['category']}\n")
                                if place_info['website']:
                                    f.write(f"Main Website: {place_info['website']}\n")
                                if place_info['business_website']:
                                    f.write(f"Business Website: {place_info['business_website']}\n")
                                if place_info['additional_links']:
                                    f.write("Additional Links:\n")
                                    for link in place_info['additional_links']:
                                        if isinstance(link, dict):
                                            link_text = link.get('text', '')
                                            link_url = link.get('link', '')
                                            if link_url:
                                                f.write(f"- {link_text}: {link_url}\n")
                                        elif isinstance(link, str):
                                            f.write(f"- {link}\n")
                                if place_info['hours']:
                                    f.write(f"Hours: {place_info['hours']}\n")
                                
                                # Add image URLs directly in the main file
                                if place_info['thumbnail']:
                                    f.write(f"Thumbnail URL: {place_info['thumbnail']}\n")
                                
                                if place_info['photos']:
                                    f.write("Photo URLs:\n")
                                    for photo in place_info['photos']:
                                        if isinstance(photo, dict) and 'image' in photo:
                                            f.write(f"- {photo['image']}\n")
                                
                                # Add Google Maps link
                                if place_info['google_maps_link']:
                                    f.write(f"Google Maps: {place_info['google_maps_link']}\n")
                                
                                # Add GPS coordinates if available
                                if place_info['gps_coordinates']:
                                    f.write(f"GPS Coordinates: {place_info['gps_coordinates']}\n")
                                
                                # Enhanced image handling
                                if place_info['all_photos']:
                                    f.write("All Photos:\n")
                                    for photo in place_info['all_photos']:
                                        if isinstance(photo, dict):
                                            if 'image' in photo:
                                                f.write(f"- {photo['image']}\n")
                                            if 'original' in photo:
                                                f.write(f"- {photo['original']}\n")
                                            if 'thumbnail' in photo:
                                                f.write(f"- {photo['thumbnail']}\n")
                                        elif isinstance(photo, str):
                                            f.write(f"- {photo}\n")
                                
                                # Add the additional images to the output file
                                if place_info['additional_images']:
                                    f.write("Additional Images:\n")
                                    for img in place_info['additional_images']:
                                        f.write(f"- Thumbnail: {img['thumbnail']}\n")
                                        f.write(f"  Original: {img['original']}\n")
                                        f.write(f"  Source: {img['source']}\n")
                                
                                # Add downloaded image paths to the output file
                                if downloaded_images:
                                    f.write("\nDownloaded Images:\n")
                                    for img_path in downloaded_images:
                                        f.write(f"- {img_path}\n")
                                
                                f.write("\n" + "-"*30 + "\n\n")
                            
                print(f"Found {len(local_results)} venues in this batch. Total so far: {len(total_results)}")
                time.sleep(2)
                start += 20
                
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                time.sleep(5)
                continue
    
    # Update final summary
    total_found = len(total_results)
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"FINAL SUMMARY\n")
        f.write(f"Total venues found across Australia: {total_found}\n")
        f.write(f"Locations searched: {', '.join(AUSTRALIAN_LOCATIONS)}\n")
    
    print(f"\nSearch complete! Total venues found across Australia: {total_found}")
    return total_results

# Usage example
if __name__ == '__main__':
    api_key = '20402ecb74d2098f5ec8109db0258c962845611afe14ec895074756b7f81c346'   
    try:
        results = search_places(
            query='wedding venue', 
            api_key=api_key
        )
    except Exception as e:
        print(f"Error: {str(e)}")