---
title: "NGINX Ingress Controller Morreu? Conheça o NGINX Gateway Fabric"
date: 2025-12-06
slug: nginx-gateway-api-kubernetes
description: "O NGINX Ingress Controller foi descontinuado, mas o NGINX não morreu! Descubra o NGINX Gateway Fabric, como ele implementa a Gateway API do Kubernetes, e por que essa mudança é uma evolução natural que separa melhor infra de dev."
cover: /images/covers/nginx-gateway-api.webp
readingTime: "8"
katex: false
mermaid: false
tags: ['kubernetes', 'nginx', 'gateway-api', 'ingress', 'devops', 'networking']
categories: ['kubernetes', 'networking']
---

{{< youtube GbNccjPmavI >}}

Se você trabalha com Kubernetes, provavelmente já usou ou pelo menos ouviu falar do **NGINX Ingress Controller**. Por muito tempo, ele foi a escolha padrão para expor aplicações ao mundo externo. Mas recentemente, a F5 (dona do NGINX) anunciou a **descontinuação** do projeto.

Calma, não entre em pânico! **O NGINX não morreu** — ele evoluiu. E neste post vou te mostrar o que é o **NGINX Gateway Fabric**, como funciona a **Gateway API**, e por que essa mudança é na verdade uma **grande evolução** para quem trabalha com Kubernetes.

## O Que Aconteceu com o NGINX Ingress Controller?

O NGINX Ingress Controller foi descontinuado em favor de uma nova implementação: o **NGINX Gateway Fabric**. Mas por que essa mudança?

### O Problema do Ingress Tradicional

O modelo de **Ingress** do Kubernetes, embora funcional, sempre teve algumas limitações:

1. **Tudo em um único recurso** — O Ingress mistura configurações de infraestrutura com configurações de aplicação
2. **Annotation Hell** — Funcionalidades avançadas como SSL redirect, timeouts, rate limiting dependiam de annotations específicas de cada controller
3. **Não é portável** — Um Ingress configurado para NGINX não funciona igual no Traefik ou HAProxy
4. **Difícil separação de responsabilidades** — Quem configura o Ingress? O time de infra ou o dev?

Veja um exemplo clássico de Ingress que ilustra esses problemas:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: meu-ingress-confuso
  annotations:
    # --- ISTO É INFRAESTRUTURA (Annotation Hell) ---
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
    aws-load-balancer-backend-protocol: "http"
    aws-load-balancer-ssl-ports: "443"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    # -----------------------------------------------
spec:
  rules:
  # --- ISTO É RESPONSABILIDADE DO DESENVOLVEDOR ---
  - host: minhabloja.com
    http:
      paths:
      - path: /api/v1/pagamentos
        pathType: Prefix
        backend:
          service:
            name: servico-pagamentos
            port:
              number: 8080
  # ------------------------------------------------
```

Percebe o problema? **Configurações de infraestrutura e de aplicação estão misturadas no mesmo arquivo**. Quem deveria gerenciar esse YAML? O SRE que entende de SSL e timeouts, ou o desenvolvedor que conhece sua aplicação?

## A Solução: Gateway API

A **Gateway API** é a evolução natural do Ingress. É uma especificação oficial do Kubernetes (sig-network) que resolve esses problemas através de uma **separação clara de responsabilidades**.

![Comparação entre Ingress e Gateway API](/images/posts/ingress-vs-gateway-comparison.webp)

### A Arquitetura da Gateway API

A Gateway API divide as configurações em **três camadas**:

| Recurso | Responsável | O que configura |
|---------|-------------|-----------------|
| **GatewayClass** | Provedor (NGINX, Traefik, etc) | Implementação do controller |
| **Gateway** | Time de Infraestrutura/Platform | Listeners, portas, TLS, IP |
| **HTTPRoute** | Time de Desenvolvimento | Rotas, hosts, paths, backends |

Essa separação permite que:

- ✅ **Infra** gerencia o Gateway (certificados, IPs públicos, políticas de segurança)
- ✅ **Devs** gerenciam apenas suas rotas (sem tocar em configs de infra)
- ✅ **Cada um no seu quadrado**, sem conflitos

## Instalando o NGINX Gateway Fabric

Antes de começarmos com os exemplos práticos, precisamos instalar o NGINX Gateway Fabric no cluster. A instalação é feita em duas etapas:

### 1. Instalando os CRDs da Gateway API

Primeiro, precisamos ensinar ao Kubernetes o que é um Gateway, HTTPRoute, e os outros recursos da Gateway API. Fazemos isso instalando os CRDs (Custom Resource Definitions):

```bash
kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.2.1" | kubectl apply -f -
```

Esse comando baixa e aplica os CRDs diretamente do repositório oficial do NGINX Gateway Fabric. Com isso, o cluster passa a entender os novos tipos de recursos.

### 2. Instalando o NGINX Gateway Fabric

Agora instalamos o controller em si. Você pode fazer isso via Helm:

```bash
# Adicionar o repo
helm repo add nginx-gateway https://nginx.github.io/nginx-gateway-fabric

