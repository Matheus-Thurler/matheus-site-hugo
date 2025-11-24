---
title: "GitHub Actions Matrix Strategy: Testando Múltiplas Versões Simultaneamente"
date: 2025-11-22
description: "Aprenda a usar Matrix Strategy no GitHub Actions para testar seu código em múltiplas versões de linguagens, sistemas operacionais e dependências ao mesmo tempo, economizando tempo e garantindo compatibilidade."
cover: /images/placeholder/github-actions-matrix.png
readingTime: "12"
katex: false
mermaid: false
tags: ['github-actions', 'ci-cd', 'testing', 'devops', 'automation']
categories: ['devops', 'ci-cd']
---

Testar seu código em apenas uma versão de Node.js, Python ou Ruby é arriscado. E se seu código quebrar no Python 3.9 mas funcionar no 3.12? E se houver bugs específicos do Windows que você não detecta no Linux? **Matrix Strategy** do GitHub Actions resolve isso de forma elegante.

## O Problema: Compatibilidade Multi-Versão

Imagine este cenário comum:

```yaml
# Workflow simples
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm test
```

**Problemas:**
- ❌ Só testa em Node.js 20
- ❌ Só testa em Ubuntu
- ❌ Usuários com Node 16 ou 18 podem ter problemas
- ❌ Bugs específicos do Windows ou macOS passam despercebidos

Para testar em 3 versões do Node × 3 SOs = 9 combinações, você precisaria de 9 jobs separados. Muito código duplicado!

## A Solução: Matrix Strategy

Matrix Strategy permite definir múltiplas dimensões de teste em um único job:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [16, 18, 20]
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

**Resultado:** 9 jobs executados em paralelo automaticamente! 🚀

## Como Funciona a Matrix

### Sintaxe Básica

```yaml
strategy:
  matrix:
    # Cada chave define uma dimensão
    language: [node, python, go]
    version: [latest, stable]
```

GitHub Actions cria **produto cartesiano** de todas as combinações:
- language: node, version: latest
- language: node, version: stable
- language: python, version: latest
- language: python, version: stable
- language: go, version: latest
- language: go, version: stable

**Total:** 3 × 2 = **6 jobs**

### Acessando Valores da Matrix

Use `${{ matrix.variavel }}` para acessar o valor atual:

```yaml
steps:
  - name: Print current combination
    run: |
      echo "Testing ${{ matrix.language }} version ${{ matrix.version }}"
```

## Exemplos Práticos

### 1. Teste Multi-Versão Node.js

```yaml
name: Node.js CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x, 21.x]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run lint
        run: npm run lint
```

**Resultado:** Testa em Node 16, 18, 20 e 21 simultaneamente.

### 2. Teste Cross-Platform

```yaml
name: Cross-Platform Tests

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
```

**Resultado:** 3 SOs × 4 versões Python = **12 jobs em paralelo**

### 3. Matrix com Múltiplas Dimensões

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node-version: [18, 20]
    database: [postgres, mysql, sqlite]
    include:
      # Adiciona combinação específica
      - os: macos-latest
        node-version: 20
        database: postgres

steps:
  - name: Start database
    run: |
      echo "Starting ${{ matrix.database }} on ${{ matrix.os }}"
```

**Resultado:** (2 × 2 × 3) + 1 = **13 jobs**

## Recursos Avançados

### 1. Include - Adicionar Combinações Específicas

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    node-version: [18, 20]
    include:
      # Testa Node 16 apenas no Ubuntu
      - os: ubuntu-latest
        node-version: 16
      
      # Testa Node 20 no macOS também
      - os: macos-latest
        node-version: 20
        
      # Adiciona variáveis extras para combinação específica
      - os: ubuntu-latest
        node-version: 20
        experimental: true
```

### 2. Exclude - Remover Combinações Indesejadas

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16, 18, 20]
    exclude:
      # Node 16 não suportado no Windows
      - os: windows-latest
        node-version: 16
      
      # Economizar runners - pular macOS para Node 18
      - os: macos-latest
        node-version: 18
```

**Resultado:** (3 × 3) - 2 = **7 jobs** ao invés de 9

### 3. Fail-Fast (Padrão: true)

```yaml
strategy:
  fail-fast: false  # Continua outros jobs mesmo se um falhar
  matrix:
    version: [1, 2, 3, 4, 5]
```

**fail-fast: true** (padrão): Cancela todos os jobs se um falhar  
**fail-fast: false**: Roda todos independentemente

### 4. Max-Parallel - Limitar Execuções Simultâneas

```yaml
strategy:
  max-parallel: 3  # Apenas 3 jobs por vez
  matrix:
    version: [1, 2, 3, 4, 5, 6, 7, 8]
```

Útil para:
- Economizar minutos de CI
- Evitar rate limiting de APIs externas
- Limitar uso de recursos

## Casos de Uso Reais

### 1. Biblioteca NPM Multi-Versão

```yaml
name: NPM Package CI

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        node-version: [16, 18, 20, 22]
        os: [ubuntu-latest, windows-latest, macos-latest]
        exclude:
          # Node 22 ainda experimental
          - os: windows-latest
            node-version: 22
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      
      - run: npm ci
      - run: npm test
      - run: npm run build
      
      - name: Test installation
        run: |
          npm pack
          npm install -g *.tgz
