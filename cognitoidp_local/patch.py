import copyreg
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from moto.cognitoidp.responses import CognitoIdpResponse
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


def _unserialize_private_key(pem_data):
    """Helper to restore key from bytes."""
    return serialization.load_pem_private_key(pem_data, password=None)


def _serialize_private_key(key):
    """Helper to convert key to bytes."""
    pem_data = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return _unserialize_private_key, (pem_data,)


def apply_crypto_patch():
    """Patches Pickle to support RSAPrivateKey serialization."""
    try:
        # Generate a dummy key to get the class type dynamically
        dummy_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        KeyClass = type(dummy_key)

        # Register the GLOBAL helper function
        copyreg.pickle(KeyClass, _serialize_private_key)
        logger.info(f"Applied cryptography pickle patch for {KeyClass.__name__}.")
    except Exception as e:
        logger.error(f"Failed to patch cryptography: {e}")


def apply_region_patch():
    """
    Patches Moto to return 400 instead of crashing on invalid regions.
    This wraps Moto's internal dictionary lookup.
    If a user requests an invalid region like "eu" instead of "eu-central-1",
    Moto raises a KeyError which crashes the thread.
    We catch it and raise an HTTP 400 BadRequest instead.
    """
    original_backend_prop = CognitoIdpResponse.backend

    def safe_backend_getter(self):
        try:
            return original_backend_prop.fget(self)
        except KeyError as exc:
            logger.warning(f"Blocked crash: Invalid region '{self.region}' requested.")
            raise BadRequest(f"Region '{self.region}' is not valid or not supported.") from exc

    CognitoIdpResponse.backend = property(safe_backend_getter)
    logger.info("Applied region crash patch.")


def apply_all():
    apply_region_patch()
    apply_crypto_patch()
