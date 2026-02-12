**Project Overview**
**The Problem:** Once an attacker gains an initial foothold in a Kubernetes cluster, they begin Lateral Movement—scanning internal ports to find databases or admin panels. Standard firewalls often miss this because the traffic stays "inside" the house.

**The Solution:** We deployed Shadow Services. These are "fake" microservices that look like high-value production databases. Since no legitimate user or service is configured to talk to them, any interaction is a 100% High-Fidelity Alert of a breach.

**Step 1:** The "Bait" (Flask App)
wrote a lightweight Python application using Flask. It mimics an Internal Admin API. If an attacker tries to "Brute Force" the login, the app captures their metadata.

Logic Design:
Path: /api/v1/admin/login (Tempting for scanners).

Security Action: Logs the Source IP, User-Agent, and raw JSON payload (attempted passwords).

Deception: It returns a 401 Unauthorized error to make the attacker believe it is a real, secured service.

**Step 2:** Infrastructure (Kubernetes Setup)
We used Minikube to simulate an enterprise-grade Kubernetes environment locally.

minikube start
eval $(minikube docker-env) # Points Docker to the K8s environment
Containerization
We packaged the Flask app into a Docker image (ephemeral-honeypot:v1) to ensure it can run anywhere in the cluster.

Orchestration (honeypot.yaml)
We defined a Deployment and a Service.

Replicas: We launched 3 instances (Pods) of the honeypot to ensure high availability and a larger "surface area" for the trap.

Service Name: We named the service prod-db-service. In a scan, this looks like a critical production database.

**Step 3.** The Attack Process (Simulation)
To validate the trap, we simulated a compromised container inside the cluster.

Attacker Entry: We ran a temporary "Attacker Pod" using curl.



kubectl run attacker-sim --rm -it --image=curlimages/curl -- sh
Internal Discovery: From inside the cluster, the attacker finds prod-db-service via DNS discovery.

The Probe: The attacker sends a malicious POST request attempting to guess the admin password.

Bash

curl -X POST http://prod-db-service/api/v1/admin/login -d '{"admin":"password123"}'
Step 4. The Detection Process (Forensics)
Detection is instantaneous. Since we are using K8s label selectors, we can watch the logs of all 3 honeypot instances simultaneously.

Analyzing the "Catch":
By running kubectl logs -l app=shadow-db, we identified:
10.244.0.6 - - [12/Feb/2026 04:23:13] "POST /api/v1/admin/login HTTP/1.1" 401 -

Serving Flask app 'honeypot'

Debug mode: off

Source IP: 10.244.0.6 (The exact internal IP of the compromised pod).

Timestamp: The exact second the probe occurred.

Attacker Intelligence: We captured the specific password strings they were using, revealing their "wordlist" or sophistication level.

Security Impact
Zero False Positives: Unlike traditional IDS (Intrusion Detection Systems), this only alerts when someone touches a service they shouldn't.

Early Warning: Detects attackers before they find the real database.

Cost-Effective: Consumes negligible CPU/RAM (Python-slim) while providing massive security visibility.
