import os
import requests
from typing import List, Dict, Any
import json

class SpiderFootService:
    def __init__(self):
        self.api_base_url = f"http://localhost:{os.getenv('SPIDERFOOT_API_PORT', '5001')}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def list_scans(self) -> List[Dict[str, Any]]:
        """List all existing scans"""
        try:
            response = requests.get(f"{self.api_base_url}/scanlist", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing scans: {str(e)}")
            return []

    def start_scan(self, name: str, target: str, modules: List[str]) -> Dict[str, Any]:
        """Start a new scan"""
        try:
            data = {
                "scanname": name,
                "scantarget": target,
                "usecase": "all",
                "modulelist": ",".join(modules)
            }
            response = requests.post(f"{self.api_base_url}/startscan", 
                                  headers=self.headers,
                                  json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error starting scan: {str(e)}")
            return {"error": str(e)}

    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get scan status"""
        try:
            response = requests.get(f"{self.api_base_url}/scanstatus", 
                                 params={"id": scan_id},
                                 headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting scan status: {str(e)}")
            return {"error": str(e)}

    def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan"""
        try:
            response = requests.post(f"{self.api_base_url}/scandelete", 
                                  params={"id": scan_id},
                                  headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting scan: {str(e)}")
            return False

    def get_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """Get scan results"""
        try:
            response = requests.get(f"{self.api_base_url}/scaneventresults", 
                                 params={"id": scan_id},
                                 headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting scan results: {str(e)}")
            return {"error": str(e)} 