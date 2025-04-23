#!/usr/bin/env python3
import os
import json
import argparse
from tabulate import tabulate

def analyze_cross_az_flows(output_format: str):
    base_path = os.path.join(os.path.dirname(__file__), "..", "data")

    with open(os.path.join(base_path, "node_zones.json")) as f:
        node_zones = json.load(f)

    with open(os.path.join(base_path, "ip_to_node.json")) as f:
        ip_to_node = json.load(f)

    with open(os.path.join(base_path, "flow.json")) as f:
        rows = []
        for line in f:
            try:
                record = json.loads(line)
                flow = record.get("flow", {})

                src_node = flow.get("node_name")
                dst_ip = flow.get("IP", {}).get("destination")

                if not src_node or not dst_ip:
                    continue

                dst_node = ip_to_node.get(dst_ip)
                if not dst_node:
                    continue

                src_zone = node_zones.get(src_node, "unknown")
                dst_zone = node_zones.get(dst_node, "unknown")

                if src_zone != dst_zone and "unknown" not in [src_zone, dst_zone]:
                    src_pod = flow.get("source", {}).get("pod_name", "?")
                    dst_pod = flow.get("destination", {}).get("pod_name", "?")
                    src_ns = flow.get("source", {}).get("namespace", "?")
                    dst_ns = flow.get("destination", {}).get("namespace", "?")

                    row = [
                        src_zone, src_node, f"{src_ns}/{src_pod}",
                        dst_zone, dst_node, f"{dst_ns}/{dst_pod}", dst_ip
                    ]

                    if output_format == "table":
                        rows.append(row)
                    else:
                        print(
                            f"🚦 Cross-AZ: [{src_zone}] {src_node} ({src_ns}/{src_pod}) → "
                            f"[{dst_zone}] {dst_node} ({dst_ip} → {dst_ns}/{dst_pod})"
                        )
            except Exception:
                continue

    if output_format == "table":
        headers = [
            "Source Zone", "Source Node", "Source Pod",
            "Destination Zone", "Destination Node", "Destination Pod", "Destination IP"
        ]
        print(tabulate(rows, headers=headers, tablefmt="github"))

def main():
    parser = argparse.ArgumentParser(description="Analyze cross-AZ Hubble flows")
    parser.add_argument(
        "--output", choices=["log", "table"], default="log",
        help="Choose output format: 'log' (default) or 'table'"
    )
    args = parser.parse_args()
    analyze_cross_az_flows(args.output)

if __name__ == "__main__":
    main()
