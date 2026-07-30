import urllib.request
import json
import os
import time

BLOG_URL = "https://tr.tabirly.com"
BATCH_SIZE = 150
INDEX_FILE = os.path.join(os.path.dirname(__file__), "search-index.json")

def fetch_all_posts():
    print(f"Fetching posts from {BLOG_URL}...")
    start_index = 1
    all_posts = []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    while True:
        url = f"{BLOG_URL}/feeds/posts/summary?alt=json&max-results={BATCH_SIZE}&start-index={start_index}"
        
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                data = json.loads(res.read().decode('utf-8'))
                feed = data.get('feed', {})
                entries = feed.get('entry', [])
                
                if not entries:
                    print("No more entries found.")
                    break
                
                for entry in entries:
                    title = entry.get('title', {}).get('$t', '').strip()
                    
                    # Extract URL path (relative to save bandwidth)
                    full_url = ''
                    for link in entry.get('link', []):
                        if link.get('rel') == 'alternate':
                            full_url = link.get('href', '')
                            break
                    
                    path = full_url.replace(BLOG_URL, '') if full_url.startswith(BLOG_URL) else full_url
                    
                    # Extract image/thumbnail if present
                    media_thumbnail = entry.get('media$thumbnail', {})
                    img_url = media_thumbnail.get('url', '') if media_thumbnail else ''
                    
                    # Extract first category/label
                    categories = [c.get('term', '') for c in entry.get('category', []) if c.get('term')]
                    category = categories[0] if categories else ''
                    
                    all_posts.append({
                        't': title,
                        'u': path,
                        'i': img_url,
                        'c': category
                    })
                
                print(f"Batch at index {start_index}: got {len(entries)} items. Total indexed: {len(all_posts)}")
                
                start_index += len(entries)
                time.sleep(0.1)  # Light delay
                
        except Exception as e:
            print(f"Error fetching batch at start-index {start_index}: {e}")
            break
            
    print(f"Finished! Total posts indexed: {len(all_posts)}")
    return all_posts

def main():
    posts = fetch_all_posts()
    if posts:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, separators=(',', ':'))
        
        size_kb = round(os.path.getsize(INDEX_FILE) / 1024, 2)
        print(f"Successfully saved {len(posts)} posts to {INDEX_FILE} ({size_kb} KB)")

if __name__ == '__main__':
    main()
