Jenkins + ArgoCD GitOps CI/CD for SaaS App.

This project demonstrates a complete GitOps CI/CD pipeline where developers push code, Jenkins builds and pushes Docker images, updates Kubernetes manifests in a GitOps repo, and Argo CD automatically deploys the app to a Kubernetes cluster. It also includes Prometheus monitoring and Grafana dashboards for observability. This is ideal for modern SaaS applications that need fully automated, reliable deployments.

---

# 1) Overview (quick flow)

```
Developer push (app repo)
   ↓ (webhook)
Jenkins (builds image & tags e.g. username/app:123) 
   ↓ (push to Docker Hub)
Jenkins (clone GitOps repo → update dev/app-deployment.yaml image: field → commit & push)
   ↓
Argo CD (auto-sync + self-heal) reads GitOps repo → deploys to Kubernetes
   ↓
Prometheus scrapes app + node-exporter → Grafana visualizes metrics
```

---

# 2) Repos & files you need

* **App repo** (example): `https://github.com/<you>/sassappcode`

  * must contain: `Dockerfile`, `app.py` (Flask), `requirements.txt`, optional `Jenkinsfile` but we place Jenkinsfile in the APP_repo too.
    
* **GitOps repo** (example): `https://github.com/<you>/Argocd-connector-saas`

  * must contain k8s manifests under a folder `dev/`:

    * `dev/app-deployment.yaml` (Deployment + Service)
    * `dev/prometheus.yaml` (Deployment/ConfigMap/Service)
    * `dev/grafana.yaml` (Deployment/Service)
    * `dev/node-exporter.yaml` (DaemonSet)
  * ArgoCD will watch `dev/` and deploy all manifests.

---

# 3) Environment & prerequisites (install locally or cloud)

* Git + GitHub access (token)
* Docker (Docker Desktop or Docker CE with Docker_credentials Token)
* Kubernetes cluster (Docker Desktop Kubernetes, kind, or cloud EKS/GKE/AKS)
* `kubectl`, `helm`, `git`, `docker`, and Jenkins (container or VM)
* Argo CD installed into the cluster

Commands to check tools:

```bash
git --version
docker --version
kubectl version --client
helm version
```

---

# 4) Install Argo CD (commands)

If you haven’t installed Argo CD yet:

```bash
kubectl create namespace argocd

# install via helm (recommended)
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd --namespace argocd
```

Port-forward to open UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8000:443
# Browse: https://localhost:8000 
```

Get initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode
```
```
Open http://localhost:8000
```

🚀 Deploy Application via Argo CD

```Log in to Argo CD UI.

Click + New App → Fill in details:
General

Application Name: my-web-app
Project: default
Sync Policy: Automatic (PRUNE + SELF HEAL)
Source

Repository URL: https://github.com/<your-username>/my-gitops-repo.git
Revision: HEAD
Path: dev
Destination

Cluster URL: https://kubernetes.default.svc
Namespace: my-web-app-ns (Enable AUTO-CREATE NAMESPACE)
Click CREATE — Argo CD will sync your app automatically.

```
🏃 Access the Application

Port-forward the service:

kubectl port-forward svc/demo-app(servicename for app) -n my-web-app-ns 5000:80
```
Then open: http://localhost:5000
```
---

# 5) Jenkins: install & plugins (quick)



**Jenkins itself cannot talk to Docker**

Here’s why and how to fix it:

### 1. Check your Jenkins setup

* If you are using **Jenkins inside a container** (common with Docker-based Jenkins), that container **does not have access to the host’s Docker daemon** by default.
* `docker build` runs inside the Jenkins container, but it needs access to the Docker daemon (`/var/run/docker.sock`) to work.

---

### 2. Solutions

#### **Option A — If Jenkins is a container**

Run Jenkins container with Docker socket mounted:

```bash
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home:/var/jenkins_home \
  -p 8080:8080 \
  --name jenkins-docker \
  jenkins/jenkins:lts
```
> Mounting `/var/run/docker.sock` is needed if Jenkins needs to run Docker build on host. (We later fixed socket permissions.)
This gives the Jenkins container access to the host Docker daemon.

---

#### **Option B — Install Docker on Jenkins host**

If Jenkins runs directly on a VM or physical machine:

1. Make sure Docker is installed:

```bash
docker --version
sudo systemctl status docker
```

2. Ensure the `jenkins` user can access Docker:

```bash
sudo usermod -aG docker jenkins
```

Then **restart Jenkins** or log out/in to apply group permissions.

---

#### **Option C — Use Docker-in-Docker (dind)**

