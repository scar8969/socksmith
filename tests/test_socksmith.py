"""A5 moeSS — tests. Run: pytest test_socksmith.py"""
import sys, os

import pytest

def test_subscription_ss():
    from moess.panel.sub import generate_subscription
    import base64, urllib.parse
    class N:
        ss_method = "aes-256-gcm"
        server = "hk01.example.com"
        ss_port = 8388
        name = "HK-01"
    class U:
        ss_password = "secret"
    sub = generate_subscription(U(), [N()], "ss")
    assert sub.startswith("ss://")
    # decode the payload to verify method
    payload = sub[5:].split("#")[0]
    payload += "=" * (-len(payload) % 4)
    decoded = base64.urlsafe_b64decode(payload).decode()
    assert "aes-256-gcm" in decoded
    assert "hk01.example.com" in decoded

def test_subscription_clash():
    from moess.panel.sub import generate_subscription
    class N:
        ss_method = "aes-256-gcm"
        server = "hk01.example.com"
        ss_port = 8388
        name = "HK-01"
    class U:
        ss_password = "secret"
    sub = generate_subscription(U(), [N()], "clash")
    assert "type: ss" in sub

def test_ratelimit_config():
    from moess.panel.ratelimit import config_for
    class U:
        ss_port = 8388
        ss_password = "x"
        ss_method = "aes-256-gcm"
        rate_up_mbps = 10
        rate_down_mbps = 5
    cfg = config_for(U())
    assert cfg["up"] == 10 and cfg["down"] == 5
