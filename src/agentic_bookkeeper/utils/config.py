"""
Configuration management for Agentic Bookkeeper.

This module handles loading, validation, and encryption of configuration data.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for Agentic Bookkeeper.

    Handles loading from .env files, JSON configuration files,
    and API key encryption/decryption.
    """

    def __init__(self, env_file: str = ".env", config_dir: str = "./config"):
        """
        Initialize configuration manager.

        Implements environment variable precedence (highest to lowest priority):
        1. System environment variables (e.g., set in ~/.bashrc, /etc/environment)
        2. Session environment variables (e.g., export VAR=value)
        3. .env file values (DEVELOPMENT ONLY)

        load_dotenv() only sets variables that are not already in the environment,
        ensuring that system/session variables always take precedence over .env file.

        Args:
            env_file: Path to .env file (for development only)
            config_dir: Directory containing JSON config files
        """
        self.env_file = Path(env_file)
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._cipher: Optional[Fernet] = None

        # Load environment variables from .env file (only if not already set)
        # This preserves system/session environment variable precedence
        load_dotenv(self.env_file)

        # Initialize encryption
        self._init_encryption()

        # Load configuration
        self._load_config()

    def _init_encryption(self) -> None:
        """Initialize encryption cipher for API keys."""
        # Use a machine-specific key derived from environment
        # In production, this should use a more secure key storage method
        salt = b"agentic_bookkeeper_salt_2025"  # Static salt (not ideal for production)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        # Derive key from machine ID or user-specific data
        machine_id = os.environ.get("MACHINE_ID", "default_machine_id")
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        self._cipher = Fernet(key)

    def _load_config(self) -> None:
        """Load configuration from environment and JSON files."""
        # Load from environment
        self._config = {
            "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
            "tax_jurisdiction": os.getenv("TAX_JURISDICTION", "CRA"),
            "fiscal_year_start": os.getenv("FISCAL_YEAR_START", "01-01"),
            "watch_directory": os.getenv("WATCH_DIRECTORY", "./data/watch"),
            "processed_directory": os.getenv("PROCESSED_DIRECTORY", "./data/processed"),
            "database_path": os.getenv("DATABASE_PATH", "./data/bookkeeper.db"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE", "./logs/agentic_bookkeeper.log"),
        }

        # Load API keys (encrypted)
        self._config["api_keys"] = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "xai": os.getenv("XAI_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
        }

        # Load categories from JSON
        self._load_categories()

        # Validate configuration
        self.validate()

        logger.info("Configuration loaded successfully")

    def _load_categories(self) -> None:
        """Load tax categories from JSON files."""
        try:
            # Load CRA categories
            cra_file = self.config_dir / "categories_cra.json"
            if cra_file.exists():
                with open(cra_file, "r") as f:
                    self._config["cra_categories"] = json.load(f)
            else:
                logger.warning(f"CRA categories file not found: {cra_file}")
                self._config["cra_categories"] = []

            # Load IRS categories
            irs_file = self.config_dir / "categories_irs.json"
            if irs_file.exists():
                with open(irs_file, "r") as f:
                    self._config["irs_categories"] = json.load(f)
            else:
                logger.warning(f"IRS categories file not found: {irs_file}")
                self._config["irs_categories"] = []

        except Exception as e:
            logger.error(f"Failed to load categories: {e}")
            self._config["cra_categories"] = []
            self._config["irs_categories"] = []

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate LLM provider
        valid_providers = ["openai", "anthropic", "xai", "google"]
        if self._config["llm_provider"] not in valid_providers:
            raise ValueError(
                f"Invalid LLM provider: {self._config['llm_provider']}. "
                f"Must be one of {valid_providers}"
            )

        # Validate tax jurisdiction
        valid_jurisdictions = ["CRA", "IRS"]
        if self._config["tax_jurisdiction"] not in valid_jurisdictions:
            raise ValueError(
                f"Invalid tax jurisdiction: {self._config['tax_jurisdiction']}. "
                f"Must be one of {valid_jurisdictions}"
            )

        # Validate fiscal year start (MM-DD format)
        fiscal_year_start = self._config["fiscal_year_start"]
        if not self._validate_fiscal_year_format(fiscal_year_start):
            raise ValueError(
                f"Invalid fiscal year start: {fiscal_year_start}. " f"Must be in MM-DD format"
            )

        # Validate directories exist or can be created
        for dir_key in ["watch_directory", "processed_directory"]:
            dir_path = Path(self._config[dir_key])
            dir_path.mkdir(parents=True, exist_ok=True)

        # Validate log directory
        log_file = Path(self._config["log_file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_fiscal_year_format(date_str: str) -> bool:
        """Validate MM-DD format."""
        try:
            month, day = date_str.split("-")
            month_int = int(month)
            day_int = int(day)
            return 1 <= month_int <= 12 and 1 <= day_int <= 31
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def get_api_key(self, provider: str) -> str:
        """
        Get API key for a provider.

        Args:
            provider: Provider name ('openai', 'anthropic', 'xai', 'google')

        Returns:
            API key (decrypted if necessary)
        """
        return self._config["api_keys"].get(provider, "")

    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider.

        Args:
            provider: Provider name
            api_key: API key value
        """
        self._config["api_keys"][provider] = api_key

    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key.

        Args:
            api_key: Plain text API key

        Returns:
            Encrypted API key (base64 encoded)
        """
        if not api_key:
            return ""
        encrypted = self._cipher.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key.

        Args:
            encrypted_key: Encrypted API key (base64 encoded)

        Returns:
            Decrypted API key
        """
        if not encrypted_key:
            return ""
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            return ""

    def get_categories(self, jurisdiction: Optional[str] = None) -> list:
        """
        Get tax categories for jurisdiction.

        Args:
            jurisdiction: Tax jurisdiction ('CRA' or 'IRS'). If None, uses config value.

        Returns:
            List of category names
        """
        if jurisdiction is None:
            jurisdiction = self._config["tax_jurisdiction"]

        if jurisdiction == "CRA":
            return self._config.get("cra_categories", [])
        elif jurisdiction == "IRS":
            return self._config.get("irs_categories", [])
        else:
            return []

    def get_current_provider(self) -> str:
        """Get currently configured LLM provider."""
        return self._config["llm_provider"]

    def get_watch_directory(self) -> Path:
        """Get watch directory path."""
        return Path(self._config["watch_directory"])

    def get_processed_directory(self) -> Path:
        """Get processed directory path."""
        return Path(self._config["processed_directory"])

    def get_database_path(self) -> Path:
        """Get database file path."""
        return Path(self._config["database_path"])

    def get_log_level(self) -> str:
        """Get logging level."""
        return self._config["log_level"]

    def get_log_file(self) -> Path:
        """Get log file path."""
        return Path(self._config["log_file"])

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary (without sensitive data).

        Returns:
            Configuration dictionary
        """
        config_copy = self._config.copy()
        # Remove sensitive data
        config_copy["api_keys"] = {
            provider: "***" if key else "" for provider, key in config_copy["api_keys"].items()
        }
        return config_copy

    def __str__(self) -> str:
        """Return string representation without sensitive data."""
        return (
            f"Config(provider={self._config['llm_provider']}, "
            f"jurisdiction={self._config['tax_jurisdiction']})"
        )
