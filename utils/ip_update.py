import requests
import json
import time
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class CloudflareIPUpdater:
    def __init__(self):
        """
        Initialize the CloudflareIPUpdater.
        
        Args:
            api_token (str): Cloudflare API token with DNS edit permissions
            zone_id (str): The zone ID for your domain
            record_names (List[str]): List of A record names to monitor/update
        """
        self.api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        self.zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
        self.record_names = os.getenv("CLOUDFLARE_RECORD_NAMES").split(",")
        self.current_ip: Optional[str] = None
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.cloudflare.com/client/v4"

    def get_current_ip(self) -> str:
        """Get the current public IP address."""
        try:
            response = requests.get("https://api.ipify.org?format=json")
            response.raise_for_status()
            return response.json()["ip"]
        except requests.RequestException as e:
            raise Exception(f"Failed to get current IP: {str(e)}")

    def get_dns_record(self, record_name: str) -> Optional[dict]:
        """Get the DNS record details from Cloudflare."""
        try:
            url = f"{self.base_url}/zones/{self.zone_id}/dns_records"
            params = {"name": record_name, "type": "A"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            records = response.json()["result"]
            return records[0] if records else None
        except requests.RequestException as e:
            raise Exception(f"Failed to get DNS record: {str(e)}")

    def update_dns_record(self, record_id: str, record_name: str, new_ip: str) -> bool:
        """Update the DNS record with a new IP address."""
        try:
            url = f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}"
            data = {
                "type": "A",
                "name": record_name,
                "content": new_ip,
                "proxied": True  # Set to False if you don't want Cloudflare proxying
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to update DNS record: {str(e)}")
            return False

    def check_and_update(self) -> None:
        """Check current IP and update DNS records if needed."""
        try:
            new_ip = self.get_current_ip()
            
            if new_ip == self.current_ip:
                print(f"IP hasn't changed: {new_ip}")
                return
                
            print(f"IP has changed: {self.current_ip} -> {new_ip}")
            self.current_ip = new_ip
            
            for record_name in self.record_names:
                record = self.get_dns_record(record_name)
                if not record:
                    print(f"No DNS record found for {record_name}")
                    continue
                    
                if record["content"] != new_ip:
                    success = self.update_dns_record(
                        record["id"], 
                        record_name, 
                        new_ip
                    )
                    if success:
                        print(f"Updated {record_name} to {new_ip}")
                    else:
                        print(f"Failed to update {record_name}")
                else:
                    print(f"Record {record_name} already has correct IP")
                    
        except Exception as e:
            print(f"Error during check and update: {str(e)}")

    def start_monitoring(self, interval_seconds: int = 300) -> None:
        """Start monitoring IP changes at specified interval."""
        print("Starting IP monitoring...")
        while True:
            self.check_and_update()
            time.sleep(interval_seconds)