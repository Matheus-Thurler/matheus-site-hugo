---
title: "Política de Privacidade — Trilha Ops"
date: 2026-09-25
layout: "page"
url: /trilha-ops/privacy/
comments_disabled: true
description: "Política de privacidade do aplicativo Trilha Ops (Android): dados coletados, compartilhamento, retenção e exclusão de conta."
---

**Última atualização:** 25 de novembro de 2026  
**Idioma:** português (Brasil)

Esta política descreve, de forma honesta, quais dados o aplicativo **Trilha Ops** (pacote `br.com.matheusthurler.trilha_ops`) trata. O app é um produto educacional de estudo DevOps no celular.

## Quem somos

Trilha Ops é mantido por Thurler IT Consultancy.

- **Controlador dos dados:** MATHEUS ANTONIO THURLER DA SILVA CONSULTORIA EM TECNOLOGIA DA INFORMAÇÃO LTDA (nome fantasia: Thurler IT Consultancy), CNPJ 52.195.603/0001-90, com sede na Rua Visconde de Pirajá, 414, Sala 718, Ipanema, Rio de Janeiro/RJ, CEP 22410-002.
- **Encarregado pelo tratamento de dados pessoais:** Matheus Antonio Thurler da Silva, canal para exercer seus direitos: **contato@matheusthurler.com.br**.

## Quais dados coletamos

### Conta Google (Firebase Authentication)

Ao tocar em “Continuar com Google”, o Firebase Authentication recebe o login da sua conta Google. Guardamos no Firebase (e espelhamos em Firestore) identificadores necessários para a sessão:

- UID da conta no Firebase
- e-mail
- nome de exibição (quando a Google fornece)
- URL da foto de perfil (quando a Google fornece)

Esses dados existem para **identificar você** no app. **O progresso de estudo (módulos concluídos, melhores notas de quiz e sequência/streak) é guardado neste aparelho e também no seu perfil no Firestore**, para você recuperá-lo ao trocar de celular ou reinstalar o app. Só você acessa esses dados (regras de acesso por conta).

### Estudar sem conta

Dá para estudar o primeiro módulo (O que é Linux) e fazer o quiz sem entrar. Nesse caso nada vai para a nuvem: o progresso fica só neste aparelho até você entrar com Google. Ao entrar, ele passa a fazer parte do seu perfil. Se entrar com uma conta diferente da que usou antes neste aparelho, o progresso local anterior é apagado para não ir parar na conta errada.

### Certificado

O certificado por nível concluído é uma tela dentro do app, gerada no aparelho com o nome da sua conta Google e a data. Não é enviado a ninguém e não tem validade oficial.

### Perfil no Firestore

Criamos/atualizamos o documento `users/{uid}` com os campos de perfil acima e timestamps de criação / último login.

### No aparelho (local)

- Progresso de módulos e melhores scores de quiz
- Sequência diária (streak)
- Preferências (ex.: animações de acerto, nome de exibição local)
- Cache de conteúdo de estudo (trilhas/módulos)

### Anúncios (Google AdMob)

O app exibe anúncios de banner do **Google AdMob**. Para exibi-los e medir resultados, o AdMob pode usar o **ID de publicidade** do aparelho e coletar **localização aproximada**, dados de **diagnóstico** (ex.: falhas) e de **interação** com os anúncios. Por padrão pedimos anúncios **não personalizados**. A personalização só pode ser ligada em Perfil → Anúncios personalizados por quem confirmar ter **18 anos ou mais**; essa confirmação fica só no seu aparelho e não é enviada a ninguém. Também pode redefinir ou desativar o ID de publicidade em Configurações do Android → Google → Anúncios. Detalhes: https://policies.google.com/technologies/ads.

### Análise de uso e falhas (Firebase Analytics e Crashlytics)

Usamos o **Firebase Analytics** para entender como o app é usado e melhorá-lo: eventos como módulo aberto, quiz concluído (trilha, módulo, acertos), além de dados técnicos do aparelho (modelo, versão do Android, idioma) e um identificador da instalação do app. Usamos o **Firebase Crashlytics** para receber relatórios de falhas (tipo do erro, versão do app, modelo do aparelho). Não usamos esses dados para vender nem para identificar você pelo nome; eles ficam associados à instalação do app. A base legal é o nosso legítimo interesse em manter e melhorar o app. Você pode desligar quando quiser em Perfil → Dados de uso e falhas; o Google guarda esses dados pelos prazos padrão do Firebase. Tanto o Analytics quanto o Crashlytics são serviços do Google.