* Only if you want Jenkins to run its **own Docker daemon inside the container**.
* More complex, usually Option A is simpler.

---
In this project i used Option-A
```
docker exec -it -u root <container_id> bash #using root is not safe for production
docker info
usermod -aG docker jenkins #Add Jenkins user to Docker group
docker restart <container_id>
docker exec -it <container_id> bash
id jenkins #You should see docker in the list
 ```uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins),103(docker)```

docker exec -it -u jenkins <container_id> bash -c "id && docker ps -a || echo 'docker command failed with exit code $?'"

```
Now the jenkins Pipeline will able to build and push images to docker registery

**Required Jenkins plugins** (Manage Jenkins → Manage Plugins → Install):

* Git Plugin
* Pipeline (Pipeline: Groovy)
* Credentials Plugin
* Docker Pipeline (if you want `withDockerRegistry`, `docker` step)
* GitHub Integration or GitHub plugin (for webhook support)
* Docker

Install them and restart Jenkins if necessary.

---

# 6) Jenkins setup (credentials + webhook)

Inside Jenkins:

* **Add credentials** (Manage Jenkins → Credentials → Global):

  * Docker Hub: type *Username with password*

    * id = `dockerhub-creds` (example)
    * username = DockerHub username
    * password = **Docker Hub access token** (NOT your account password; create it on Docker Hub Security → New Access Token)


* GitHub (for pushing to GitOps repo): type *Username with password* or *Secret text (token)*
    * id = `sassapp-id` (example) with PAT that has repo:reade & write on `sassappcde`

  * GitHub (for pushing to GitOps repo): type *Username with password* or *Secret text (token)*
    * id = `argocd-id` (example) with PAT that has repo:Read & write on `Argocd-connector-saas`
  

* **Create a pipeline job**:

  * New Item → Pipeline →Check GithubProject -> check Github HookTrigger  link to the app repo Jenkinsfile using pipeline script from SCM.

* **Enable webhook on GitHub**:

  * Repo → Settings → Webhooks → Add webhook
  * Payload URL: `https://<your-jenkins-host>/github-webhook/` (if Jenkins is local, use ngrok to expose)
  * Content type: `application/json`
  * Events: `push`

**If local Jenkins is not publicly reachable**: use `ngrok` for dev:

```bash
ngrok http 8080
# Use the generated https URL: https://abcd1234.ngrok.io/github-webhook/
```

---


# 8) GitOps manifests 

```
Add all Necessary .yaml file
```

# 10) Full run / test flow (commands and checks)

1. **Push code (app repo)**:

```bash
# make small change e.g. index.html or app.py
git add .
git commit -m "feat: test change"
git push origin main
```

2. **Jenkins job triggers** (via webhook). If not reachable, run:

```bash
# (manually) - run build now in Jenkins UI or trigger from github webhook
```

3. **Check Jenkins logs**:

* In Jenkins job → Console Output.
  Or if Jenkins installed locally:

```bash
# tail logs inside container
docker logs -f jenkins-docker
```

4. **Check image on Docker Hub**:
   Go to Docker Hub or:

```bash
docker pull muthuraj07/gitapp:<build-number>
```

5. **Check GitOps repo updated**:

```bash
# on GitHub or locally
git clone https://github.com/user-name/Argocd-connector-saas
cd Argocd-connector-saas/dev
grep image -R .
```

6. **Argo CD UI**: port-forward and open:

```bash
kubectl port-forward svc/argocd-server -n argocd 8000:443
# visit https://localhost:8080
```

* Argo CD should show `my-sass-app` auto-syncing and status **Synced / Healthy**.

7. **Check Kubernetes pods**:

```bash
kubectl get pods -n demo-app
kubectl describe deployment demo-app -n demo-app
kubectl logs <pod-name> -n demo-app
```

8. **Port-forward app/service for check**:

```bash
kubectl port-forward svc/my-sass-app -n my-sass-app 5000:5000
# Visit http://localhost:5000
```

9. **Prometheus & Grafana access**:

```bash
kubectl port-forward svc/prometheus-service -n demo-app 9090:9090
kubectl port-forward svc/grafana-service -n demo-app 3000:3000
# Visit http://localhost:9090 and http://localhost:3000 (login: admin/admin default)
```

---

# 11) Common errors you saw and exact fixes

### A. `git push` rejected: remote contains work you do not have locally

Fix:

```bash
git pull --rebase origin main
# resolve conflicts if any:
git status
# edit files, then
git add <file>
git rebase --continue
# finally
git push origin main
```

If you must overwrite (use with caution):

