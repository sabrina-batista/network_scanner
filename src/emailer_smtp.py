from __future__ import annotations

from typing import List
import boto3

from .scanner import Finding


def build_email_subject(findings: List[Finding]) -> str:
    critical = sum(1 for f in findings if (f.unsafe_meta or {}).get("severity") in ("critical", "high"))
    return f"[ALERTA] Exposição de portas inseguras (achados={len(findings)}, alto/crit={critical})"


def build_email_body_text(findings: List[Finding]) -> str:
    lines = []
    lines.append("Foram detectadas regras INBOUND abertas para o mundo em instâncias AWS (EC2).")
    lines.append("")
    for f in findings:
        sev = (f.unsafe_meta or {}).get("severity", "unknown")
        reason = (f.unsafe_meta or {}).get("reason", "")
        port_info = "ALL" if f.unsafe_port is None else str(f.unsafe_port)
        lines.append(
            f"- account={f.account_id} region={f.region} instance={f.instance_id} name='{f.instance_name}' "
            f"sg={f.security_group_id}({f.security_group_name}) proto={f.protocol} "
            f"ports={f.from_port}-{f.to_port} unsafe_port={port_info} cidr={f.cidr} severity={sev} reason='{reason}'"
        )
    lines.append("")
    lines.append("Ação recomendada: restringir origem (CIDR), usar bastion/VPN, ou limitar por SG/PrefixList.")
    return "\n".join(lines)


def send_email_via_ses(
    region: str,
    sender: str,
    recipients: List[str],
    subject: str,
    body_text: str,
) -> None:
    ses = boto3.client("ses", region_name=region)
    ses.send_email(
        Source=sender,
        Destination={"ToAddresses": recipients},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body_text, "Charset": "UTF-8"}},
        },
    )
