---
title: "DOMINE Reusable Workflows e Diga ADEUS ao Copia e Cola no seu CI/CD!"
date: 2025-06-24
slug: reusable-workflows-github-actions
description: "Aprenda a usar Reusable Workflows no GitHub Actions para eliminar duplicação de código, centralizar a manutenção e escalar seus pipelines de CI/CD de forma profissional."
cover: /images/covers/github-reusable-workflows.png
readingTime: "12"
katex: false
mermaid: false
tags: ['github-actions', 'ci-cd', 'devops', 'automation', 'best-practices', 'reusable-workflows']
categories: ['devops', 'ci-cd']
---

{{< youtube E-EvR4fykIc >}}

Se você trabalha com CI/CD no GitHub Actions, provavelmente já se pegou copiando e colando o mesmo código YAML entre diferentes workflows. E se eu te dissesse que existe uma forma muito mais elegante e profissional de fazer isso? Neste post, vou te mostrar como **Reusable Workflows** podem revolucionar seu pipeline de CI/CD.

## O Problema: Copy-Paste Hell

Imagine esta situação familiar:

Você tem 10 repositórios, cada um com seu próprio workflow de CI/CD. Todos eles fazem basicamente a mesma coisa:
- Build da aplicação
- Execução de testes
- Análise de código estático
- Deploy para staging/production

Agora você precisa atualizar a versão do Node.js usada em todos os workflows. O que acontece?

```yaml
# repo-1/.github/workflows/ci.yml
- uses: actions/setup-node@v3
  with:
    node-version: '16'  # Precisa mudar para '18'
    
# repo-2/.github/workflows/ci.yml
- uses: actions/setup-node@v3
  with:
    node-version: '16'  # Precisa mudar aqui também
    
# repo-3/.github/workflows/ci.yml
- uses: actions/setup-node@v3
  with:
    node-version: '16'  # E aqui...
    
# ... mais 7 repositórios para atualizar manualmente
```

Você acaba tendo que:
1. Abrir 10 pull requests diferentes
2. Atualizar manualmente cada arquivo
3. Esperar que ninguém cometa erros no processo
4. Lidar com inconsistências entre os repositórios

Isso não é produtivo, não é escalável, e definitivamente não é enterprise-grade.

## A Solução: Reusable Workflows

**Reusable Workflows** são a resposta do GitHub Actions para o princípio DRY (Don't Repeat Yourself) em CI/CD. Eles permitem que você:

- ✅ **Centralize a lógica comum** em um único lugar
- ✅ **Reutilize workflows** entre múltiplos repositórios
- ✅ **Faça mudanças uma única vez** que se propagam para todos os usuários
- ✅ **Garanta consistência** entre todos os seus projetos
- ✅ **Simplifique a manutenção** drasticamente

## Como Funcionam os Reusable Workflows

### Estrutura Básica

Um Reusable Workflow é simplesmente um workflow normal do GitHub Actions com um gatilho especial: `workflow_call`.

```yaml
# .github/workflows/reusable-build.yml
name: Reusable Build Workflow

on:
  workflow_call:
    inputs:
      node-version:
        description: 'Node.js version to use'
        required: false
        default: '18'
        type: string
    secrets:
      DEPLOY_TOKEN:
        description: 'Token for deployment'
        required: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
```

### Usando o Reusable Workflow

Agora, em qualquer repositório, você pode simplesmente chamar este workflow:

```yaml
# outro-repo/.github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    uses: minha-org/workflows/.github/workflows/reusable-build.yml@main
    with:
      node-version: '18'
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

Pronto! Apenas 3 linhas e você tem todo o pipeline funcionando.

## Recursos Avançados dos Reusable Workflows

### 1. **Inputs Tipados**

Os Reusable Workflows suportam diferentes tipos de inputs:

```yaml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
      
      enable-cache:
        type: boolean
        default: true
      
      max-parallel-jobs:
        type: number
        default: 4
```

Isso garante type-safety e validação automática dos parâmetros.

### 2. **Outputs**

Workflows reutilizáveis podem retornar valores para quem os chamou:

```yaml
on:
  workflow_call:
    outputs:
      build-version:
        description: "Version of the built artifact"
        value: ${{ jobs.build.outputs.version }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.get-version.outputs.version }}
    steps:
      - id: get-version
        run: echo "version=$(cat package.json | jq -r .version)" >> $GITHUB_OUTPUT
