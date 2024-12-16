import json
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from r2r import R2RClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class InteractiveScraper:
    def __init__(self, root_url):
        self.root_url = root_url
        self.visited_urls = set()
        self.domain = urlparse(root_url).netloc
        # First create a visible browser for login
        self.driver = self._initialize_driver(headless=False)
        self._handle_login()
        # After login, quit the visible browser and create a headless one
        cookies = self.cookies  # Save cookies before quitting
        self.driver.quit()
        self.driver = self._initialize_driver(headless=True)
        # Add cookies to new driver
        self.driver.get(self.root_url)  # Need to be on the domain to add cookies
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        # Refresh page to apply cookies
        self.driver.get(self.root_url)

    def _initialize_driver(self, headless=True):
        """Initialize and configure Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def _handle_login(self):
        """Handle manual login process"""
        self.driver.get(self.root_url)
        print("Please log in to the website in the opened browser window.")
        print("After you have successfully logged in, press Enter here in the terminal.")
        input("Press Enter to continue after logging in...")
        # Get the cookies from the logged-in session
        self.cookies = self.driver.get_cookies()

    def is_valid_url(self, url):
        """Check if URL should be scraped"""
        parsed = urlparse(url)
        if parsed.netloc != self.domain:
            return False
        if any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif']):
            return False
        if url.startswith('#'):
            return False
        # Exclude class-specific URLs
        if url.startswith('https://portals.veracross.com/nobles/faculty/class/'):
            return False
        return True

    def scrape_page(self, url):
        """Scrape content and links from a single page"""
        try:
            self.driver.get(url)
            self._scroll_page()
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            print(f"Requested: {url}")
            print(f"Final URL: {self.driver.current_url}")

            self._remove_unwanted_elements(soup)
            page_text = self._extract_text(soup)
            links = self._extract_links(soup, url)

            return page_text, links

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None, set()

    def _scroll_page(self):
        """Handle page scrolling for lazy loading"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def _remove_unwanted_elements(self, soup):
        """Remove unnecessary HTML elements"""
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            element.decompose()

    def _extract_text(self, soup):
        """Extract text content from HTML"""
        content_areas = soup.find_all(['article', 'main', 'div.content', 'div.main-content'])
        if not content_areas:
            content_areas = [soup.find('body')]

        texts = []
        for area in content_areas:
            if area:
                for element in area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'li']):
                    if element.string:
                        texts.append(element.string.strip())

        return ' '.join(filter(None, texts))

    def _extract_links(self, soup, url):
        """Extract valid links from HTML"""
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(url, a_tag['href'])
            if self.is_valid_url(link):
                links.add(link)
        return links

    def scrape(self):
        """Main scraping method using breadth-first traversal"""
        pages_dict = {}
        page_count = 0
        max_pages = 100
        
        # Initialize with root URL at depth 0
        current_depth_urls = {self.root_url}
        self.visited_urls = set()

        while current_depth_urls and page_count < max_pages:
            print(f"\nProcessing depth {len(self.visited_urls)}")
            next_depth_urls = set()

            # Process all URLs at current depth
            for current_url in current_depth_urls:
                if current_url in self.visited_urls or page_count >= max_pages:
                    continue

                print(f"\nScraping page {page_count + 1}/{max_pages}: {current_url}")
                page_text, new_links = self.scrape_page(current_url)

                if page_text:
                    page_name = urlparse(current_url).path.strip('/').replace('/', '_') or 'home'
                    pages_dict[page_name] = page_text
                    print(f"Text length for {page_name}: {len(page_text)} characters")
                    print(f"Text snippet: {page_text[:200]}...")
                    page_count += 1

                self.visited_urls.add(current_url)
                
                # Add new links to next depth
                next_depth_urls.update(
                    link for link in new_links 
                    if link not in self.visited_urls 
                    and link not in current_depth_urls
                    and page_count < max_pages
                )
                
                time.sleep(0.5)

            # Move to next depth
            current_depth_urls = next_depth_urls

        print(f"\nReached limit of {max_pages} pages or finished scraping all available pages.")
        return pages_dict


def ingest_pages(pages):
    """Ingest scraped pages into R2R"""
    client = R2RClient("http://localhost:7272")
    for page_name, page_text in pages.items():
        page_string = json.dumps({"name": page_name, "text": page_text})
        response = client.documents.create(
            raw_text=page_string,
            ingestion_mode="hi-res",
            metadata={
                "title": page_name,
                "source": "veracross"
            }
        )
        print(f"Ingestion response for {page_name}:", response)


def main():
    root_url = "https://portals.veracross.com/nobles/faculty"
    scraper = InteractiveScraper(root_url)
    pages = scraper.scrape()
    print(f"\nScraped {len(pages)} pages")
    ingest_pages(pages)


if __name__ == "__main__":
    main()
