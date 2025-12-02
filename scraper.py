"""
Web scraper for extracting mutual fund data from Groww website
"""

import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from urllib.parse import urljoin

import config
from validators import validate_url, validate_all_fields

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GrowwMFScraper:
    """Scraper for Groww mutual fund detail pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.scraped_data = []
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL with retry logic.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if failed
        """
        # Validate URL first
        is_valid, error = validate_url(url)
        if not is_valid:
            logger.error(f"Invalid URL: {url} - {error}")
            return None
        
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{config.MAX_RETRIES})")
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # Check if we got HTML content
                if 'text/html' in response.headers.get('Content-Type', ''):
                    return response.text
                else:
                    logger.warning(f"Unexpected content type for {url}: {response.headers.get('Content-Type')}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching {url} (attempt {attempt + 1}): {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        
        return None
    
    def parse_fund_data(self, html: str, url: str) -> Dict:
        """
        Parse mutual fund data from HTML content.
        
        Args:
            html: HTML content of the page
            url: Source URL
            
        Returns:
            Dictionary with extracted data
        """
        soup = BeautifulSoup(html, 'lxml')
        data = {
            "source_url": url,
            "expense_ratio": None,
            "exit_load": None,
            "minimum_sip": None,
            "lock_in": None,
            "riskometer": None,
            "benchmark": None,
        }
        
        try:
            # Strategy 1: Extract from JSON data embedded in script tags (Groww uses Next.js)
            json_data = self._extract_json_from_script(soup)
            if json_data:
                data = self._parse_json_data(json_data, data, url)
            
            # Strategy 2: Look for table structures (fallback)
            if not all([data["expense_ratio"], data["exit_load"], data["minimum_sip"], 
                       data["lock_in"], data["riskometer"], data["benchmark"]]):
                data = self._extract_from_tables(soup, data)
            
            # Strategy 3: Look for div/list structures with label-value pairs
            if not all([data["expense_ratio"], data["exit_load"], data["minimum_sip"], 
                       data["lock_in"], data["riskometer"], data["benchmark"]]):
                data = self._extract_from_divs(soup, data)
            
            # Strategy 4: Look for text patterns with regex
            if not all([data["expense_ratio"], data["exit_load"], data["minimum_sip"], 
                       data["lock_in"], data["riskometer"], data["benchmark"]]):
                data = self._extract_from_text_patterns(soup, data)
            
            # Strategy 5: Extract riskometer from page text if still missing
            if not data["riskometer"]:
                data = self._extract_riskometer_from_text(soup, data)
            
        except Exception as e:
            logger.error(f"Error parsing HTML for {url}: {e}")
        
        return data
    
    def _extract_json_from_script(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract JSON data from script tags"""
        import json
        import re
        
        # Look for script tags with JSON data (Next.js __NEXT_DATA__ pattern)
        scripts = soup.find_all('script', id='__NEXT_DATA__')
        
        for script in scripts:
            try:
                json_text = script.string
                if json_text:
                    json_obj = json.loads(json_text)
                    return json_obj
            except (json.JSONDecodeError, AttributeError) as e:
                logger.debug(f"Failed to parse JSON from script: {e}")
                continue
        
        # Also try to find JSON in other script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('expense_ratio' in script.string or 'mf' in script.string.lower()):
                try:
                    # Try to extract JSON object from script content
                    json_match = re.search(r'\{.*"expense_ratio".*\}', script.string, re.DOTALL)
                    if json_match:
                        json_obj = json.loads(json_match.group(0))
                        return json_obj
                except (json.JSONDecodeError, AttributeError):
                    continue
        
        return None
    
    def _parse_json_data(self, json_data: Dict, data: Dict, url: str = None) -> Dict:
        """Parse fund data from JSON structure"""
        try:
            # Navigate to the fund data in the JSON structure
            # Based on the HTML structure, data is in props.pageProps.mf
            mf_data = None
            
            if 'props' in json_data and 'pageProps' in json_data['props']:
                if 'mf' in json_data['props']['pageProps']:
                    mf_data = json_data['props']['pageProps']['mf']
            
            if not mf_data:
                return data
            
            # Extract search_id from URL for matching
            search_id = None
            if url:
                # Extract search_id from URL like "parag-parikh-elss-tax-saver-fund-direct-growth"
                parts = url.rstrip('/').split('/')
                if parts:
                    search_id = parts[-1]
            
            # Extract expense ratio
            if not data["expense_ratio"]:
                # Try from historic_fund_expense (latest)
                if 'historic_fund_expense' in mf_data and mf_data['historic_fund_expense']:
                    latest_expense = mf_data['historic_fund_expense'][0]
                    if 'expense_ratio' in latest_expense:
                        data["expense_ratio"] = f"{latest_expense['expense_ratio']}%"
                # Or from direct field
                elif 'expense_ratio' in mf_data:
                    exp_ratio = mf_data['expense_ratio']
                    if isinstance(exp_ratio, str):
                        data["expense_ratio"] = exp_ratio if '%' in exp_ratio else f"{exp_ratio}%"
                    else:
                        data["expense_ratio"] = f"{exp_ratio}%"
            
            # Extract exit load
            if not data["exit_load"]:
                # First check direct exit_load field (may contain full description)
                if 'exit_load' in mf_data and mf_data['exit_load']:
                    exit_load = mf_data['exit_load']
                    if isinstance(exit_load, str) and exit_load.strip():
                        data["exit_load"] = exit_load.strip()
                    elif exit_load != 0:
                        data["exit_load"] = f"{exit_load}%"
                
                # If not found, check historic_exit_loads
                if not data["exit_load"] and 'historic_exit_loads' in mf_data and mf_data['historic_exit_loads']:
                    latest_exit_load = mf_data['historic_exit_loads'][0]
                    
                    # Check note field first (contains full description like "Exit load of 0.25%, if redeemed within 30 days")
                    if latest_exit_load.get('note') and latest_exit_load.get('note').strip():
                        data["exit_load"] = latest_exit_load.get('note').strip()
                    # Check if there's a CDSC (Contingent Deferred Sales Charge) with note
                    elif latest_exit_load.get('cdsc') and latest_exit_load.get('note'):
                        data["exit_load"] = latest_exit_load.get('note').strip()
                    # Check front_load and back_load
                    elif latest_exit_load.get('front_load') == 0 and latest_exit_load.get('back_load') == 0:
                        # Only set to Nil if there's no note field
                        if not latest_exit_load.get('note'):
                            data["exit_load"] = "Nil"
                    else:
                        # Format exit load if present in front_load or back_load
                        exit_load_val = latest_exit_load.get('back_load') or latest_exit_load.get('front_load')
                        if exit_load_val:
                            data["exit_load"] = f"{exit_load_val}%"
                
                # Default to Nil if nothing found
                if not data["exit_load"]:
                    data["exit_load"] = "Nil"
            
            # Extract minimum SIP
            if not data["minimum_sip"]:
                if 'min_sip_investment' in mf_data:
                    min_sip = mf_data['min_sip_investment']
                    data["minimum_sip"] = f"₹{min_sip}"
                elif 'min_investment' in mf_data:
                    min_inv = mf_data['min_investment']
                    data["minimum_sip"] = f"₹{min_inv}"
            
            # Extract lock-in
            if not data["lock_in"]:
                if 'lock_in' in mf_data:
                    lock_in_obj = mf_data['lock_in']
                    if isinstance(lock_in_obj, dict):
                        years = lock_in_obj.get('years')
                        if years is not None and years > 0:
                            data["lock_in"] = f"{int(years)}Y"
                        else:
                            data["lock_in"] = "N/A"
                    elif isinstance(lock_in_obj, (int, float)) and lock_in_obj > 0:
                        data["lock_in"] = f"{int(lock_in_obj)}Y"
                    else:
                        data["lock_in"] = "N/A"
                elif 'additional_details' in mf_data and mf_data['additional_details']:
                    lock_yrs = mf_data['additional_details'].get('lock_in_yrs')
                    if lock_yrs is not None and lock_yrs > 0:
                        data["lock_in"] = f"{int(lock_yrs)}Y"
                    else:
                        data["lock_in"] = "N/A"
                else:
                    data["lock_in"] = "N/A"
            
            # Extract riskometer
            if not data["riskometer"]:
                if 'risk' in mf_data and mf_data['risk']:
                    risk = mf_data['risk']
                    data["riskometer"] = risk + " Risk" if "Risk" not in risk else risk
                elif 'risk_rating' in mf_data:
                    # Map numeric risk rating to text
                    risk_map = {1: "Low Risk", 2: "Low to Moderate Risk", 3: "Moderate Risk",
                               4: "Moderately High Risk", 5: "High Risk", 6: "Very High Risk"}
                    rating = mf_data['risk_rating']
                    if rating in risk_map:
                        data["riskometer"] = risk_map[rating]
                # Try to get from peerComparison (current fund's entry)
                if not data["riskometer"] and 'peerComparison' in mf_data and mf_data['peerComparison']:
                    for peer in mf_data['peerComparison']:
                        # Find the current fund in peer comparison
                        if search_id and peer.get('search_id') == search_id:
                            if 'risk' in peer and peer['risk']:
                                risk = peer['risk']
                                data["riskometer"] = risk + " Risk" if "Risk" not in risk else risk
                                break
                    # If still not found, try partial match
                    if not data["riskometer"] and search_id:
                        for peer in mf_data['peerComparison']:
                            peer_search_id = peer.get('search_id', '')
                            if peer_search_id and search_id in peer_search_id or peer_search_id in search_id:
                                if 'risk' in peer and peer['risk']:
                                    risk = peer['risk']
                                    data["riskometer"] = risk + " Risk" if "Risk" not in risk else risk
                                    break
            
            # Extract benchmark
            if not data["benchmark"]:
                # Prefer benchmark_name for full name
                if 'benchmark_name' in mf_data and mf_data['benchmark_name']:
                    data["benchmark"] = mf_data['benchmark_name']
                elif 'benchmark' in mf_data and mf_data['benchmark']:
                    data["benchmark"] = mf_data['benchmark']
            
        except Exception as e:
            logger.error(f"Error parsing JSON data: {e}")
        
        return data
    
    def _extract_from_tables(self, soup: BeautifulSoup, data: Dict) -> Dict:
        """Extract data from HTML tables"""
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if 'expense' in label and 'ratio' in label and not data["expense_ratio"]:
                        data["expense_ratio"] = value
                    elif 'exit' in label and 'load' in label and not data["exit_load"]:
                        data["exit_load"] = value
                    elif 'minimum' in label and 'sip' in label and not data["minimum_sip"]:
                        data["minimum_sip"] = value
                    elif 'lock' in label and 'in' in label and not data["lock_in"]:
                        data["lock_in"] = value
                    elif 'riskometer' in label or ('risk' in label and 'meter' in label) and not data["riskometer"]:
                        data["riskometer"] = value
                    elif 'benchmark' in label and not data["benchmark"]:
                        data["benchmark"] = value
        
        return data
    
    def _extract_from_divs(self, soup: BeautifulSoup, data: Dict) -> Dict:
        """Extract data from div/list structures"""
        # Look for common patterns: label in one div/span, value in adjacent one
        all_divs = soup.find_all(['div', 'span', 'li', 'p'])
        
        for i, elem in enumerate(all_divs):
            text = elem.get_text(strip=True).lower()
            
            # Check for labels and get adjacent value
            if 'expense' in text and 'ratio' in text and not data["expense_ratio"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["expense_ratio"] = value
            elif 'exit' in text and 'load' in text and not data["exit_load"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["exit_load"] = value
            elif 'minimum' in text and 'sip' in text and not data["minimum_sip"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["minimum_sip"] = value
            elif ('lock' in text and 'in' in text) or 'lock-in' in text and not data["lock_in"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["lock_in"] = value
            elif 'riskometer' in text or ('risk' in text and 'meter' in text) and not data["riskometer"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["riskometer"] = value
            elif 'benchmark' in text and not data["benchmark"]:
                value = self._get_value_from_element(elem)
                if value:
                    data["benchmark"] = value
        
        return data
    
    def _get_value_from_element(self, elem) -> Optional[str]:
        """Extract value from an element or its siblings"""
        # Check if value is in the same element (after colon or in next part)
        text = elem.get_text()
        if ':' in text:
            parts = text.split(':', 1)
            if len(parts) > 1:
                value = parts[1].strip()
                if value and len(value) < 200:
                    return value
        
        # Check next sibling
        next_sib = elem.find_next_sibling()
        if next_sib:
            value = next_sib.get_text(strip=True)
            if value and len(value) < 200:
                return value
        
        # Check parent's next sibling
        parent = elem.parent
        if parent:
            next_sib = parent.find_next_sibling()
            if next_sib:
                value = next_sib.get_text(strip=True)
                if value and len(value) < 200:
                    return value
        
        # Check children for value
        children = elem.find_all(['span', 'div', 'strong', 'b'])
        for child in children:
            value = child.get_text(strip=True)
            if value and len(value) < 200 and value not in ['Expense Ratio', 'Exit Load', 'Minimum SIP', 'Lock-in', 'Riskometer', 'Benchmark']:
                # Check if it looks like a value (has numbers or specific patterns)
                if any(char.isdigit() for char in value) or value.upper() in ['NIL', 'NA', 'N/A']:
                    return value
        
        return None
    
    def _extract_from_text_patterns(self, soup: BeautifulSoup, data: Dict) -> Dict:
        """Extract data using regex patterns on page text"""
        import re
        page_text = soup.get_text()
        
        # Expense Ratio pattern
        if not data["expense_ratio"]:
            pattern = r'expense\s+ratio[:\s]+([0-9.]+%)'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["expense_ratio"] = match.group(1)
        
        # Exit Load pattern
        if not data["exit_load"]:
            pattern = r'exit\s+load[:\s]+(nil|n/a|na|[0-9.]+%)'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["exit_load"] = match.group(1).capitalize() if match.group(1).lower() in ['nil', 'n/a', 'na'] else match.group(1)
        
        # Minimum SIP pattern
        if not data["minimum_sip"]:
            pattern = r'minimum\s+sip[:\s]+(?:₹|rs\.?|inr\s*)?([0-9,]+)'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["minimum_sip"] = f"₹{match.group(1)}"
        
        # Lock-in pattern
        if not data["lock_in"]:
            pattern = r'lock[-\s]?in[:\s]+(?:n/a|na|nil|([0-9]+)\s*(?:y|yr|years?))'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if match.group(1):
                    data["lock_in"] = f"{match.group(1)}Y"
                else:
                    data["lock_in"] = "N/A"
        
        # Riskometer pattern
        if not data["riskometer"]:
            pattern = r'riskometer[:\s]+([a-z\s]+risk)'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["riskometer"] = match.group(1).strip().title()
        
        return data
    
    def _extract_riskometer_from_text(self, soup: BeautifulSoup, data: Dict) -> Dict:
        """Extract riskometer from page text as fallback"""
        import re
        page_text = soup.get_text()
        
        # Common risk patterns in order of specificity
        risk_patterns = [
            (r'(very\s+high\s+risk)', 'Very High Risk'),
            (r'(moderately\s+high\s+risk)', 'Moderately High Risk'),
            (r'(high\s+risk)', 'High Risk'),
            (r'(moderate\s+risk)', 'Moderate Risk'),
            (r'(low\s+to\s+moderate\s+risk)', 'Low to Moderate Risk'),
            (r'(low\s+risk)', 'Low Risk'),
        ]
        
        for pattern, risk_text in risk_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["riskometer"] = risk_text
                logger.info(f"Extracted riskometer from page text: {risk_text}")
                break
        
        # Benchmark pattern
        if not data["benchmark"]:
            pattern = r'benchmark[:\s]+([a-z0-9\s]+index)'
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["benchmark"] = match.group(1).strip()
        
        return data
    
    def _extract_from_attributes(self, soup: BeautifulSoup, data: Dict) -> Dict:
        """Extract data from data attributes"""
        if not data["expense_ratio"]:
            data["expense_ratio"] = self._extract_by_attribute(soup, "expense-ratio", "expenseRatio")
        if not data["exit_load"]:
            data["exit_load"] = self._extract_by_attribute(soup, "exit-load", "exitLoad")
        if not data["minimum_sip"]:
            data["minimum_sip"] = self._extract_by_attribute(soup, "minimum-sip", "minimumSip")
        if not data["lock_in"]:
            data["lock_in"] = self._extract_by_attribute(soup, "lock-in", "lockIn")
        if not data["riskometer"]:
            data["riskometer"] = self._extract_by_attribute(soup, "riskometer", "riskometer")
        if not data["benchmark"]:
            data["benchmark"] = self._extract_by_attribute(soup, "benchmark", "benchmark")
        
        return data
    
    
    def _extract_by_attribute(self, soup: BeautifulSoup, *attribute_names: str) -> Optional[str]:
        """
        Extract value by data attribute names.
        """
        for attr_name in attribute_names:
            # Try different variations
            elements = soup.find_all(attrs={attr_name: True})
            if not elements:
                # Try with data- prefix
                elements = soup.find_all(attrs={f"data-{attr_name}": True})
            
            for element in elements:
                value = element.get(attr_name) or element.get(f"data-{attr_name}")
                if value:
                    return str(value).strip()
                # Or get text content
                text = element.get_text(strip=True)
                if text:
                    return text
        
        return None
    
    def scrape_fund(self, fund_name: str, url: str, save_html: bool = False) -> Dict:
        """
        Scrape a single mutual fund page.
        
        Args:
            fund_name: Name of the fund
            url: URL of the fund page
            save_html: If True, save raw HTML for debugging
            
        Returns:
            Dictionary with scraped data and metadata
        """
        logger.info(f"Scraping {fund_name} from {url}")
        
        html = self.fetch_page(url)
        if not html:
            logger.error(f"Failed to fetch {fund_name}")
            return {
                "fund_name": fund_name,
                "source_url": url,
                "error": "Failed to fetch page",
                "validation_status": "failed"
            }
        
        # Save HTML for debugging if requested
        if save_html:
            import os
            os.makedirs("data/raw", exist_ok=True)
            safe_name = fund_name.lower().replace(" ", "_").replace("/", "_")
            with open(f"data/raw/{safe_name}.html", "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"Saved HTML to data/raw/{safe_name}.html")
        
        data = self.parse_fund_data(html, url)
        data["fund_name"] = fund_name
        
        # Validate extracted data
        is_valid, errors = validate_all_fields(data)
        data["validation_status"] = "valid" if is_valid else "invalid"
        data["validation_errors"] = errors
        
        if not is_valid:
            logger.warning(f"Validation failed for {fund_name}: {errors}")
        else:
            logger.info(f"Successfully scraped and validated {fund_name}")
        
        return data
    
    def scrape_all_funds(self) -> List[Dict]:
        """
        Scrape all funds defined in config.
        
        Returns:
            List of dictionaries with scraped data
        """
        results = []
        
        for fund_name, url_slug in config.PARAG_PARIKH_FUNDS.items():
            url = urljoin(config.BASE_URL, url_slug)
            
            # Scrape the fund
            data = self.scrape_fund(fund_name, url)
            results.append(data)
            
            # Add delay between requests
            time.sleep(config.REQUEST_DELAY)
        
        self.scraped_data = results
        return results

