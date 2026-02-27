from __future__ import annotations

import json
import os
from typing import List

from .scanner import scan_region_for_world_exposed_unsafe_ports, Finding
from .emailer_smtp import (
    build_email_subject,
    build_email_body_text,
    send_email_via_smtp,
)


def load_unsafe_ports(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_csv_env(name: str, default: str = "") -> List[str]:
    raw = os.environ.get(name, default).strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def main() -> int:
    # ── Configuração de regiões e portas ──────────────────────────────────────
    unsafe_ports_path = os.environ.get("UNSAFE_PORTS_PATH", "config/unsafe_ports.json")
    regions = parse_csv_env("AWS_REGIONS", os.environ.get("AWS_REGION", "us-east-1"))
    only_running = os.environ.get("ONLY_RUNNING", "true").lower() == "true"

    # ── Configuração SMTP ─────────────────────────────────────────────────────
    smtp_host = os.environ["SMTP_HOST"]                          # ex: smtp.gmail.com
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ["SMTP_USER"]                          # ex: alertas@empresa.com
    smtp_password = os.environ["SMTP_PASSWORD"]
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
    use_starttls = os.environ.get("SMTP_USE_STARTTLS", "false").lower() == "true"

    email_sender = os.environ["EMAIL_SENDER"]                    # ex: alertas@empresa.com
    email_recipients = parse_csv_env("EMAIL_RECIPIENTS")         # ex: sec@empresa.com,ti@empresa.com

    if not email_recipients:
        raise RuntimeError("Defina EMAIL_RECIPIENTS (separado por vírgula).")

    # ── Scan ──────────────────────────────────────────────────────────────────
    unsafe_ports = load_unsafe_ports(unsafe_ports_path)

    all_findings: List[Finding] = []
    for region in regions:
        all_findings.extend(
            scan_region_for_world_exposed_unsafe_ports(
                region=region,
                unsafe_ports=unsafe_ports,
                only_running=only_running,
            )
        )

    if not all_findings:
        print("Nenhum achado. Nenhum email enviado.")
        return 0

    # ── Envio de email ────────────────────────────────────────────────────────
    subject = build_email_subject(all_findings)
    body = build_email_body_text(all_findings)

    send_email_via_smtp(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        sender=email_sender,
        recipients=email_recipients,
        subject=subject,
        body_text=body,
        use_tls=use_tls,
        use_starttls=use_starttls,
    )
    print(f"Email enviado para {email_recipients} com {len(all_findings)} achado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
