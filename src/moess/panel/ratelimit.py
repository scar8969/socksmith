from ..models import User


def config_for(user: User) -> dict:
    """Backend shaping config."""
    return {
        "port": user.ss_port,
        "password": user.ss_password,
        "method": user.ss_method,
        "up": user.rate_up_mbps,
        "down": user.rate_down_mbps,
    }
