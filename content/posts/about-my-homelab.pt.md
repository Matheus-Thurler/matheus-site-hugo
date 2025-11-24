---
title: "Adeus Proxmox? Por que migrei meu Homelab para o Apache CloudStack"
date: 2025-11-24
description: "Descubra os motivos técnicos e de carreira que me levaram a migrar meu Homelab de Proxmox e OpenStack para o Apache CloudStack. Conheça minha topologia física e como ela simula um ambiente real de Datacenter."
cover: /images/placeholder/cloudstack-logo.png
readingTime: "10"
katex: false
mermaid: false
tags: ['homelab', 'cloudstack', 'proxmox', 'openstack', 'virtualização', 'terraform', 'kvm']
categories: ['homelab', 'cloud']
---

{{< youtube BB7wloVn3WE >}}

Você ainda gerencia suas VMs no Proxmox? Se você está buscando evoluir seus estudos de cloud computing e se aproximar mais de ambientes enterprise reais, talvez seja hora de repensar sua stack de virtualização. Neste post, vou compartilhar os motivos que me levaram a migrar meu homelab de Proxmox e OpenStack para o **Apache CloudStack**, e como essa decisão transformou minha experiência de aprendizado.

## Por que não Proxmox?

Não me entenda mal - o **Proxmox** é uma excelente plataforma de virtualização. É gratuito, tem uma interface web intuitiva, gerencia tanto containers LXC quanto VMs KVM, e funciona muito bem para a maioria dos homelabs. Muitos profissionais de TI usam Proxmox com sucesso em seus laboratórios.

### As Limitações do Proxmox para Estudos Avançados

No entanto, quando você começa a se aprofundar em conceitos de **cloud computing** e **infraestrutura como código (IaC)**, algumas limitações aparecem:

1. **API limitada para automação avançada** - Embora o Proxmox tenha uma API, ela é principalmente voltada para operações básicas de CRUD (criar, ler, atualizar, deletar) em VMs e containers.

2. **Não é uma plataforma de cloud real** - O Proxmox é um hypervisor com interface web, não uma plataforma de orquestração de cloud. Conceitos como multi-tenancy, service offerings, e network orchestration não são nativos.

3. **Distância do mundo enterprise** - Pouquíssimas empresas usam Proxmox em produção. Se seu objetivo é aprender tecnologias relevantes para o mercado, você precisa de algo mais próximo do que é usado em datacenters reais.

4. **Automação com Terraform limitada** - Embora exista um provider do Terraform para Proxmox, a experiência não se compara com providers de clouds públicas ou plataformas enterprise de IaaS.

Se você só quer rodar algumas VMs e serviços em casa, Proxmox é perfeito. Mas se você quer **simular um ambiente de cloud real** e aprender tecnologias enterprise, precisa de algo mais robusto.

## E o OpenStack? Por que não?

Depois do Proxmox, muitos entusiastas consideram o **OpenStack** como o próximo passo natural. Afinal, é a plataforma de cloud privada open-source mais popular, usada por grandes empresas e provedores de cloud.

### O Problema: OpenStack pode ser "Overkill"

O OpenStack é fantástico, mas vem com suas próprias complicações:

1. **Complexidade extrema** - O OpenStack é composto por mais de 30 projetos diferentes (Nova, Neutron, Cinder, Glance, Keystone, etc.). Cada um tem suas próprias configurações e quirks.

2. **Requisitos de hardware** - Para rodar o OpenStack adequadamente, você precisa de recursos significativos. Um deployment mínimo já consome muita RAM e CPU.

3. **Curva de aprendizado íngreme** - Antes de começar a usar o OpenStack como plataforma de estudos, você precisa investir semanas (ou meses) só para entender como instalá-lo e configurá-lo corretamente.

4. **Manutenção trabalhosa** - Upgrades, troubleshooting e manutenção do OpenStack podem consumir mais tempo do que você realmente gostaria de gastar em um homelab.

5. **Mercado mais nichado** - Embora o OpenStack seja usado em produção, sua adoção está mais concentrada em telecoms e grandes clouds privadas. Para a maioria dos profissionais, não é a tecnologia que vão encontrar no dia a dia.

Para mim, o OpenStack acabou sendo um peso maior do que o benefício que trazia. Eu queria estudar conceitos de cloud e automação, não passar semanas debugando o Neutron.

## A Decisão: Apache CloudStack

Depois de avaliar as opções, decidi migrar para o **Apache CloudStack**. E essa escolha mudou completamente minha experiência com o homelab.

### Por que CloudStack?

O CloudStack oferece o melhor dos dois mundos:

#### 1. **Plataforma de Cloud Real**

Diferente do Proxmox, o CloudStack é uma **plataforma de orquestração de cloud IaaS** completa, com:

