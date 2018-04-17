## Objective
Setup Datadog monitoring. Sign-up datadog (limited monotoring capability is free after trial) to use.

## How to run
./scripts/main.sh or
./scripts/main.sh <env|inventory> <ansible_remote_user> <args>

args can specify ansible options such as --chech or -e variable=value

## DATADOG_API_KEY environment variable.
Set the Datadog API_KEY to DATADOG_API_KEY environment variable.

## Structure

```
.
├── Readme.md
├── diff.sh
├── plays
│   ├── handlers
│   │   ├── restart_datadog.yml
│   │   └── restart_worker.yml
│   ├── roles
│   │   ├── dd_installation      <---- datadog agent installation on nodes
│   │   ├── dd_service_account   <---- K8S service account setup for datadog
│   │   ├── kube_state_metrics   <---- kube-state-metrics pod deployment
│   │   ├── dd_daemonset         <---- datadog agent pod deployment (not enabled due to security of docker socket mount)
│   │   ├── dd_kubernetes        <---- datadog k8s monitoring on host (not daemonset)
│   │   ├── dd_kubernetes_state  <---- datadog kube-state-metrics monitoring on host
│   │   ├── dd_etcd              <---- datadog etcd monitoring
│   │   ├── dd_k8s_master        <---- datadog k8s master component monitoring
│   │   └── dd_application       <---- datadog application liveness checks
│   ├── site.yml
│   ├── masters.yml
│   └── workers.yml
└── scripts
    └── main.sh

```