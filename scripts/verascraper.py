import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from r2r import R2RClient

class WebScraper:
    def __init__(self, root_url):
        self.root_url = root_url
        self.visited_urls = set()
        self.domain = urlparse(root_url).netloc
        self.pages = {}  # Dictionary to store url:text pairs
        # Add your cookies here
        self.headers = {
            'Cookie': 'last_client_url=/nobles/; _veracross_session=aDg5Q1B2S3g2UnhJem5sTUp4dldKS3ZVc1RyV1NXTXpZYUZGd3M2dWZNSzQ5Yzd0ekxDaS9XaHh6bGg1d3FObkNqcmM5d2pFckRhd3YycENyRyt2U0pEQm5vb1RrbU5YTjJkUjNZZzFKcWs5YUNmVmtzbDZUWEJEYWdrdFgxTjJEL3hmcDVQOHI1TTNxWnJPV040cGhWaUxRQUZwN1lEem8rQ0VveTd5WlhaRVQ4ZEhLTFVjVjhqMjNpZXNLSXBlRnVmakt6RWJvT3FiRjAyb25WS0pqUjhUVlVkNEE5UUVUZ1BsSXV5WUx5TT0tLUpKclhQRndFaWU1MHl4SlFCZGJRWnc9PQ%3D%3D--d33af876fc92fda6298977eab931815c5b43538a; _dd_s=logs=1&id=608a5ea5-9c14-4ece-bfef-91a0aa38df65&created=1734364013633&expire=1734365951399',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def is_valid_url(self, url):
        """Check if URL belongs to same domain and is not a file/anchor"""
        parsed = urlparse(url)
        return (
            parsed.netloc == self.domain and
            not any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif']) and
            not url.startswith('#')
        )

    def get_page_text(self, url):
        """Extract readable text from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style']):
                element.decompose()
                
            return ' '.join(soup.stripped_strings)
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None

    def get_links(self, url):
        """Get all valid links from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = set()
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(url, a_tag['href'])
                if self.is_valid_url(link):
                    links.add(link)
                    
            return links
            
        except Exception as e:
            print(f"Error getting links from {url}: {str(e)}")
            return set()

    def scrape(self):
        """Main scraping method limited to max_pages"""
        queue = [self.root_url]
        pages_dict = {}
        pages_scraped = 0
        client = R2RClient("http://localhost:7272")
        
        while queue:
            current_url = queue.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            print(f"Scraping: {current_url}")
            
            # Get page text
            page_text = self.get_page_text(current_url)
            if page_text:
                # Extract page name from URL
                page_name = urlparse(current_url).path.strip('/').replace('/', '_') or 'home'
                pages_dict[page_name] = page_text
                
                # Ingest document immediately after scraping
                page_string = json.dumps({"name": page_name, "text": page_text})
                response = client.documents.create(
                    raw_text=page_string,
                    ingestion_mode="hi-res",
                    metadata={
                        "title": page_name,
                        "url": current_url,
                        "source": "veracross"
                    }
                )
                print(f"Ingestion response for {page_name}:", response)
                
                pages_scraped += 1
                
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Add new links to queue
            new_links = self.get_links(current_url)
            queue.extend(link for link in new_links if link not in self.visited_urls)
                
            # Be nice to servers
            time.sleep(1)

        return pages_dict

def main():
    root_url = "https://portals.veracross.com/nobles/faculty"
    scraper = WebScraper(root_url)
    pages = scraper.scrape()
    print(f"\nScraped {len(pages)} pages")

if __name__ == "__main__":
    main()
