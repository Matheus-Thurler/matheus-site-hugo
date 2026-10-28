---
title: "Política de Privacidade — Trilha Ops"
date: 2026-09-25
layout: "page"
url: /trilha-ops/privacy/
comments_disabled: true
description: "Política de privacidade do aplicativo Trilha Ops (Android): dados coletados, compartilhamento, retenção e exclusão de conta."
---

**Última atualização:** 28 de outubro de 2026  
**Idioma:** português (Brasil)

Esta política descreve, de forma honesta, quais dados o aplicativo **Trilha Ops** (pacote `br.com.matheusthurler.trilha_ops`) trata. O app é um produto educacional de estudo DevOps no celular.

## Quem somos

Trilha Ops é mantido por Thurler IT / Matheus Thurler. Contato de suporte: **contato@matheusthurler.com.br**.

## Quais dados coletamos

### Conta Google (Firebase Authentication)

Ao tocar em “Continuar com Google”, o Firebase Authentication recebe o login da sua conta Google. Guardamos no Firebase (e espelhamos em Firestore) identificadores necessários para a sessão:

- UID da conta no Firebase
- e-mail
- nome de exibição (quando a Google fornece)
- URL da foto de perfil (quando a Google fornece)

Esses dados existem para **identificar você** no app. **O progresso de estudo (módulos concluídos, notas de quiz e sequência/streak) fica neste aparelho** (armazenamento local) e **ainda não é sincronizado na nuvem**.

### Perfil no Firestore

Criamos/atualizamos o documento `users/{uid}` com os campos de perfil acima e timestamps de criação / último login.

### No aparelho (local)

- Progresso de módulos e melhores scores de quiz
- Sequência diária (streak)
- Preferências (ex.: animações de acerto, nome de exibição local)
- Cache de conteúdo de estudo (trilhas/módulos)

### Anúncios (Google AdMob)

O app exibe anúncios de banner do **Google AdMob**. Para exibi-los e medir resultados, o AdMob pode usar o **ID de publicidade** do aparelho e coletar **localização aproximada**, dados de **diagnóstico** (ex.: falhas) e de **interação** com os anúncios. Você pode redefinir ou desativar o ID de publicidade em Configurações do Android → Google → Anúncios. Detalhes: https://policies.google.com/technologies/ads.

### Conteúdo e fontes

- O catálogo de trilhas pode ser atualizado a partir do CDN/site do projeto (`thurler-it-consultancy.web.app` ou equivalente).
- Tipografia pode ser baixada em runtime via Google Fonts quando a rede estiver disponível.

### Compras e assinaturas

O app oferece (ou passará a oferecer) assinatura paga pelo **Google Play Billing**. O pagamento é processado pelo Google: **não recebemos nem guardamos número de cartão ou dados de pagamento**. Podemos guardar o estado da assinatura (produto, ativa/expirada e token de compra) associado ao seu UID para liberar o conteúdo pago. Você gerencia ou cancela a assinatura em Play Store → Pagamentos e assinaturas.

## O que **não** fazemos (hoje)

- Não vendemos seus dados
- Não pedimos localização, contatos, microfone ou câmera
- Labs de prática são **simulados** no app (não executam shell real no dispositivo)

## Compartilhamento

Dados de autenticação e perfil transitam pelos serviços da **Google** (Google Sign-In, Firebase Authentication, Cloud Firestore, Google Play Billing) conforme as políticas desses produtos. Os dados descritos em “Anúncios” são compartilhados com o Google AdMob.

## Exclusão de conta

No app: **Perfil → Excluir conta**. O fluxo:

1. pede confirmação;
2. apaga o documento `users/{uid}` no Firestore;
3. solicita a exclusão da conta no Firebase Authentication (pode pedir para entrar de novo com o Google se a sessão estiver antiga);
4. limpa progresso e preferências locais neste aparelho.

Você também pode solicitar exclusão pelo e-mail de suporte.

## Retenção

- Perfil na nuvem: enquanto a conta existir
- Dados locais: até você limpar o armazenamento do app, desinstalar, ou excluir a conta pelo fluxo acima

## Crianças

O app não é direcionado a menores de 13 anos. Se você for responsável legal e acreditar que uma criança nos enviou dados, escreva para o e-mail de suporte.

## Alterações

Podemos atualizar esta política. A data no topo indica a versão vigente. Mudanças relevantes serão refletidas no app e, quando a URL pública existir, na página hospedada.

## Contato

Dúvidas sobre privacidade: **contato@matheusthurler.com.br**.
