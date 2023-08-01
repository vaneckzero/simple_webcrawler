import requests
import bs4
import argparse
from collections import deque
from urllib.parse import urljoin, urlparse

# Define argument parser
parser = argparse.ArgumentParser(description='Web crawler script.')
parser.add_argument('start_url', type=str, help='Starting URL')
parser.add_argument('user_agent', type=str, help='User-Agent for the web crawler')
args = parser.parse_args()

# Initialize the headers using provided user-agent
headers = {
    "User-Agent": args.user_agent,
    "From": "youremail@domain.com"
}

start_url = args.start_url  # Starting URL

# Set maximum depth for non-target domain
MAX_DEPTH = 1

queue = deque([(start_url, 0)])  # Queue now also stores depth info
visited_urls = set()  # Create an empty set to store visited URLs

# For storing the failed URLs
failed_urls = {}

def same_domain(url1, url2):
    return urlparse(url1).netloc == urlparse(url2).netloc

while len(queue) != 0:
    url, depth = queue.popleft()

    # If we have already visited this URL, skip
    if url in visited_urls:
        continue

    visited_urls.add(url)

    try:
        # Set a timeout for requests
        res = requests.get(url, headers=headers, timeout=3)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        # Print the URL and the status code
        print(f"{url}: {res.status_code}")

        # If HTTP status is not 200, save it to the dictionary
        if res.status_code != 200:
            failed_urls[url] = res.status_code

        # Only crawl other links if the current URL is from the target domain or the depth is less than MAX_DEPTH
        if same_domain(url, start_url) or depth < MAX_DEPTH:
            # Find all the links on the webpage
            for link in soup.find_all('a'):
                href = link.get('href')

                # Skip if href is None
                if href is None:
                    continue

                # Build the full URL if it's a relative link
                if href.startswith('/'):
                    new_url = urljoin(url, href)
                    queue.append((new_url, depth+1))
                elif href.startswith('http'):
                    new_url = href
                    queue.append((new_url, depth+1))

    except Exception as e:
        print(f"Error for URL {url}: {str(e)}")
        failed_urls[url] = str(e)

# Print summary of links with non-200 status codes
print("\n\n---Failed URLs---")
for url, error in failed_urls.items():
    print(f"{url}: {error}")