```

Depois você pode usar esse output:

```yaml
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy version ${{ needs.build.outputs.build-version }}
        run: echo "Deploying ${{ needs.build.outputs.build-version }}"
```

### 3. **Secrets Management**

Secrets podem ser passados de forma segura:

```yaml
jobs:
  production-deploy:
    uses: ./.github/workflows/deploy.yml
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

Ou, se você quiser passar todos os secrets automaticamente:

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit  # Passa todos os secrets do caller
```

## Padrões e Best Practices

### 1. **Versionamento de Workflows**

Sempre use tags ou branches específicas ao chamar workflows reutilizáveis:

```yaml
# ✅ Bom - usa uma tag específica
uses: minha-org/workflows/.github/workflows/ci.yml@v1.2.0

# ✅ Bom - usa um branch específico
uses: minha-org/workflows/.github/workflows/ci.yml@main

# ❌ Evite - SHA específico é difícil de gerenciar
uses: minha-org/workflows/.github/workflows/ci.yml@a1b2c3d4
```

### 2. **Repositório Centralizado**

Crie um repositório dedicado para seus workflows reutilizáveis:

```
minha-org/github-workflows/
├── .github/
│   └── workflows/
│       ├── build-node.yml
│       ├── build-python.yml
│       ├── build-go.yml
│       ├── deploy-aws.yml
│       ├── deploy-gcp.yml
│       └── security-scan.yml
└── README.md
```

### 3. **Documentação Clara**

Documente cada workflow reutilizável:

```yaml
name: Node.js Build Workflow

# Descrição: Pipeline completo para aplicações Node.js
# 
# Inputs:
#   - node-version: Versão do Node.js (padrão: '18')
#   - run-tests: Executar testes (padrão: true)
#   - run-lint: Executar linter (padrão: true)
#
# Secrets necessários:
#   - NPM_TOKEN: Token para registry privado (opcional)
#
# Outputs:
#   - artifact-name: Nome do artefato gerado
#   - test-results: Status dos testes

on:
  workflow_call:
    # ...
```

### 4. **Granularidade Apropriada**

Crie workflows com responsabilidades bem definidas:

```yaml
# ✅ Bom - workflows específicos
- build-and-test.yml
- security-scan.yml
- deploy-to-aws.yml

# ❌ Evite - workflow monolítico
- do-everything.yml
```

## Casos de Uso Reais

### 1. **Pipeline Multirepo Consistente**

```yaml
# Template para todos os microsserviços
jobs:
  ci:
    uses: company/workflows/.github/workflows/microservice-ci.yml@v2
    with:
      language: 'node'
      test-framework: 'jest'
    secrets: inherit
```

Todos os 50 microsserviços usam o mesmo pipeline. Uma atualização -> 50 repos atualizados.

### 2. **Ambientes de Deploy Padronizados**

```yaml
jobs:
  deploy-staging:
    uses: company/workflows/.github/workflows/deploy-k8s.yml@v1
    with:
      environment: 'staging'
      namespace: 'my-app-staging'
    secrets: inherit
    
  deploy-production:
    needs: deploy-staging
    uses: company/workflows/.github/workflows/deploy-k8s.yml@v1
    with:
      environment: 'production'
      namespace: 'my-app-prod'
    secrets: inherit
```

### 3. **Security Scanning Centralizado**

```yaml
jobs:
  security:
    uses: security-team/workflows/.github/workflows/security-scan.yml@main
    with:
      scan-type: 'full'
      fail-on: 'high'
```

O time de segurança mantém o workflow. Todos os times se beneficiam das atualizações.

## Comparação: Antes vs Depois

### Antes (sem Reusable Workflows)

```yaml
# 150 linhas de YAML duplicado em cada repo
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      # ... mais 30 linhas
  
  build:
    runs-on: ubuntu-latest
    # ... mais 40 linhas
    
  security:
    # ... mais 30 linhas
    
  deploy:
    # ... mais 50 linhas