```

### 2. Aplicação com Múltiplos Bancos

```yaml
strategy:
  matrix:
    database:
      - type: postgres
        version: '14'
        port: 5432
      - type: postgres
        version: '15'
        port: 5432
      - type: mysql
        version: '8.0'
        port: 3306
      - type: mariadb
        version: '10.11'
        port: 3306

steps:
  - name: Start ${{ matrix.database.type }}
    run: |
      docker run -d \
        -p ${{ matrix.database.port }}:${{ matrix.database.port }} \
        ${{ matrix.database.type }}:${{ matrix.database.version }}
  
  - name: Run migrations
    env:
      DATABASE_URL: ${{ matrix.database.type }}://localhost:${{ matrix.database.port }}/test
    run: npm run migrate
  
  - name: Run tests
    run: npm test
```

### 3. Build Multi-Arquitetura

```yaml
strategy:
  matrix:
    include:
      - arch: amd64
        os: ubuntu-latest
      - arch: arm64
        os: ubuntu-latest
      - arch: armv7
        os: ubuntu-latest

steps:
  - uses: actions/checkout@v4
  
  - name: Set up QEMU
    uses: docker/setup-qemu-action@v3
  
  - name: Build for ${{ matrix.arch }}
    run: |
      docker buildx build \
        --platform linux/${{ matrix.arch }} \
        -t myapp:${{ matrix.arch }} \
        .
```

## Naming e Identificação

### Nome Dinâmico do Job

```yaml
jobs:
  test:
    name: Test on ${{ matrix.os }} with Node ${{ matrix.node-version }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node-version: [18, 20]
    runs-on: ${{ matrix.os }}
```

**Resultado na UI:**
- Test on ubuntu-latest with Node 18
- Test on ubuntu-latest with Node 20
- Test on windows-latest with Node 18
- Test on windows-latest with Node 20

## Matrix com Outputs

Você pode usar outputs de uma matrix em jobs subsequentes:

```yaml
jobs:
  build:
    strategy:
      matrix:
        version: [v1, v2, v3]
    outputs:
      # Não funciona diretamente - precisa workaround
      artifact-name: myapp-${{ matrix.version }}
    steps:
      - run: echo "Building ${{ matrix.version }}"
  
  # Alternativa: usar artefatos nomeados
  deploy:
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: myapp-*
```

## Performance e Custos

### Minutos de Consumo

Exemplo: Matrix com 12 combinações, cada uma rodando 5 minutos.

**fail-fast: true** (se nenhum falhar): 5 minutos × 12 = **60 minutos** de runner  
**fail-fast: true** (se um falhar em 2min): ~2-5 minutos (cancela os outros)  
**fail-fast: false**: Sempre 60 minutos

### Otimizações

1. **Use cache agressivamente:**

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ matrix.node-version }}-${{ hashFiles('**/package-lock.json') }}
```

2. **Priorize combinações importantes:**

```yaml
include:
  - os: ubuntu-latest
    node-version: 20
    priority: high  # Rode isso primeiro
```

3. **Use max-parallel para controlar custo:**

```yaml
strategy:
  max-parallel: 2  # Máximo 2 jobs por vez em contas free
```

## Debugging Matrix

### Ver Todas as Combinações

```yaml
jobs:
  debug:
    strategy:
      matrix:
        os: [ubuntu, windows, macos]
        version: [1, 2, 3]
    steps:
      - name: Print matrix
        run: |
          echo "OS: ${{ matrix.os }}"
          echo "Version: ${{ matrix.version }}"
          echo "Runner: ${{ runner.os }}"
```

### Testar Uma Combinação

Use `workflow_dispatch` com inputs:

```yaml
on:
  workflow_dispatch:
    inputs:
      os:
        type: choice
        options: [ubuntu-latest, windows-latest, macos-latest]
      node-version:
        type: choice
        options: [16, 18, 20]

jobs:
  test:
    runs-on: ${{ inputs.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
```

## Best Practices

1. ✅ **Sempre teste versões LTS + latest**
2. ✅ **Use fail-fast: false em PRs para ver todos os problemas**
3. ✅ **Documente quais combinações são obrigatórias**
4. ✅ **Use exclude para economizar em combinações não importantes**
5. ✅ **Nomeie jobs descritivamente**
6. ❌ **Evite matrices muito grandes (>20 combinações)**
7. ❌ **Não duplique lógica - use matrix**

## Conclusão

Matrix Strategy transforma:

```yaml
# De 100+ linhas de código duplicado
test-node-16-ubuntu: ...
test-node-18-ubuntu: ...
test-node-20-ubuntu: ...
test-node-16-windows: ...
# ... etc
```

Para:

```yaml
# 20 linhas elegantes
strategy:
  matrix:
    os: [ubuntu, windows, macos]
    node: [16, 18, 20]
```

Benefícios:
- ⏱️ **Economia de tempo** - testes em paralelo
- 🎯 **Mais cobertura** - múltiplas combinações facilmente
- 🔧 **Manutenção simples** - um lugar para atualizar
- 💰 **Controle de custos** - max-parallel e exclude

---

**Já usa Matrix Strategy? Compartilhe nos comentários quantas combinações você testa!**

#GitHubActions #CI #Testing #DevOps
