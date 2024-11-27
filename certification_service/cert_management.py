import os
import subprocess
import config
from dotenv import load_dotenv
from logger import logger

# Load environment variables from .env file
load_dotenv()

# Ensure certificates directory exists
os.makedirs(config.CERTIFICATES_DIR, exist_ok=True)


def ensure_certificate_and_key_exist():
    """Ensure that the private key, certificate, and PFX file exist."""
    key_path = os.path.join(config.CERTIFICATES_DIR, "private.key")
    cert_path = os.path.join(config.CERTIFICATES_DIR, "certificate.crt")
    pfx_path = os.path.join(config.CERTIFICATES_DIR, "certificate.pfx")

    if not os.path.exists(key_path):
        logger.info("Private key not found. Generating a new private key...")
        subprocess.run([
            "openssl", "genpkey", "-algorithm", "RSA", "-out", key_path
        ], check=True)

    if not os.path.exists(cert_path):
        logger.info("Certificate not found. Generating a new self-signed certificate...")
        subprocess.run([
            "openssl", "req", "-x509", "-nodes", "-days", "365",
            "-newkey", "rsa:2048", "-keyout", key_path, "-out", cert_path,
            "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=localhost"
        ], check=True)

    if not os.path.exists(pfx_path):
        logger.info("PFX file not found. Creating a new PFX file...")
        subprocess.run([
            "openssl", "pkcs12", "-export", "-out", pfx_path,
            "-inkey", key_path, "-in", cert_path,
            "-passout", f"pass:{config.PFX_PASSPHRASE}"
        ], check=True)
