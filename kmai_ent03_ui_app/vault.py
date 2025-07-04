import os
import requests
import json
from requests.exceptions import RequestException
from azure.identity import ManagedIdentityCredential
import logging

# Set environment variable
env = os.getenv("ENV", "test")
logger = logging.getLogger(__name__)

class VaultConfig:
    def __init__(self):
        self.vault_login_uri = os.getenv(
            "VAULT_LOGIN_URI", "https://vault-e.dev.azure.com/v1/auth/azure/login"
        )
        self.vault_role = os.getenv(
            "VAULT_ROLE_NAME", "asp-d42-eastus-as-ai-ai-app"
        )

class DcoaiVaultException(Exception):
    pass

class VaultService:
    def __init__(self, config: VaultConfig):
        self.config = config
        self.credential = (
            None if env in ["test", "local"] else ManagedIdentityCredential()
        )

    def get_msi_token(self):
        """Retrieves an access token for Azure Resource Manager using Managed Identity."""
        if env in ["local", "test"]:
            return "token"
        try:
            token = self.credential.get_token("https://management.azure.com/")
            return token.token
        except Exception as e:
            logger.error("Error retrieving MSI token", exc_info=True)
            raise DcoaiVaultException("Failed to retrieve MSI token") from e

    def get_vault_token(self, msi_token):
        """Authenticates to Vault using the MSI token."""
        payload = {"jwt": msi_token, "role": self.config.vault_role}
        try:
            response = requests.post(self.config.vault_login_uri, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("auth", {}).get("client_token")
        except RequestException as e:
            if env in ["local", "test"]:
                return "token"
            logger.error("Vault access issue", exc_info=True)
            raise DcoaiVaultException("Failed to retrieve Vault token") from e

    def read_secret(self, path, key_name, token):
        """Reads a secret from Vault."""
        headers = {"X-Vault-Token": token}
        try:
            response = requests.get(path, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["data"]["data"].get(key_name, "").strip()
        except RequestException as e:
            if env in ["local", "test"]:
                return "token"
            logger.error("Vault access issue", exc_info=True)
            raise DcoaiVaultException("Failed to read secret from Vault") from e

    def get_secret(self, key_name, path, msi_token=None):
        """Retrieves a secret from Vault using Managed Identity authentication."""
        if not msi_token:
            msi_token = self.get_msi_token()
        vault_token = self.get_vault_token(msi_token)
        return self.read_secret(path, key_name, vault_token)
