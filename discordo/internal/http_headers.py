"""HTTP headers and properties for Discord API requests."""

import base64
import json
import uuid
from typing import Dict, Any


# Browser identification
BROWSER = "Chrome"
BROWSER_VERSION = "140.0.0.0"
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

# Locale
LOCALE = "en-US"


def get_headers() -> Dict[str, str]:
    """
    Get standard HTTP headers for Discord API requests.
    
    Returns:
        Dictionary of HTTP headers
    """
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://discord.com",
        "Priority": "u=0, i",
        "Referer": "https://discord.com/channels/@me",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": LOCALE,
    }
    
    # Add X-Super-Properties header
    try:
        super_props = get_super_properties()
        headers["X-Super-Properties"] = super_props
    except Exception as err:
        import logging
        logging.warning(f"Failed to generate X-Super-Properties: {err}")
    
    return headers


def get_identify_properties() -> Dict[str, Any]:
    """
    Get identify properties for Discord gateway connection.
    
    These properties are sent when identifying with the Discord gateway
    to simulate a real Discord client.
    
    Returns:
        Dictionary of identify properties
    """
    return {
        "device": "",
        "os": "Windows",
        "os_version": "10",
        "browser": BROWSER,
        "browser_version": BROWSER_VERSION,
        "browser_user_agent": BROWSER_USER_AGENT,
        "client_build_number": 447677,
        "client_event_source": None,
        "client_app_state": "focused",
        "client_launch_id": str(uuid.uuid4()),
        "client_heartbeat_session_id": str(uuid.uuid4()),
        "launch_signature": str(uuid.uuid4()),
        "system_locale": LOCALE,
        "release_channel": "stable",
        "has_client_mods": False,
        "referrer": "",
        "referrer_current": "",
        "referring_domain": "",
        "referring_domain_current": "",
        "is_fast_connect": False,
        "gateway_connect_reasons": "AppSkeleton",
    }


def get_super_properties() -> str:
    """
    Get X-Super-Properties header value.
    
    This is a base64-encoded JSON representation of identify properties,
    excluding gateway-only properties.
    
    Returns:
        Base64-encoded super properties string
    """
    props = get_identify_properties()
    
    # Remove gateway-only properties
    props.pop("is_fast_connect", None)
    props.pop("gateway_connect_reasons", None)
    
    # Serialize to JSON and encode as base64
    json_str = json.dumps(props, separators=(',', ':'))
    return base64.b64encode(json_str.encode()).decode()