- **Multi-tenancy nativo** - Suporte para múltiplos usuários, domínios e accounts
- **Service Offerings** - Templates de recursos (CPU, RAM, disco) como em clouds públicas
- **Network Orchestration** - VLANs, VPCs, Load Balancers, VPNs, tudo gerenciado pela plataforma
- **Storage Management** - Primary e Secondary Storage, templates, snapshots, volumes
- **Autoscaling e High Availability** - Recursos enterprise nativos

#### 2. **Mais Simples que OpenStack**

O CloudStack tem uma arquitetura muito mais enxuta:

- **Uma única aplicação (Management Server)** ao invés de dezenas de serviços separados
- **Instalação e configuração mais diretas** - Em poucas horas você tem um ambiente funcionando
- **Manutenção mais simples** - Menos componentes = menos pontos de falha
- **Documentação mais coesa** - Tudo em um lugar, não fragmentado em 30 projetos diferentes

#### 3. **Relevância no Mercado**

O CloudStack é usado em produção por diversos provedores de cloud ao redor do mundo:

- **Provedores de cloud** - Como a Leaseweb, ShapeBlue, e outros na Europa, Ásia e América Latina
- **Empresas de telecomunicações** - Várias telecoms usam CloudStack para seus serviços de cloud
- **Empresas que precisam de cloud privada** - Especialmente em setores regulados que não podem usar cloud pública

Conhecer CloudStack pode abrir portas em empresas que operam infraestrutura de cloud privada ou híbrida.

#### 4. **Excelente para Automação e IaC**

O CloudStack tem uma **API extremamente completa e bem documentada**, e o **provider do Terraform para CloudStack** é maduro e bem mantido. Isso significa que posso:

- Provisionar toda minha infraestrutura como código
- Criar e destruir ambientes completos com um comando
- Simular cenários reais de deploy de aplicações cloud-native
- Praticar GitOps e CI/CD para infraestrutura

## Minha Topologia Atual

Aqui está como estruturei meu homelab com CloudStack:

### Infraestrutura Física

![Diagrama da infraestrutura física do meu homelab com CloudStack](/images/placeholder/diagrama-homelab.png)

### Componentes

1. **Management Server**
   - VM/máquina dedicada rodando o CloudStack Management Server
   - Responsável por toda orquestração, API, e interface web
   - MySQL/MariaDB para banco de dados
   - NFS para Secondary Storage (templates, snapshots, ISOs)

2. **KVM Hosts (2 nós)**
   - Servidores físicos ou VMs poderosas rodando KVM
   - Conectados via libvirt ao Management Server
   - Primary Storage local ou compartilhado (NFS/iSCSI)
   - Cada host em uma VLAN de management separada

3. **Switch Gerenciável**
   - Suporte a VLANs (essencial para segregação de rede)
   - VLAN de Management (comunicação CloudStack ↔ Hosts)
   - VLANs de Guest (redes das VMs criadas)
   - VLAN de Public (acesso externo/internet)
   - VLAN de Storage (tráfego NFS/iSCSI, se aplicável)

### Por que essa topologia?

Essa configuração simula um **datacenter real em escala reduzida**:

- **Separação de funções** - Management separado do Compute
- **Alta disponibilidade** - Dois hosts permitem testes de migração de VMs, redundância, etc.
- **Networking enterprise** - VLANs segregando diferentes tipos de tráfego
- **Escalabilidade** - Fácil adicionar mais hosts KVM conforme necessário

Diferente do Proxmox onde você teria VMs gerenciadas individualmente em cada nó, no CloudStack você tem uma **camada de orquestração centralizada** que gerencia todos os recursos como um pool unificado - exatamente como AWS, Azure, ou GCP fazem.

## Benefícios que Experimentei

Desde a migração para CloudStack, tenho aproveitado diversos benefícios:

### 1. **Aprendizado de Conceitos Enterprise**

- **Zones, Pods, Clusters** - Hierarquia de datacenter real
- **Service Offerings** - Como criar "planos" de VMs (igual t2.micro, t2.large da AWS)
- **Network Offerings** - Diferentes topologias de rede (isolada, VPC, shared)
- **Accounts e Domains** - Multi-tenancy real

### 2. **Automação Avançada com Terraform**

Posso provisionar infraestrutura completa via código:

```hcl
resource "cloudstack_instance" "web_server" {
  name             = "web-server-01"
  service_offering = "Medium Instance"
  template         = "Ubuntu 22.04"
  zone             = "lab-zone-1"
  network_id       = cloudstack_network.app_network.id
}

resource "cloudstack_network" "app_network" {
  name             = "app-tier-network"
  cidr             = "10.1.1.0/24"
  network_offering = "DefaultIsolatedNetworkOffering"
  zone             = "lab-zone-1"
}
```

