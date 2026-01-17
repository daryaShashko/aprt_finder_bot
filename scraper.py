import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Optional

# User-Agent to mimic a real browser and avoid 403 Forbidden
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def fetch_ad_urls(url: str) -> List[str]:
    """
    Fetches the list of ad URLs from the given OLX listing URL.
    Returns a list of full URLs to the ads.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # OLX structure changes often, but typically ads are in <a> tags within a listing container.
        # We look for links that look like ad pages.
        # This selector targets the common ad card links.
        # Note: Selectors might need adjustment if OLX updates their UI.
        ad_links = []
        
        # Broad implementation: finding all links that contain '/d/' which usually indicates an ad or category.
        # Filter for actual ad links.
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Check for standard OLX ad path or promoted ads
            if "/d/oferta/" in href:
                full_url = href if href.startswith("http") else f"https://www.olx.pl{href}"
                # Remove anchor parameters to get clean URL and avoid duplicates
                if "#" in full_url:
                    full_url = full_url.split("#")[0]
                ad_links.append(full_url)
                
        # Remove duplicates
        return list(set(ad_links))

    except requests.RequestException as e:
        logging.error(f"Error fetching ad list: {e}")
        return []

def fetch_ad_content(url: str) -> Optional[str]:
    """
    Fetches the text content of a specific ad.
    Returns the combined title and description text.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Try to find title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        
        # Try to find description
        # OLX often uses a div with logging-level-1 or similar class for description
        # Fallback to finding the largest text block or specific container
        description_div = soup.find("div", {"data-cy": "ad_description"})
        if not description_div:
             # Fallback: look for common description containers
             description_div = soup.find("div", class_="css-bgzo2k") # Example class, might be unstable

        description = description_div.get_text(separator="\n", strip=True) if description_div else "No Description"
        
        return f"Title: {title}\n\nDescription:\n{description}"

    except requests.RequestException as e:
        logging.error(f"Error fetching ad content for {url}: {e}")
        return None
