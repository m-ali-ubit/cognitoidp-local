import pickle

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from moto.cognitoidp.responses import CognitoIdpResponse
from werkzeug.exceptions import BadRequest

from cognitoidp_local import patch


def test_cryptography_patch_serialization():
    """
    Verifies that the custom patch allows pickling of RSAPrivateKey objects.
    """
    patch.apply_crypto_patch()
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    try:
        serialized = pickle.dumps(key)
    except Exception as e:
        pytest.fail(f"Pickling RSA Key failed: {e}")
    try:
        restored_key = pickle.loads(serialized)
    except Exception as e:
        pytest.fail(f"Unpickling RSA Key failed: {e}")
    assert isinstance(restored_key, type(key))
    assert key.private_numbers().p == restored_key.private_numbers().p


def test_region_crash_patch():
    """
    Verifies that accessing an invalid region raises BadRequest (400)
    instead of KeyError (Crash).
    """
    patch.apply_region_patch()

    # Create a dummy object mimicking the structure of CognitoIdpResponse
    # We only need the 'region' and 'current_account' attributes
    class MockResponse:
        region = "mars-1"  # Invalid region
        current_account = "123456789012"

    mock_obj = MockResponse()
    with pytest.raises(BadRequest) as excinfo:
        _ = CognitoIdpResponse.backend.fget(mock_obj)

    assert "Region 'mars-1' is not valid" in str(excinfo.value)