```bash
git push origin main --force
```

### B. `interactive rebase in progress` / unmerged files

If `git status` shows `both added: Dockerfile` (no <<<< markers), choose local or remote:

Keep local:

```bash
git checkout --ours Dockerfile app.py requirements.txt
git add Dockerfile app.py requirements.txt
git rebase --continue
```

Keep remote:

```bash
git checkout --theirs Dockerfile app.py requirements.txt
git add ...
git rebase --continue
```

### C. Docker login unauthorized / must use token

* Create Docker Hub token (Docker Hub UI → Security → New Access Token)
* Update Jenkins credential to use username + token (password field).

### D. `No such DSL method 'withDockerRegistry'`

Install **Docker Pipeline** plugin in Jenkins. Or use fallback login method (see Jenkinsfile fallback).

### E. `Cannot connect to the Docker daemon` / `permission denied on /var/run/docker.sock`

* If Jenkins runs in container, mount docker socket:

```bash
docker run -d -v /var/run/docker.sock:/var/run/docker.sock ...
```

* Ensure `jenkins` user is in host's `docker` group or the socket is owned by `root:docker` and group ID matches:

```bash
# On host: get docker group GID
getent group docker
# Inside jenkins container (root):
groupmod -g <host-docker-gid> docker
usermod -aG docker jenkins
# Or change socket:
chown root:docker /var/run/docker.sock
chmod 660 /var/run/docker.sock
```

If quick test:

```bash
chmod 666 /var/run/docker.sock  # temporary and insecure
```

### F. ArgoCD `InvalidSpecError: Namespace ... is missing.`

Either:

* Add `metadata.namespace: <name>` to **each** manifest (Service, Deployment, ConfigMap), or
* Set default `destination.namespace` in the ArgoCD `Application` (preferred):

```yaml
spec:
  destination:
    namespace: demo-app
```

and `kubectl create ns demo-app`.

### G. Kind / LoadBalancer / Envoy errors (`SyncLoadBalancerFailed`, `exit status 125`, containers stuck `Created`)

Fix sequence:

```bash
# remove stuck created containers (names from docker ps -a)
docker rm -f <containerIDs...>

# ensure kind network exists
docker network ls
docker network create kind   # if missing

# ensure ports (5000,3000,9090) not used by other containers
docker ps

# delete cloud-provider-kind pods so they can be re-created
kubectl delete pod -n kube-system -l app=cloud-provider-kind
# watch restart
kubectl get pods -n kube-system -w
```

---

# 12) Helpful commands & logs (quick list)

* Jenkins logs (container):

```bash
docker logs -f jenkins-docker
```

* View Jenkins pipeline console in UI → job → Console Output
* Check docker containers & details:

```bash
docker ps -a
docker logs <container-id>
docker inspect <container-id>
```

* Kubernetes basics:

```bash
kubectl get pods -n demo-app
kubectl describe pod <pod> -n demo-app
kubectl logs <pod> -n demo-app
kubectl get events -n demo-app --sort-by='.lastTimestamp'
```

* ArgoCD application status:

```bash
kubectl get applications -n argocd
kubectl describe application my-sass-app -n argocd
```

* Show resource diff:

```bash
argocd app diff my-sass-app   # if using argocd CLI
```

---

# 13) TL;DR quick commands cheat-sheet

**Install Argo CD**

```bash
kubectl create ns argocd
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd --namespace argocd
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**Start Jenkins (container) with Docker socket**

```bash
docker run -d --name jenkins-docker -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins:lts
```

**Fix docker socket permissions (in container as root)**

```bash
chown root:docker /var/run/docker.sock
chmod 660 /var/run/docker.sock
# verify jenkins user is in docker group:
id jenkins
```

**Run Jenkins pipeline test (Docker commands)**

```bash
# create pipeline job with a simple script:
sh 'docker version && docker ps -a'
```

**Create namespaces**

```bash
kubectl create ns demo-app
kubectl create ns monitoring
```

**Apply ArgoCD Application manifest**

```bash
kubectl apply -f argocd-application.yaml
```

**Force re-sync (ArgoCD UI or CLI)**

```bash
argocd app sync my-sass-app
```

---

## Final notes & next steps

* Keep images versioned (build number or git short sha) — DO NOT use `latest` for production.
* Use CI pipeline tests (unit/integration) before pushing images.
* For production, run Jenkins on a VM/cloud (not container with host socket) or use dedicated build workers.
* Add Slack/email notifications in Jenkins and Argo CD alerts for failures.
* Consider `yq` instead of `sed` for safely editing YAML.

---
