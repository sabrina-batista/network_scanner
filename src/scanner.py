from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import boto3


WORLD_IPV4 = "0.0.0.0/0"
WORLD_IPV6 = "::/0"


@dataclass
class Finding:
    account_id: str
    region: str
    instance_id: str
    instance_name: str
    vpc_id: str
    security_group_id: str
    security_group_name: str
    protocol: str
    from_port: Optional[int]
    to_port: Optional[int]
    cidr: str
    description: str
    unsafe_port: Optional[int]
    unsafe_meta: Optional[dict]


def _get_account_id(sts_client) -> str:
    return sts_client.get_caller_identity()["Account"]


def _get_instance_name(tags: Optional[List[Dict[str, str]]]) -> str:
    if not tags:
        return ""
    for t in tags:
        if t.get("Key") == "Name":
            return t.get("Value", "")
    return ""


def _port_range_overlaps_port(from_port: Optional[int], to_port: Optional[int], port: int) -> bool:
    if from_port is None or to_port is None:
        return False
    return from_port <= port <= to_port


def scan_region_for_world_exposed_unsafe_ports(
    region: str,
    unsafe_ports: Dict[str, Any],
    only_running: bool = True,
) -> List[Finding]:
    """
    Busca instâncias EC2 e identifica regras inbound abertas para o mundo (IPv4/IPv6)
    que incluam portas listadas em unsafe_ports (chaves do JSON).
    """
    session = boto3.Session(region_name=region)
    ec2 = session.client("ec2")
    sts = session.client("sts")

    account_id = _get_account_id(sts)

    # Paginação
    paginator = ec2.get_paginator("describe_instances")

    filters = []
    if only_running:
        filters.append({"Name": "instance-state-name", "Values": ["running"]})

    findings: List[Finding] = []

    for page in paginator.paginate(Filters=filters):
        for reservation in page.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                instance_id = inst["InstanceId"]
                instance_name = _get_instance_name(inst.get("Tags"))
                vpc_id = inst.get("VpcId", "")
                sgs = inst.get("SecurityGroups", [])

                if not sgs:
                    continue

                # Carrega detalhes dos SGs (para pegar IpPermissions)
                sg_ids = [sg["GroupId"] for sg in sgs if "GroupId" in sg]
                if not sg_ids:
                    continue

                sg_resp = ec2.describe_security_groups(GroupIds=sg_ids)
                for sg in sg_resp.get("SecurityGroups", []):
                    sg_id = sg.get("GroupId", "")
                    sg_name = sg.get("GroupName", "")

                    for perm in sg.get("IpPermissions", []):
                        proto = perm.get("IpProtocol", "")
                        from_port = perm.get("FromPort")
                        to_port = perm.get("ToPort")

                        # Fontes IPv4
                        for r in perm.get("IpRanges", []):
                            cidr = r.get("CidrIp", "")
                            desc = r.get("Description") or ""
                            if cidr != WORLD_IPV4:
                                continue
                            # Se regra é para "all traffic" (-1), From/To podem não existir
                            findings.extend(
                                _evaluate_permission(
                                    account_id, region, instance_id, instance_name, vpc_id,
                                    sg_id, sg_name, proto, from_port, to_port, cidr, desc,
                                    unsafe_ports
                                )
                            )

                        # Fontes IPv6
                        for r in perm.get("Ipv6Ranges", []):
                            cidr = r.get("CidrIpv6", "")
                            desc = r.get("Description") or ""
                            if cidr != WORLD_IPV6:
                                continue
                            findings.extend(
                                _evaluate_permission(
                                    account_id, region, instance_id, instance_name, vpc_id,
                                    sg_id, sg_name, proto, from_port, to_port, cidr, desc,
                                    unsafe_ports
                                )
                            )

    return findings


def _evaluate_permission(
    account_id: str,
    region: str,
    instance_id: str,
    instance_name: str,
    vpc_id: str,
    sg_id: str,
    sg_name: str,
    proto: str,
    from_port: Optional[int],
    to_port: Optional[int],
    cidr: str,
    desc: str,
    unsafe_ports: Dict[str, Any],
) -> List[Finding]:
    """
    Retorna Findings apenas quando a regra aberta para o mundo intersecta portas inseguras.
    Trata também o caso de regra "all traffic" (IpProtocol = -1).
    """
    out: List[Finding] = []

    # Se "all traffic", consideramos como achado genérico de alto risco
    if proto == "-1":
        out.append(
            Finding(
                account_id=account_id,
                region=region,
                instance_id=instance_id,
                instance_name=instance_name,
                vpc_id=vpc_id,
                security_group_id=sg_id,
                security_group_name=sg_name,
                protocol=proto,
                from_port=from_port,
                to_port=to_port,
                cidr=cidr,
                description=desc,
                unsafe_port=None,
                unsafe_meta={"name": "ALL_TRAFFIC", "severity": "critical", "reason": "All traffic exposto para o mundo"}
            )
        )
        return out

    # Checa interseção com as portas inseguras do JSON
    for port_str, meta in unsafe_ports.items():
        try:
            port = int(port_str)
        except ValueError:
            continue

        if _port_range_overlaps_port(from_port, to_port, port):
            out.append(
                Finding(
                    account_id=account_id,
                    region=region,
                    instance_id=instance_id,
                    instance_name=instance_name,
                    vpc_id=vpc_id,
                    security_group_id=sg_id,
                    security_group_name=sg_name,
                    protocol=proto,
                    from_port=from_port,
                    to_port=to_port,
                    cidr=cidr,
                    description=desc,
                    unsafe_port=port,
                    unsafe_meta=meta if isinstance(meta, dict) else {"meta": meta},
                )
            )

    return out
