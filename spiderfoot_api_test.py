import requests
import json
import sys

class SpiderFootAPI:
    def __init__(self, root_url, api_key="spiderfoot123"):
        self.root_url = root_url.rstrip('/')
        self.api_url = f"http://{self.root_url.replace('https://', '')}:81"  # HTTP API port
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
    def scan_list(self):
        """List all scans"""
        url = f"{self.api_url}/api/scans"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing scans: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None

    def start_scan(self, scan_name, scan_target, module_list=None):
        """Start a new scan"""
        url = f"{self.api_url}/api/scan/new"
        
        if not module_list:
            module_list = ["sfp_dns", "sfp_whois"]
            
        data = {
            "scanname": scan_name,
            "scantarget": scan_target,
            "usecase": "all",
            "modulelist": module_list
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error starting scan: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None

def main():
    # Initialize the API wrapper
    sf = SpiderFootAPI("https://spiderfoot.fly.dev")
    
    # List existing scans
    print("\nListing existing scans...")
    scans = sf.scan_list()
    if scans:
        print(json.dumps(scans, indent=2))
    
    # Start a new scan
    print("\nStarting new scan...")
    result = sf.start_scan(
        scan_name="Test Scan",
        scan_target="example.com",
        module_list=["sfp_dns", "sfp_whois"]
    )
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 