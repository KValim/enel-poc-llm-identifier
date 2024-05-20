"""
This module provides tools to retrieve and manage public IP address information and associated
geolocation details using external APIs.

Classes:
    IPInfo: A class to fetch the public IP address of the current device and to retrieve location
    information for any given IP address using the ipinfo.io API.

Exceptions:
    ConnectionError: An error thrown when the API calls fail to execute due to connectivity issues
    or incorrect responses.
"""

import requests

class IPInfo:
    """
    Class to retrieve public IP address and location information using external APIs.

    Attributes:
        access_token (str): Access token for ipinfo.io API.
    """

    API_IP_URL = "https://api64.ipify.org?format=json"
    API_INFO_URL = "https://ipinfo.io/{ip_address}?token={token}"

    def __init__(self, access_token: str):
        """
        Initializes the IPInfo class with necessary API access token.

        Args:
            access_token (str): Access token for the ipinfo.io service.
        """
        self.access_token = access_token

    def get_public_ip(self) -> str:
        """Retrieves the public IP address of the current device."""
        try:
            response = requests.get(self.API_IP_URL)
            response.raise_for_status()  # Raises HTTPError for bad requests
            ip_data = response.json()
            return ip_data['ip']
        except requests.RequestException as e:
            raise ConnectionError("Failed to retrieve IP address.") from e

    def get_ip_location(self, ip_address: str) -> dict:
        """
        Retrieves location information for a given IP address.

        Args:
            ip_address (str): The public IP address.

        Returns:
            dict: A dictionary containing location information.
        """
        try:
            response = requests.get(self.API_INFO_URL.format(ip_address=ip_address, token=self.access_token))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError("Failed to retrieve location information.") from e

# Usage example:
# ip_info = IPInfo(access_token='your_access_token_here')
# public_ip = ip_info.get_public_ip()
# location_info = ip_info.get_ip_location(public_ip)
# print(f"Public IP: {public_ip}")
# print(f"Location Info: {location_info}")