# Instalar
helm install ngf nginx-gateway/nginx-gateway-fabric \
  --namespace nginx-gateway \
  --create-namespace
```

Ou via manifests:

```bash
kubectl apply -f https://github.com/nginxinc/nginx-gateway-fabric/releases/latest/download/nginx-gateway.yaml
```

Após a instalação, verifique se o controller está rodando:

```bash
kubectl get pods -n nginx-gateway
```

Agora sim, estamos prontos para criar nossos Gateways e Rotas!

### Entendendo o LoadBalancer: Gateway vs Ingress

Uma diferença importante que você vai notar: **quando você aplica um Gateway, ele cria automaticamente um LoadBalancer com um IP dedicado**.

| Aspecto | Ingress Controller | Gateway API |
|---------|-------------------|-------------|
| **LoadBalancer** | Um só para todo o cluster | Um por Gateway (pode ter vários) |
| **IP** | Compartilhado entre todas as apps | Dedicado por Gateway |
| **Isolamento** | Todas as apps no mesmo ponto de entrada | Cada Gateway pode ter seu próprio IP |

**Na prática, nas clouds:**

- **AWS**: O Gateway cria um **Network Load Balancer (NLB)** ou **Application Load Balancer (ALB)** para cada Gateway
- **GCP**: Cria um **Google Cloud Load Balancer** dedicado
- **Azure**: Cria um **Azure Load Balancer** para cada Gateway
- **Apache CloudStack**: No meu homelab, o CloudStack provisiona um **IP público dedicado** para cada Gateway automaticamente
- **On-premise/Bare-metal**: Você pode usar **MetalLB** para atribuir IPs aos Gateways

Isso significa que você pode ter:
- Um Gateway para aplicações **públicas** (com IP externo)
- Outro Gateway para APIs **internas** (com IP privado)
- Um Gateway por **cliente/tenant** em cenários multi-tenant

Com Ingress tradicional, tudo passa pelo mesmo IP — com Gateway API, você tem **flexibilidade total**.

## Exemplo Prático: Migrando de Ingress para Gateway API

Vamos ver na prática como fica mais simples e organizado com a Gateway API.

### 1. Gateway (Gerenciado pelo Time de Infra)

O Gateway define a "porta de entrada" do cluster. É aqui que o time de plataforma configura portas, protocolos, e quais namespaces podem criar rotas:

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

Note o `allowedRoutes.namespaces.from: All` — isso permite que **qualquer namespace** crie rotas apontando para esse Gateway. Você também pode restringir para namespaces específicos, dando controle granular sobre quem pode expor serviços.

### 2. HTTPRoute (Gerenciado pelo Time de Dev)

O desenvolvedor só precisa se preocupar com **sua rota e seu serviço**:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: rota-cafe
  namespace: default
spec:
  parentRefs:
  - name: gateway-principal
  hostnames:
  - "cafe.homelab.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: cafe-svc
      port: 80
```

**É isso!** Nada de annotations, nada de configurações de SSL ou timeouts. O dev apenas declara: "Quero que `cafe.homelab.com` aponte para meu serviço `cafe-svc`".