### Lembrete diário

Se você ativar, o app agenda um **lembrete local** de estudo no próprio aparelho, no horário escolhido. Ele não envia dados para a nuvem. Você pode desligar em Perfil ou nas configurações de notificações do Android.

### Consentimento de anúncios

Antes dos anúncios, o app pode exibir a mensagem de consentimento do Google (UMP), quando exigida, para você escolher como seus dados são usados em anúncios.

### Conteúdo e fontes

- O catálogo de trilhas pode ser atualizado a partir do CDN/site do projeto (`thurler-it-consultancy.web.app` ou equivalente).
- As fontes do app são baixadas do Google Fonts quando há rede; nessa requisição o Google recebe o endereço IP do aparelho.

### Compras e assinaturas

O app oferece assinatura paga (mensal, anual e vitalício) pelo **Google Play Billing**. O pagamento é processado pelo Google: **não recebemos nem guardamos número de cartão ou dados de pagamento**. Guardamos o estado da assinatura (produto, ativa/expirada, validade e o token de compra do Google Play) no documento `entitlements/{uid}`, e um vínculo entre o token (guardado como hash) e o seu UID em `purchaseTokens`, para liberar o conteúdo pago e impedir que a mesma compra seja usada em outra conta. Você gerencia ou cancela a assinatura em Play Store → Pagamentos e assinaturas.

## Transferência internacional

Google (Firebase, AdMob, Play) pode processar dados fora do Brasil, sob os contratos e salvaguardas do próprio Google.

## Seus direitos

Pela LGPD (art. 18) você pode pedir confirmação, acesso, correção, portabilidade, eliminação e informação sobre compartilhamento. Escreva para **contato@matheusthurler.com.br**; respondemos em até 15 dias.

## O que **não** fazemos (hoje)

- Não vendemos seus dados
- Não pedimos localização, contatos, microfone ou câmera
- Labs de prática são **simulados** no app (não executam shell real no dispositivo)

## Compartilhamento

Dados de autenticação e perfil transitam pelos serviços da **Google** (Google Sign-In, Firebase Authentication, Cloud Firestore, Google Play Billing, Firebase Analytics, Firebase Crashlytics) conforme as políticas desses produtos. Os dados descritos em “Anúncios” são compartilhados com o Google AdMob, e os de “Análise de uso e falhas”, com o Google (Firebase).

<a id="exclusao-de-conta"></a>

## Exclusão de conta

No app: **Perfil → Excluir conta**. O fluxo:

1. pede confirmação;
2. apaga o documento `users/{uid}` no Firestore;
3. solicita a exclusão da conta no Firebase Authentication (pode pedir para entrar de novo com o Google se a sessão estiver antiga);
4. limpa progresso e preferências locais neste aparelho.

O registro de assinatura (`entitlements`) e o vínculo do token de compra com a sua conta também são apagados. Excluir a conta não cancela a assinatura no Google Play.

Você também pode solicitar exclusão pelo e-mail de suporte.

## Retenção

- Perfil na nuvem: enquanto a conta existir
- Dados locais: até você limpar o armazenamento do app, desinstalar, ou excluir a conta pelo fluxo acima

## Crianças e adolescentes

O Trilha Ops não é direcionado a menores de 18 anos e não tem rede social, chat nem conteúdo gerado por usuários. Não pedimos a idade no cadastro. Por precaução (Lei 15.211/2025, ECA Digital): anúncios personalizados ficam desligados e só se ligam depois da confirmação de que a pessoa tem 18 anos ou mais; não montamos perfil de interesses para publicidade a partir dos seus dados. Se você for responsável legal e acreditar que uma criança ou adolescente nos enviou dados, escreva para **contato@matheusthurler.com.br** e apagamos a conta.

## Alterações

Podemos atualizar esta política. A data no topo indica a versão vigente. Mudanças relevantes serão refletidas no app e na página hospedada na URL pública acima.

## Contato

Dúvidas sobre privacidade: **contato@matheusthurler.com.br** (Encarregado: Matheus Antonio Thurler da Silva).