Isso me permite praticar **Infrastructure as Code** de verdade, com uma plataforma que se comporta como clouds públicas.

### 3. **Ambiente de Testes para Certificações**

Se você está estudando para certificações cloud (AWS, Azure, GCP), ter um CloudStack local ajuda a entender conceitos fundamentais de IaaS:

- VPCs e redes isoladas
- Security Groups
- Load Balancers
- Storage (Block Storage, Object Storage)
- Templates e Images

### 4. **Experiência de API Real**

A API do CloudStack é REST, bem documentada, e extremamente completa. Isso significa que posso:

- Integrar com scripts Python/Go/Bash
- Criar ferramentas customizadas
- Simular cenários de automação que encontraria em empresas reais

## Desafios e Como Superei

Claro, nem tudo são flores. Aqui estão alguns desafios que enfrentei:

### 1. **Curva de Aprendizado Inicial**

**Desafio**: Entender a arquitetura do CloudStack (Zone → Pod → Cluster → Host) leva um tempo.

**Solução**: A documentação oficial é excelente. Dediquei alguns dias lendo e fazendo testes em VMs antes de montar o ambiente definitivo.

### 2. **Requisitos de Rede**

**Desafio**: CloudStack exige um switch gerenciável com suporte a VLANs.

**Solução**: Não é obrigatório, mas é recomendado, pois pode ser configurado sem a necessidade de um switch gerenciável. Investi em um switch gerenciável básico (TP-Link TL-SG105E ou similar). Não precisa ser enterprise-grade, apenas suportar VLANs 802.1Q.

### 3. **Storage**

**Desafio**: Configurar NFS para Secondary Storage pode ser confuso no início.

**Solução**: Usei o próprio Management Server como servidor NFS para começar. Depois, irei migrar para um NAS dedicado conforme for escalando ou até mesmo nem usar .

### 4. **Debugging**

**Desafio**: Quando algo dá errado, os logs podem ser extensos.

**Solução**: Aprendi a usar o CloudMonkey (CLI do CloudStack) e a ler os logs em `/var/log/cloudstack/management/`. Com o tempo, ficou mais fácil identificar problemas.

## Próximos Passos

Agora que tenho um ambiente CloudStack funcionando, meus próximos passos são:

1. **Automatizei todo o deployment com Ansible** - Provisionar a instalação do CloudStack
2. **Automatizei todo o deployment com Terraform** - Provisionar a infraestrutura base via código, com Kubernetes
3. **Implementar CI/CD** - Pipeline completo de infra + aplicação

E claro, **no próximo vídeo vou trazer um tutorial passo a passo** de como você pode levantar o CloudStack localmente no seu próprio homelab usando ansible!

## Conclusão: Vale a Pena Migrar?

A migração do Proxmox para o CloudStack foi uma das melhores decisões que tomei para meu homelab. Se você:

- ✅ Quer aprender conceitos de cloud computing de verdade
- ✅ Busca uma plataforma relevante no mercado enterprise
- ✅ Gosta de automação e Infrastructure as Code
- ✅ Quer simular um datacenter real em casa
- ✅ Não quer a complexidade absurda do OpenStack

Então o **Apache CloudStack** pode ser a escolha perfeita para você.

### Comparação Rápida

| Critério | Proxmox | OpenStack | CloudStack |
|----------|---------|-----------|------------|
| **Facilidade de instalação** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Recursos de cloud IaaS** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Complexidade** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Qualidade da API** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Terraform support** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Relevância no mercado** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Requisitos de hardware** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Documentação** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### Para quem é cada plataforma?

- **Proxmox**: Ideal para quem quer um hypervisor simples e eficiente para rodar VMs e containers sem complicação
- **OpenStack**: Para quem quer estudar a plataforma específica (trabalha com OpenStack ou pretende trabalhar) e tem hardware robusto
- **CloudStack**: Para quem quer aprender cloud computing enterprise, automação, e IaC sem a complexidade do OpenStack

## Recursos e Links Úteis

- **[Documentação Oficial do Apache CloudStack](http://docs.cloudstack.apache.org/)**
- **[CloudStack GitHub](https://github.com/apache/cloudstack)**
- **[Terraform Provider para CloudStack](https://registry.terraform.io/providers/cloudstack/cloudstack/latest/docs)**
- **[CloudMonkey CLI](https://github.com/apache/cloudstack-cloudmonkey)**
- **[Comunidade CloudStack](https://cloudstack.apache.org/community.html)**

---

**Fique ligado no próximo post/vídeo onde vou mostrar o tutorial completo de instalação do CloudStack passo a passo!**

Já usou CloudStack? Tem dúvidas sobre a migração? Deixa nos comentários!