### 3. Aplicação Completa

Completando o exemplo, aqui está o Deployment e Service:

```yaml
# deployment.yml
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
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
# service.yml
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

## Multi-Tenancy: Múltiplas Aplicações, Um Gateway

Uma das grandes vantagens da Gateway API é o suporte nativo a **multi-tenancy**. Você pode ter um único Gateway servindo múltiplas aplicações de times diferentes.

### Exemplo: Adicionando um Serviço de Pagamentos

Imagine que outro time quer expor a API de pagamentos no mesmo cluster:

```yaml
# deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pagamentos-svc
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pagamentos-svc
  template:
    metadata:
      labels:
        app: pagamentos-svc
    spec:
      containers:
      - name: nginx
        image: nginxdemos/nginx-hello:plain-text
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
# service.yml
apiVersion: v1
kind: Service
metadata:
  name: pagamentos-svc
  namespace: default
spec:
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: pagamentos-svc
```

E a rota:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: rota-api
  namespace: default
spec:
  parentRefs:
  - name: gateway-principal
  hostnames:
  - "api.homelab.com"  # Outro domínio!
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: pagamentos-svc  # Outro serviço!
      port: 80
```

**Pronto!** Agora temos:

- `cafe.homelab.com` → Serviço Café
- `api.homelab.com` → Serviço Pagamentos

Cada time gerencia apenas sua própria HTTPRoute, e o time de plataforma gerencia o Gateway central. **Zero conflitos, zero annotations duplicadas**.

## Testando as Rotas

Para testar, basta fazer requisições com o header `Host` correto:

```bash
# Obtendo o IP do Gateway
export IP_VIP=$(kubectl get gateway gateway-principal -o jsonpath='{.status.addresses[0].value}')

# Testando o serviço Café
curl -v -H "Host: cafe.homelab.com" http://$IP_VIP

# Testando o serviço de API/Pagamentos
curl -v -H "Host: api.homelab.com" http://$IP_VIP

# Testando um host não configurado (deve retornar 404)
curl -v -H "Host: errado.com" http://$IP_VIP
```

## Por que Migrar para Gateway API?

### ✅ Benefícios Claros

| Aspecto | Ingress | Gateway API |
|---------|---------|-------------|
| **Separação de responsabilidades** | ❌ Tudo junto | ✅ Gateway vs HTTPRoute |
| **Portabilidade** | ❌ Annotations específicas | ✅ API padronizada |
| **Multi-tenancy** | ❌ Complexo | ✅ Nativo |
| **Evolução/Extensibilidade** | ❌ Limitado | ✅ Novos recursos (GRPCRoute, TCPRoute, etc) |
| **Suporte da comunidade** | ⚠️ Estável mas estagnado | ✅ Ativamente desenvolvido |

### O NGINX Gateway Fabric

O **NGINX Gateway Fabric** é a implementação da F5/NGINX da Gateway API. Ele substitui o antigo Ingress Controller e traz:

- Implementação completa da Gateway API v1
- Performance do NGINX que você já conhece
- Suporte a HTTPRoute, GRPCRoute, e mais
- Transição suave para quem já usa NGINX

## Conclusão

O NGINX Ingress Controller pode ter sido descontinuado, mas o NGINX está **mais vivo do que nunca** com o Gateway Fabric. A migração para a Gateway API não é apenas uma atualização — é uma **evolução arquitetural** que traz:

- 🎯 **Separação clara** entre infra e dev
- 🔄 **Portabilidade** entre diferentes controllers
- 🏢 **Multi-tenancy** nativo e seguro
- 🚀 **Futuro garantido** com suporte ativo da comunidade Kubernetes

Se você ainda está usando Ingress, agora é o momento perfeito para começar a planejar sua migração. A Gateway API veio para ficar, e quanto antes você adotar, mais preparado estará para o futuro do Kubernetes.

---

**Tem dúvidas sobre a migração ou quer ver mais exemplos?** Deixa nos comentários!

