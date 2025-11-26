### 1\. Instalar os CRDs da Gateway API (Método Oficial)

[cite\_start]Este comando baixa e aplica as definições exatas suportadas pela versão 2.2.1[cite: 29].

```bash
kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.2.1" | kubectl apply -f -
```

### 2\. Instalar o NGINX Gateway Fabric (v2.2.1)

[cite\_start]Usando o registro OCI oficial atualizado[cite: 46].

```bash
helm install nginx-gateway oci://ghcr.io/nginx/charts/nginx-gateway-fabric \
  --create-namespace \
  -n nginx-gateway \
  --version 2.2.1
```

### 3\. Criar o Gateway (Infraestrutura)

[cite\_start]O Service LoadBalancer só será criado após este manifesto ser aplicado[cite: 87, 119].

**Arquivo:** `infra-gateway.yaml`

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: gateway-principal
  namespace: default
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: All
```

*Aplique:* `kubectl apply -f infra-gateway.yaml`

### 4\. Aplicação de Teste (Backend)

**Arquivo:** `app-cafe.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cafe
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cafe
  template:
    metadata:
      labels:
        app: cafe
    spec:
      containers:
      - name: nginx
        image: nginxdemos/nginx-hello:plain-text
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: cafe-svc
  namespace: default
spec:
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: cafe
```

*Aplique:* `kubectl apply -f app-cafe.yaml`

### 5\. Criar a Rota (Acesso via IP)

[cite\_start]Não definimos `hostnames` para permitir o acesso direto pelo IP do Load Balancer[cite: 116].

**Arquivo:** `rota-ip-direto.yaml`

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: rota-cafe
  namespace: default
spec:
  parentRefs:
  - name: gateway-principal
  # hostnames removido para permitir qualquer IP/Host
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: cafe-svc
      port: 80
```

*Aplique:* `kubectl apply -f rota-ip-direto.yaml`

-----

### 6\. Verificação

1.  **Obter o IP Público:**
    [cite\_start]O NGINX cria o service no formato `<nome-gateway>-<nome-classe>` no namespace do Gateway[cite: 100, 101].

    ```bash
    kubectl get svc gateway-principal-nginx -n default
    ```

2.  **Testar:**

    ```bash
    curl http://<SEU-IP-PUBLICO>
    ```