```

**Problemas:**
- 150 linhas × 20 repos = 3000 linhas de código duplicado
- Mudança simples requer 20 PRs
- Inconsistências entre repos
- Difícil manter padrões

### Depois (com Reusable Workflows)

```yaml
# 10 linhas em cada repo
name: CI
on: [push]

jobs:
  pipeline:
    uses: company/workflows/.github/workflows/standard-pipeline.yml@v2
    with:
      app-name: 'my-app'
      environment: 'production'
    secrets: inherit
```

**Benefícios:**
- 10 linhas × 20 repos = 200 linhas total
- Uma mudança -> todos os repos atualizados instantaneamente
- Consistência garantida
- Fácil manutenção e evolução

## Matriz de Workflows Combinados

Você pode criar workflows compostos chamando múltiplos workflows reutilizáveis:

```yaml
jobs:
  lint:
    uses: ./.github/workflows/lint.yml
    
  test:
    uses: ./.github/workflows/test.yml
    needs: lint
    
  build:
    uses: ./.github/workflows/build.yml
    needs: test
    
  security-scan:
    uses: ./.github/workflows/security.yml
    needs: build
    
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    needs: [build, security-scan]
    with:
      environment: 'staging'
    
  integration-tests:
    uses: ./.github/workflows/integration-tests.yml
    needs: deploy-staging
    
  deploy-production:
    uses: ./.github/workflows/deploy.yml
    needs: integration-tests
    with:
      environment: 'production'
```

Cada step é um workflow reutilizável independente, permitindo composição flexível.

## Monitoramento e Observabilidade

Reusable Workflows aparecem como jobs expandidos na UI do GitHub Actions, permitindo:

- Ver exatamente qual versão do workflow foi executada
- Rastrear de onde o workflow foi chamado
- Debugar com clareza a origem dos problemas
- Ter visibilidade completa da execução

## Limitações e Considerações

### Limitações Atuais

1. **Depth Limit**: Workflows reutilizáveis podem chamar outros workflows reutilizáveis, mas apenas até 4 níveis de profundidade.

2. **Environment Variables**: Variáveis de ambiente não são automaticamente propagadas (use inputs explícitos).

3. **Contextos Limitados**: Alguns contextos como `github.token` podem se comportar diferente em workflows reutilizáveis.

### Workarounds

Para variáveis de ambiente:
```yaml
# Caller workflow
env:
  GLOBAL_VAR: 'value'

jobs:
  call-workflow:
    uses: ./.github/workflows/reusable.yml
    with:
      env-var: ${{ env.GLOBAL_VAR }}  # Passe explicitamente
```

## Conclusão: Eleve seu CI/CD ao Próximo Nível

Reusable Workflows são uma das funcionalidades mais poderosas do GitHub Actions, mas ainda são subutilizadas. Ao adotá-los, você:

- **Reduz drasticamente** código duplicado
- **Acelera** o tempo de implementação de mudanças
- **Garante consistência** entre todos os projetos
- **Facilita a manutenção** de pipelines complexos
- **Escala** para centenas de repositórios sem overhead

### Checklist de Migração

- [ ] Identifique padrões comuns em seus workflows atuais
- [ ] Crie um repositório centralizado para workflows reutilizáveis
- [ ] Comece com um workflow simples (ex: linting)
- [ ] Migre gradualmente workflows mais complexos
- [ ] Estabeleça versionamento e documentação
- [ ] Treine o time nos novos padrões
- [ ] Monitore e ajuste conforme necessário

### Próximos Passos

No próximo post/vídeo, vou mostrar:
- Como criar uma **biblioteca completa** de workflows reutilizáveis
- **Templates prontos** para diferentes tecnologias (Node.js, Python, Go, Docker)
- **Estratégias de versionamento** para workflows
- **Testes automatizados** para workflows (sim, é possível!)

## Recursos Úteis

- **[GitHub Actions Reusable Workflows Docs](https://docs.github.com/en/actions/using-workflows/reusing-workflows)**
- **[Awesome GitHub Actions](https://github.com/sdras/awesome-actions)**
- **[GitHub Actions Toolkit](https://github.com/actions/toolkit)**

---

**Já usa Reusable Workflows? Compartilha nos comentários como você os utiliza! Tem dúvidas sobre implementação? Deixa sua pergunta abaixo!**

#GitHubActions #CICD #DevOps #Automation #BestPractices
