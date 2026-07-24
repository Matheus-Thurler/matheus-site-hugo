# Performance TODO — Lighthouse 100 (desktop + mobile)

Meta: **100** em Performance, Accessibility, Best Practices e SEO no [PageSpeed Insights](https://pagespeed.web.dev/?url=https://matheusthurler.com.br).

**Realidade:** mobile **100** com AdSense + GA sempre no `<head>` é improvável. Cenário B (consent + lite YouTube) ou C (sem ads) para 100 mobile.

Medir antes/depois: PageSpeed mobile + desktop. Budget sugerido mobile: LCP < 2,5s, TBT < 200ms, CLS < 0,1.

---

## Fase 1 — Quick wins (maior ROI)

- [ ] Avatar: trocar `static/images/avatar.png` (3,1 MB) por `avatar.svg` ou WebP ~96×96; atualizar `hugo.yaml` `params.author.avatar`
- [ ] Home: `fetchpriority="high"`, `width`/`height` no avatar em `layouts/home.html`
- [ ] JS: `defer` em `main.js` e `gumshoe.polyfills.min.js` (`layouts/_partials/layout/head/js.html`)
- [ ] Busca: carregar `search.js` + `index.json` só ao abrir modal de busca (lazy)
- [ ] `preconnect` para domínios de terceiros se mantiver GA/AdSense (`layout/head.html`)
- [ ] `firebase.json`: cache longo (1 ano) para `/**/*.css`, `/**/*.js`, imagens estáticas

**Meta esperada:** mobile ~75–85, desktop ~90–95.

---

## Fase 2 — Imagens

- [ ] Covers em `static/images/covers/`: converter PNG 500–950 KB → WebP/AVIF
- [ ] Hugo image processing: `srcset` responsivo nos cards (`card-image.html` / `image-processor.html`)
- [ ] LCP: hero eager; covers abaixo da dobra com `loading="lazy"`
- [ ] Pipeline build ou script de compressão para novos posts (cover < 150 KB)

**Meta esperada:** mobile ~85–92.

---

## Fase 3 — YouTube e terceiros (decisão de produto)

- [ ] Home `custom_2.html`: lite YouTube (thumbnail + play, iframe só no clique)
- [ ] Cookie consent: GA + AdSense **após** aceite (Consent Mode v2)
- [ ] Giscus: manter abaixo da dobra; revisar script inline de tema
- [ ] AdSense in-article: carregar slot quando visível (Intersection Observer)

**Meta esperada:** mobile 90+ (cenário B).

---

## Fase 4 — CSS / JS do tema

- [ ] Rebuild Tailwind (`assets/css/main.css`) com purge dos layouts reais
- [ ] `chroma.css`: carregar só em posts com code blocks
- [ ] Revisar bundle `dock.js` + `main.js` (mobile)
- [ ] Alinhar Hugo CI com versão local documentada
- [ ] Corrigir warnings deprecated do tema Hugo (`.Site.Data`, etc.)

**Meta esperada:** desktop 100 perf; mobile ~92–98.

---

## Fase 5 — Governança

- [ ] Lighthouse CI no workflow de PR (`firebase-hosting-pull-request.yml`)
- [ ] Falhar PR se Performance mobile < threshold acordado
- [ ] Checklist pré-publicar: cover otimizado, alt, slug, PageSpeed spot-check
- [ ] (Opcional) `.cursor/rules/site-performance.mdc` neste repo

---

## Cenários de meta final

| Cenário | Mobile Perf | Desktop | Notas |
|---------|-------------|---------|-------|
| A — AdSense + GA sempre on | 85–92 | 95–100 | Mais realista com monetização |
| B — Consent + lite YouTube | 92–98 | 100 | Recomendado para 100 mobile |
| C — Sem ads | 95–100 | 100 | Máximo perf |

---

## SEO / A11y (fechar 100 nas outras categorias)

- [ ] Confirmar `sitemap.xml` gerado/publicado
- [ ] iframe YouTube: `title` descritivo
- [ ] Revisar contraste `text-muted-foreground` (links)
- [ ] Cookie banner: foco keyboard no botão Aceitar

---

## Achados do diagnóstico (referência)

| Item | Detalhe |
|------|---------|
| Avatar PNG | 3,1 MB — principal LCP mobile |
| CSS compilado | ~102 KB min |
| `main.js` | sem defer hoje |
| `search.js` | ~19 KB em todas as páginas |
| Terceiros | AdSense head, gtag, Giscus posts, 2 iframes home |
| Cookie banner | não bloqueia GA/Ads antes do accept |

Última revisão: 2026-06-28
