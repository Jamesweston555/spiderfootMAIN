import subprocess
import json
from typing import List, Optional
from datetime import datetime

class SpiderFootService:
    def __init__(self, spiderfoot_path: str = "."):
        self.spiderfoot_path = spiderfoot_path

    def list_scans(self) -> List[dict]:
        """List all SpiderFoot scans."""
        try:
            result = subprocess.run(
                ["python", f"{self.spiderfoot_path}/sf.py", "-l"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Failed to list scans: {result.stderr}")
            
            # Parse the output
            scans = []
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        scan_id = parts[0]
                        name = parts[1]
                        target = parts[2]
                        scans.append({
                            "id": scan_id,
                            "name": name,
                            "target": target
                        })
            return scans
        except Exception as e:
            raise Exception(f"Error listing scans: {str(e)}")

    def start_scan(self, name: str, target: str, modules: List[str]) -> dict:
        """Start a new SpiderFoot scan."""
        try:
            cmd = [
                "python", f"{self.spiderfoot_path}/sf.py",
                "-s", name,
                "-t", target,
                "-m", ",".join(modules)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to start scan: {result.stderr}")
            
            # Get the scan ID from the output
            scan_id = None
            for line in result.stdout.splitlines():
                if "Scan ID:" in line:
                    scan_id = line.split("Scan ID:")[1].strip()
                    break
            
            if not scan_id:
                raise Exception("Could not determine scan ID")
            
            return {
                "id": scan_id,
                "name": name,
                "target": target,
                "status": "running",
                "created": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Error starting scan: {str(e)}")

    def get_scan_status(self, scan_id: str) -> dict:
        """Get the status of a SpiderFoot scan."""
        try:
            cmd = ["python", f"{self.spiderfoot_path}/sf.py", "-q", scan_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to get scan status: {result.stderr}")
            
            # Parse the status from the output
            status = "unknown"
            for line in result.stdout.splitlines():
                if "Status:" in line:
                    status = line.split("Status:")[1].strip().lower()
                    break
            
            return {
                "id": scan_id,
                "status": status
            }
        except Exception as e:
            raise Exception(f"Error getting scan status: {str(e)}")

    def delete_scan(self, scan_id: str) -> bool:
        """Delete a SpiderFoot scan."""
        try:
            cmd = ["python", f"{self.spiderfoot_path}/sf.py", "-d", scan_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to delete scan: {result.stderr}")
            
            return True
        except Exception as e:
            raise Exception(f"Error deleting scan: {str(e)}")

    def get_scan_results(self, scan_id: str) -> dict:
        """Get the results of a SpiderFoot scan."""
        try:
            cmd = ["python", f"{self.spiderfoot_path}/sf.py", "-r", scan_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to get scan results: {result.stderr}")
            
            # Parse the results
            results = []
            for line in result.stdout.splitlines():
                if line.strip():
                    # Parse the line into a result object
                    # This is a placeholder - you'll need to implement proper parsing
                    results.append({"data": line})
            
            return {
                "id": scan_id,
                "results": results
            }
        except Exception as e:
            raise Exception(f"Error getting scan results: {str(e)}") 