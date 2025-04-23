# Cross-AZ Flow Detection with Hubble CLI + Kubernetes

This guide helps you:
- Collect enriched network flow logs using Hubble
- Map nodes and pods to AWS Availability Zones
- Detect and analyze **cross-AZ traffic** in your Kubernetes cluster using `Taskfile` automation

---

## ✨ Prerequisites

- Kubernetes cluster with **Cilium** + **Hubble Relay** installed
- Access to `kubectl`
- Python 3
- Tools: `jq`, `hubble` CLI, and `task` runner

###  Install Task:
```bash
brew install go-task/tap/go-task
```

### Install Hubble CLI:
```bash
curl -L --remote-name-all https://github.com/cilium/hubble/releases/latest/download/hubble-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-amd64.tar.gz.sha256sum
tar xzvf hubble-linux-amd64.tar.gz
sudo install -m 0755 hubble /usr/local/bin/hubble
```

---

## 🚀 Quick Start with Poetry & Taskfile

### 🧪 1. Set Up Python Environment with Poetry
```bash
poetry install
poetry run azflow
```
If you're starting fresh:
```bash
poetry init --no-interaction
poetry add --dev black
poetry add tabulate
```

### 🔧 2. Generate Zone and IP Mapping Files
```bash
task setup
```
- Outputs: `data/node_zones.json`, `data/ip_to_node.json`

### 📡 3. Capture and Analyze Flow Logs
```bash
task observe
```
Optional filter example:
```bash
task observe LAST="200" FILTER="--protocol tcp --verdict FORWARDED"
```
Narrow to specific namespace
```bash
task observe \
  FILTER="--protocol tcp --verdict FORWARDED \
    --from-namespace monitoring \
    --to-namespace monitoring" \
  LAST=300
```
Deny labels
```bash
task observe \
  FILTER="--protocol tcp --verdict FORWARDED \
  --denylist '{\"source_label\":[\"k8s:k8s-app=coredns\"],\"destination_label\":[\"k8s:k8s-app=coredns\"]}'" \
  LAST=300
```

- Captures flows to `data/flow.json`
- Analyzes cross-AZ flows with `filter_cross_az_flows.py`
- Cleans up the port-forward

### 🧪 1. Set Up Python Environment with Poetry
```bash
poetry install
poetry run azflow
```
If you're starting fresh:
```bash
poetry init --no-interaction
poetry add --dev black
poetry add tabulate
```

### 🧹 4. Cleanup Resources (Optional)
```bash
task cleanup
```

---

## 📈 Output Example
```
🚦 Cross-AZ: [us-east-1a] ip-10-182-61-104.ec2.internal (mimir-ingester) → [us-east-1c] ip-10-182-124-155.ec2.internal (10.182.124.155 → mimir-distributor)
```

---

## 📊 Next Steps
- Export to CSV
- Summarize flow counts per AZ pair
- Visualize with Prometheus + Grafana

---

## ❓ Can We Filter by Request Size in Hubble?
Currently, **Hubble CLI does not expose request size filters directly**.
- You can filter by protocol, port, or verdict
- Use Prometheus + Cilium metrics (e.g. `hubble_flows_processed_total`) for deeper insights

If request size filtering is critical, consider L7-aware observability tools like Cilium + Prometheus.
