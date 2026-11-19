# Site Dinheiro Explicado

Site estático (pronto para Hostinger, com ou sem GitHub). Textos de Sara Marques Amorim.

## Como publicar ou editar um artigo

1. Edite `conteudo.json`, na lista `posts`:
   `slug`, `titulo`, `resumo`, `categoria` (um dos slugs de `categorias`), `data` e `atualizado` (AAAA-MM-DD),
   `capa` (`img/arquivo.jpg`, opcional), `alt_capa`, `fontes` (lista de `{"nome", "url"}`), `afiliado` (true quando o artigo tiver link de afiliado: mostra o aviso no topo) e `corpo`.
2. Coloque as imagens em `img/`.
3. Rode `python3 build.py`. Ele gera `index.html`, `blog/`, `blog/<slug>/`, `quem-somos/`, `politica-de-privacidade/`, `404.html`
   e, quando `site.dominio` estiver preenchido, `sitemap.xml` e `robots.txt`.
4. `python3 build.py --previa` gera uma prévia em `_previa/` (inclui os posts com `"rascunho": true`). Não suba `_previa/`.

## Formato do `corpo`

- `## Título` e `### Subtítulo`
- `- item` e `1. item`
- `> texto` (destaque)
- `**negrito**`, `*itálico*`, `[texto](https://link)` e links internos `[texto](/blog/slug/)`
- `![descrição](img/foto.jpg)`
- `| coluna | coluna |` (tabela, com a linha `|---|---|` depois do cabeçalho)
- `@resposta texto` (caixa verde "Resposta rápida", logo no início do artigo)
- `@golpe texto` (caixa amarela "Cuidado com golpes")
- `@produto Nome | descrição | link de afiliado | img/foto.jpg | preço | loja` (card de produto com botão "Ver oferta"; imagem, preço e loja são opcionais; vários seguidos ficam lado a lado)

## Achados (vitrine de afiliados)

Lista `vitrine` em `conteudo.json`: `nome`, `descricao`, `link`, `img`, `preco`, `loja`, `categoria` (slug do assunto).
Quando houver pelo menos um item sem `"rascunho": true`, o site cria a página `/achados/`, o link no menu e a seção na página inicial.

## Grupo de ofertas

Preencha `site.grupo_ofertas.url` (e `nome`) para mostrar o convite do grupo na página inicial e no rodapé.

## Calculadoras

A página `/ferramentas/` tem duas calculadoras (renda extra para quitar dívida e simulador de empréstimo pela tabela Price).
A calculadora de renda extra também aparece na página inicial, logo depois do bloco de Renda extra.

## Regras editoriais

- Todo número, data, valor e regra com fonte oficial em `fontes` (INSS, Caixa, Receita, Banco Central, MTE, MDS, DOU).
- Sempre atualizar o campo `atualizado` quando a informação mudar.
- Nenhum conteúdo patrocinado sem identificar que é publicidade.
- Todo link de afiliado sai com o selo "Link de afiliado" e `rel="sponsored"`.
- Renda extra: nunca prometer ganho garantido nem indicar nada que peça pagamento para começar.

## Antes de pôr no ar

Domínio: https://dinheiroexplicado.com.br (o endereço com www redireciona para o sem www).
