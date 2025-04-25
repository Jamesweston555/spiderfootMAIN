import requests
import json
import sys
from typing import List, Optional

class SpiderFootAPI:
    def __init__(self, base_url: str, api_key: str = "spiderfoot123"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
    def scan_list(self) -> Optional[List[dict]]:
        """List all scans"""
        url = f"{self.base_url}/scans"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing scans: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def start_scan(self, name: str, target: str, modules: Optional[List[str]] = None) -> Optional[dict]:
        """Start a new scan"""
        url = f"{self.base_url}/scans"
        
        if not modules:
            modules = ["sfp_dns", "sfp_whois"]
            
        data = {
            "name": name,
            "target": target,
            "modules": modules
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error starting scan: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def get_scan_status(self, scan_id: str) -> Optional[dict]:
        """Get scan status"""
        url = f"{self.base_url}/scans/{scan_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting scan status: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def get_scan_results(self, scan_id: str) -> Optional[dict]:
        """Get scan results"""
        url = f"{self.base_url}/scans/{scan_id}/results"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting scan results: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan"""
        url = f"{self.base_url}/scans/{scan_id}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting scan: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return False

def main():
    # Initialize the API wrapper
    sf = SpiderFootAPI("http://localhost:8000")
    
    # List existing scans
    print("\nListing existing scans...")
    scans = sf.scan_list()
    if scans:
        print(json.dumps(scans, indent=2))
    
    # Start a new scan
    print("\nStarting new scan...")
    result = sf.start_scan(
        name="Test Scan",
        target="example.com",
        modules=["sfp_dns", "sfp_whois"]
    )
    if result:
        print(json.dumps(result, indent=2))
        
        # Get scan status
        print("\nGetting scan status...")
        status = sf.get_scan_status(result["id"])
        if status:
            print(json.dumps(status, indent=2))
            
            # Get scan results
            print("\nGetting scan results...")
            results = sf.get_scan_results(result["id"])
            if results:
                print(json.dumps(results, indent=2))
                
                # Delete scan
                print("\nDeleting scan...")
                if sf.delete_scan(result["id"]):
                    print("Scan deleted successfully")

if __name__ == "__main__":
    main() 