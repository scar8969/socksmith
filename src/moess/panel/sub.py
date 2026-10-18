import base64
import urllib.parse


def generate_subscription(user, nodes, sub_type="ss"):
    lines = []
    for n in nodes:
        if sub_type == "ss":
            method = n.ss_method or "aes-256-gcm"
            payload = f"{method}:{user.ss_password}@{n.server}:{n.ss_port}"
            lines.append(
                f"ss://{base64.urlsafe_b64encode(payload.encode()).decode().rstrip('=')}#{urllib.parse.quote(n.name)}"
            )
        elif sub_type == "clash":
            lines.append(
                f"  - {{name: {n.name}, server: {n.server}, port: {n.ss_port}, type: ss, cipher: {n.ss_method or 'aes-256-gcm'}, password: {user.ss_password}}}"
            )
    return "\n".join(lines)
