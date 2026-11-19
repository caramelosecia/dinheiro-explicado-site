#!/usr/bin/env python3
"""Gera o site Dinheiro Explicado a partir de conteudo.json.

Uso:
  python3 build.py           -> gera o site para publicar (sem rascunhos)
  python3 build.py --previa  -> gera uma prévia em _previa/ (com rascunhos e links que abrem direto no computador)
"""
import json, os, re, sys, shutil, html
from datetime import date

RAIZ = os.path.dirname(os.path.abspath(__file__))
PREVIA = "--previa" in sys.argv
SAIDA = os.path.join(RAIZ, "_previa") if PREVIA else RAIZ

dados = json.load(open(os.path.join(RAIZ, "conteudo.json"), encoding="utf-8"))
SITE = dados["site"]
CATS = {c["slug"]: c for c in dados["categorias"]}
POSTS = [p for p in dados["posts"] if PREVIA or not p.get("rascunho")]
POSTS.sort(key=lambda p: (p.get("atualizado") or p["data"]), reverse=True)
VITRINE = [v for v in dados.get("vitrine", []) if PREVIA or not v.get("rascunho")]
GRUPO = SITE.get("grupo_ofertas", {}) if SITE.get("grupo_ofertas", {}).get("url") else None
DOM = SITE.get("dominio", "").rstrip("/")
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
TEM_ACHADOS = bool(VITRINE)

AVISO_AFILIADO = ("Este conteúdo tem links de afiliado. Se você comprar por eles, o Dinheiro Explicado pode receber uma comissão, "
                  "sem nenhum custo extra para você. Isso não muda o que a gente recomenda.")

def data_br(s):
    a, m, d = s.split("-")
    return f"{int(d)} de {MESES[int(m)-1]} de {a}"

def esc(s):
    return html.escape(s or "", quote=True)

def minutos(texto):
    return max(2, round(len(re.findall(r"\w+", texto)) / 200))

# ---------- ícones (traço, 24x24) ----------
P = {
 "maos": '<path d="M3 13h3l3.5-2.5a2 2 0 0 1 2.5.2L13 12h3a2 2 0 0 1 0 4h-4"/><path d="M6 13v6h9l5-4.5a1.8 1.8 0 0 0-2.4-2.6L15 14"/><circle cx="15" cy="5.5" r="2.5"/>',
 "relogio": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
 "cofre": '<rect x="3" y="5" width="18" height="14" rx="3"/><circle cx="12" cy="12" r="3.2"/><path d="M12 8.8V7M6 19v2M18 19v2"/>',
 "cartao": '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M2.5 10h19M6.5 15h4"/>',
 "recibo": '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
 "documento": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
 "maleta": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3 13h18"/>',
 "foguete": '<path d="M5 15c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2.1-.1-2.9a2.2 2.2 0 0 0-2.9-.1z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.9A12.9 12.9 0 0 1 22 2c0 2.7-.8 7.5-6 11a22.4 22.4 0 0 1-4 2z"/><path d="M9 12H4s.5-3 2-4c1.6-1.1 5 0 5 0M12 15v5s3-.5 4-2c1.1-1.6 0-5 0-5"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "x": '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>',
 "escudo": '<path d="M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6z"/><path d="M12 8v4.5M12 16h.01"/>',
 "pergunta": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.3a2.6 2.6 0 0 1 5 .9c0 1.8-2.5 2.3-2.5 3.8M12 17h.01"/>',
 "moeda": '<circle cx="12" cy="12" r="9"/><path d="M14.8 9.2c-.4-.9-1.5-1.5-2.8-1.5-1.6 0-2.8.9-2.8 2.1 0 2.9 5.8 1.5 5.8 4.3 0 1.2-1.3 2.2-3 2.2-1.4 0-2.6-.7-3-1.7M12 6v1.7M12 16.3V18"/>',
 "calendario": '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
 "lupa": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 "livro": '<path d="M4 5a2 2 0 0 1 2-2h13v15H6a2 2 0 0 0-2 2z"/><path d="M4 20a2 2 0 0 0 2 2h13v-4"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "chevron": '<path d="m6 9 6 6 6-6"/>',
 "sacola": '<path d="M6 7h12l1 13H5z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/>',
 "calculadora": '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><path d="M8.5 6.5h7M8.5 11h.01M12 11h.01M15.5 11h.01M8.5 14.5h.01M12 14.5h.01M15.5 14.5h.01M8.5 18h.01M12 18h3.5"/>',
 "whats": '<path d="M3.5 20.5l1.3-4.2A8.5 8.5 0 1 1 8 19.4z"/><path d="M9 8.5c0 3.5 2.6 6.5 6.5 6.5l.9-1.7-2-1-1 1c-1-.4-2.2-1.6-2.7-2.7l1-1-1-2z"/>',
 "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
 "estrela": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
 "topo": '<path d="m6 15 6-6 6 6"/>',
}
def ic(nome, t=24):
    return f'<svg width="{t}" height="{t}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[nome]}</svg>'

# ---------- links ----------
def u(raiz, caminho=""):
    """Link relativo. Na prévia aponta para index.html para abrir direto do disco."""
    if PREVIA and (caminho == "" or caminho.endswith("/")):
        caminho += "index.html"
    return (raiz + caminho) or "./"

def u_assunto(raiz, slug):
    return f'{u(raiz, "blog/")}?assunto={slug}'

def abs_url(caminho=""):
    return f"{DOM}/{caminho}" if DOM else ""

def img_src(f, raiz):
    return esc(f) if f.startswith("http") else raiz + esc(f)

# ---------- produto de afiliado ----------
def produto_html(v, raiz, titulo="h3"):
    img = (f'<div class="prod-img"><img src="{img_src(v["img"], raiz)}" alt="{esc(v["nome"])}" loading="lazy"></div>' if v.get("img")
           else f'<div class="prod-img prod-sem">{ic("sacola", 40)}</div>')
    preco = f'<span class="prod-preco">{esc(v["preco"])}</span>' if v.get("preco") else ""
    loja = f'<span class="prod-loja">{esc(v["loja"])}</span>' if v.get("loja") else ""
    return f'''<div class="produto revela">{img}<div class="prod-corpo">
<span class="selo-afiliado">Link de afiliado</span>
<{titulo} class="prod-nome">{esc(v["nome"])}</{titulo}><p>{esc(v.get("descricao",""))}</p>
<div class="prod-rodape">{preco}{loja}</div>
<a class="btn btn-oferta" href="{esc(v["link"])}" target="_blank" rel="sponsored nofollow noopener">Ver oferta {ic("seta", 18)}</a>
</div></div>'''

# ---------- texto do artigo ----------
def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower().translate(str.maketrans("áàâãéêíóôõúüç", "aaaaeeiooouuc"))).strip("-")

def inline(s, raiz):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    def lk(m):
        txt, href = m.group(1), html.unescape(m.group(2))
        externo = href.startswith("http")
        if href.startswith("/"):
            href = u(raiz, href.lstrip("/"))
        attr = ' target="_blank" rel="noopener"' if externo else ""
        return f'<a href="{esc(href)}"{attr}>{txt}</a>'
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lk, s)
    return s

def corpo_html(texto, raiz):
    out, lista, tabela, prods, sumario = [], None, [], [], []
    def fecha_lista():
        nonlocal lista
        if lista: out.append(f"</{lista}>"); lista = None
    def fecha_tabela():
        nonlocal tabela
        if tabela:
            linhas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in tabela if not re.match(r"^\|?\s*:?-{2,}", l.strip())]
            h = '<div class="tabela"><table><thead><tr>' + "".join(f"<th>{inline(c, raiz)}</th>" for c in linhas[0]) + "</tr></thead><tbody>"
            for l in linhas[1:]:
                h += "<tr>" + "".join(f'<td data-rotulo="{esc(linhas[0][i] if i < len(linhas[0]) else "")}">{inline(c, raiz)}</td>' for i, c in enumerate(l)) + "</tr>"
            out.append(h + "</tbody></table></div>"); tabela = []
    def fecha_prods():
        nonlocal prods
        if prods:
            out.append('<div class="grade-produtos">' + "".join(produto_html(p, raiz) for p in prods) + "</div>"); prods = []
    for linha in texto.split("\n"):
        l = linha.rstrip()
        if l.startswith("@produto "):
            fecha_lista(); fecha_tabela()
            c = [x.strip() for x in l[9:].split("|")] + [""] * 6
            prods.append({"nome": c[0], "descricao": c[1], "link": c[2], "img": c[3], "preco": c[4], "loja": c[5]}); continue
        fecha_prods()
        if l.startswith("|"):
            fecha_lista(); tabela.append(l); continue
        fecha_tabela()
        m_ul, m_ol = re.match(r"^- (.+)", l), re.match(r"^\d+\. (.+)", l)
        if m_ul or m_ol:
            tipo = "ul" if m_ul else "ol"
            if lista != tipo: fecha_lista(); out.append(f"<{tipo}>"); lista = tipo
            out.append(f"<li>{inline((m_ul or m_ol).group(1), raiz)}</li>"); continue
        fecha_lista()
        if not l.strip(): continue
        if l.startswith("### "): out.append(f"<h3>{inline(l[4:], raiz)}</h3>")
        elif l.startswith("## "):
            t = l[3:]; idt = slugify(t); sumario.append((idt, t))
            out.append(f'<h2 id="{idt}">{inline(t, raiz)}</h2>')
        elif l.startswith("> "): out.append(f"<blockquote><p>{inline(l[2:], raiz)}</p></blockquote>")
        elif l.startswith("@resposta "):
            out.append(f'<div class="caixa caixa-resposta">{ic("check")}<div><b class="titulo-caixa">Resposta rápida</b><p>{inline(l[10:], raiz)}</p></div></div>')
        elif l.startswith("@golpe "):
            out.append(f'<div class="caixa caixa-golpe" role="note">{ic("escudo")}<div><b class="titulo-caixa">Cuidado com golpes</b><p>{inline(l[7:], raiz)}</p></div></div>')
        elif m := re.match(r"^!\[([^\]]*)\]\(([^)]+)\)", l):
            out.append(f'<figure><img src="{img_src(m.group(2), raiz)}" alt="{esc(m.group(1))}" loading="lazy">' + (f"<figcaption>{esc(m.group(1))}</figcaption>" if m.group(1) else "") + "</figure>")
        else: out.append(f"<p>{inline(l, raiz)}</p>")
    fecha_lista(); fecha_tabela(); fecha_prods()
    return "\n".join(out), sumario

# ---------- moldura ----------
FONTES = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">'

def pagina(raiz, caminho, titulo, descricao, conteudo, atual="", og_img="img/og-padrao.jpg", tipo="website", extra_head="", classe=""):
    titulo_full = titulo if SITE["nome"] in titulo else f"{titulo} | {SITE['nome']}"
    meta_dom = ""
    if DOM:
        canon = abs_url(caminho)
        meta_dom = f'<link rel="canonical" href="{canon}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{abs_url(og_img)}">'
    def item(h, n, k):
        return f'<a href="{u(raiz, h)}"' + (' aria-current="page"' if atual == k else "") + f">{n}</a>"
    drop = "".join(f'<a href="{u_assunto(raiz, c["slug"])}"><span class="ic">{ic(c["icone"], 20)}</span><span><b>{esc(c["nome"])}</b><small>{esc(c["descricao"])}</small></span></a>' for c in dados["categorias"])
    nav = (item("", "Início", "inicio")
           + f'<div class="drop"><button type="button" class="drop-btn" aria-expanded="false" aria-controls="drop-assuntos">Assuntos {ic("chevron", 16)}</button><div class="drop-painel" id="drop-assuntos">{drop}</div></div>'
           + item("blog/", "Artigos", "blog")
           + item("ferramentas/", "Calculadoras", "ferramentas")
           + (item("achados/", "Achados", "achados") if TEM_ACHADOS else "")
           + item("quem-somos/", "Quem somos", "sobre"))
    cats_rod = "".join(f'<li><a href="{u_assunto(raiz, c["slug"])}">{esc(c["nome"])}</a></li>' for c in dados["categorias"])
    grupo_rod = f'<a class="btn btn-neon" href="{esc(GRUPO["url"])}" target="_blank" rel="noopener">{ic("whats", 20)} {esc(GRUPO.get("nome") or "Entrar no grupo")}</a>' if GRUPO else ""
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo_full)}</title>
<meta name="description" content="{esc(descricao)}">
<meta name="theme-color" content="#00230D">
<meta property="og:type" content="{tipo}"><meta property="og:site_name" content="{SITE['nome']}"><meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{esc(titulo)}"><meta property="og:description" content="{esc(descricao)}">
<meta name="twitter:card" content="summary_large_image">
{meta_dom}
<link rel="icon" href="{raiz}favicon.ico" sizes="any"><link rel="icon" type="image/png" href="{raiz}img/favicon-48.png"><link rel="apple-touch-icon" href="{raiz}img/apple-touch-icon.png">
{FONTES}
<link rel="stylesheet" href="{raiz}assets/site.css">
<script>document.documentElement.classList.add('js')</script>
{extra_head}
</head>
<body class="{classe}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<div class="faixa-golpe" role="note"><div class="wrap">{ic("escudo", 18)}<span><strong>Atenção:</strong> nenhum órgão público cobra para liberar benefício. Pediram pagamento antecipado? É golpe.</span></div></div>
<header class="topo"><div class="wrap">
<a class="marca" href="{u(raiz)}"><img src="{raiz}img/logo.png" alt="Dinheiro Explicado — página inicial" width="872" height="320"></a>
<button class="btn-menu" aria-expanded="false" aria-controls="menu"><span class="hamb"><i></i><i></i><i></i></span> Menu</button>
<nav class="menu" id="menu" aria-label="Principal">{nav}<a class="cta-menu" href="{u(raiz, "blog/")}#busca">{ic("lupa", 18)}<span>Buscar</span></a></nav>
</div></header>
<main id="conteudo">
{conteudo}
</main>
<footer class="rodape"><div class="wrap">
<div class="grade">
<div><img src="{raiz}img/logo-branco.png" alt="Dinheiro Explicado" width="872" height="320">
<p>Veículo de comunicação independente sobre o dinheiro do dia a dia do brasileiro. Toda informação com fonte oficial citada e data de atualização.</p>
<p><strong style="color:#fff">Não somos banco, fintech nem correspondente bancário.</strong> Nunca pedimos seus dados bancários, senha ou pagamento. Links de afiliado são sempre identificados.</p>
{grupo_rod}</div>
<div><h4>Assuntos</h4><ul>{cats_rod}</ul></div>
<div><h4>O site</h4><ul>
<li><a href="{u(raiz, "blog/")}">Todos os artigos</a></li>
<li><a href="{u(raiz, "ferramentas/")}">Calculadoras</a></li>
{f'<li><a href="{u(raiz, "achados/")}">Achados</a></li>' if TEM_ACHADOS else ""}
<li><a href="{u(raiz, "quem-somos/")}">Quem somos</a></li>
<li><a href="{u(raiz, "quem-somos/")}#como-apuramos">Como apuramos</a></li>
<li><a href="{u(raiz, "quem-somos/")}#como-o-site-se-mantem">Como o site se mantém</a></li>
<li><a href="{u(raiz, "politica-de-privacidade/")}">Política de privacidade</a></li>
</ul></div>
</div>
<div class="legal"><span>© {date.today().year} Dinheiro Explicado.</span><span>Conteúdo informativo. Confirme sempre no canal oficial do órgão responsável.</span></div>
</div></footer>
<button class="ir-topo" type="button" aria-label="Voltar ao topo">{ic("topo", 22)}</button>
<script src="{raiz}assets/site.js" defer></script>
</body>
</html>'''

def card(p, raiz, destaque=False):
    c = CATS.get(p["categoria"], {"nome": "", "icone": "moeda"})
    capa = (f'<div class="capa"><img src="{img_src(p["capa"], raiz)}" alt="{esc(p.get("alt_capa",""))}" loading="lazy"></div>' if p.get("capa")
            else f'<div class="capa capa-ic cat-{p["categoria"]}">{ic(c.get("icone","moeda"), 54)}</div>')
    at = p.get("atualizado") or p["data"]
    afil = '<span class="tag-afil" title="Tem links de afiliado">Afiliado</span>' if p.get("afiliado") else ""
    return f'''<article class="card revela{' card-destaque' if destaque else ''}" data-assunto="{p["categoria"]}" data-busca="{esc((p["titulo"]+" "+p["resumo"]+" "+c["nome"]).lower())}">
{capa}<div class="corpo"><div class="card-tags"><span class="etiqueta">{esc(c["nome"])}</span>{afil}</div>
<h3><a href="{u(raiz, "blog/"+p["slug"]+"/")}">{esc(p["titulo"])}</a></h3><p>{esc(p["resumo"])}</p>
<span class="meta">{ic("calendario", 15)} Atualizado em {data_br(at)} · {minutos(p["corpo"])} min de leitura</span></div></article>'''

def vazio(txt="Os primeiros artigos estão chegando"):
    return f'<div class="vazio">{ic("livro", 32)}<b>{txt}</b>Em breve você encontra aqui respostas sobre benefícios, aposentadoria, FGTS, renda extra, dívidas e mais.</div>'

FONTES_OF = ["Ministério do Trabalho e Emprego", "INSS", "Caixa Econômica Federal", "Receita Federal", "Banco Central", "Ministério do Desenvolvimento Social", "Diário Oficial da União"]
NAO = ["Não somos banco, fintech nem correspondente bancário.",
       "Não fazemos empréstimo, não emitimos cartão e não intermediamos benefício.",
       "Não cobramos por informação que é gratuita e pública.",
       "Não prometemos aprovação, liberação de valor, nem renda extra garantida.",
       "Não publicamos link de afiliado ou conteúdo patrocinado sem avisar."]

def mini_autora(raiz):
    a = SITE["autora"]
    if a.get("foto"):
        return f'<span class="mini"><img src="{img_src(a["foto"], raiz)}" alt="" width="36" height="36"></span>'
    return f'<span class="mini">{esc(a["iniciais"])}</span>'

def bloco_autora(raiz, titulo="h3"):
    a = SITE["autora"]
    av = f'<img src="{img_src(a["foto"], raiz)}" alt="Foto de {esc(a["nome"])}" width="112" height="112" loading="lazy">' if a.get("foto") else esc(a["iniciais"])
    links = " · ".join(f'<a href="{esc(l["url"])}" target="_blank" rel="noopener">{esc(l["nome"])}</a>' for l in a.get("links", []))
    return f'''<div class="autora revela"><div class="avatar">{av}</div><div>
<span class="rotulo">Quem escreve</span><{titulo}>{esc(a["nome"])}</{titulo}><div class="cargo">{esc(a["cargo"])}</div>
<p>{esc(a["bio"])}</p>{f'<p class="autora-links">{links}</p>' if links else ""}</div></div>'''

def bloco_alerta():
    return f'''<div class="alerta revela" role="note"><div class="ic">{ic("escudo", 34)}</div><div>
<h2>Aviso importante: cuidado com golpes</h2>
<p><strong>Nenhum órgão público cobra para você consultar ou solicitar um benefício.</strong> Se alguém pedir pagamento antecipado para liberar dinheiro em seu nome, é golpe.</p>
<p>O Dinheiro Explicado nunca vai pedir seus dados bancários, sua senha ou qualquer pagamento.</p>
</div></div>'''

def calc_renda(id_="calc-renda", compacto=False):
    return f'''<form class="calc revela" id="{id_}" data-calc="renda" novalidate>
<div class="calc-topo"><span class="ic">{ic("foguete", 26)}</span><div><h3>Quanto de renda extra eu preciso para quitar a dívida?</h3>
<p>Coloque o valor da dívida e em quanto tempo quer pagar. A conta é feita aqui no seu celular: nada é enviado.</p></div></div>
<div class="calc-campos">
<label>Valor da dívida<span class="campo"><i>R$</i><input name="divida" inputmode="decimal" placeholder="3.000,00" value="3.000,00"></span></label>
<label>Quero quitar em<span class="campo"><input name="meses" type="number" min="1" max="120" value="10"><i>meses</i></span></label>
<label>Juros ao mês <small>(opcional)</small><span class="campo"><input name="juros" inputmode="decimal" placeholder="0" value="0"><i>%</i></span></label>
</div>
<output class="calc-resultado" aria-live="polite">
<div class="res-principal"><span>Você precisa juntar por mês</span><b data-r="mes">R$ 300,00</b></div>
<div class="res-linha"><div><span>Por semana</span><b data-r="semana">—</b></div><div><span>Por dia útil</span><b data-r="dia">—</b></div><div><span>Total pago</span><b data-r="total">—</b></div></div>
</output>
<p class="calc-nota">Estimativa simples, sem multa nem encargos de atraso. Antes de fechar acordo, confira o valor com o credor. {"" if compacto else ""}</p>
</form>'''

def calc_emprestimo(id_="calc-emprestimo"):
    return f'''<form class="calc revela" id="{id_}" data-calc="emprestimo" novalidate>
<div class="calc-topo"><span class="ic">{ic("calculadora", 26)}</span><div><h3>Simulador de parcelas de empréstimo</h3>
<p>Veja quanto você paga de juros no total antes de assinar. Use a taxa mensal que o banco informar no contrato (CET).</p></div></div>
<div class="calc-campos">
<label>Valor que vai pegar<span class="campo"><i>R$</i><input name="valor" inputmode="decimal" value="5.000,00"></span></label>
<label>Taxa ao mês (CET)<span class="campo"><input name="taxa" inputmode="decimal" value="3,5"><i>%</i></span></label>
<label>Número de parcelas<span class="campo"><input name="parcelas" type="number" min="1" max="120" value="24"><i>vezes</i></span></label>
</div>
<output class="calc-resultado" aria-live="polite">
<div class="res-principal"><span>Parcela mensal</span><b data-r="parcela">—</b></div>
<div class="res-linha"><div><span>Total pago</span><b data-r="total">—</b></div><div><span>Só de juros</span><b data-r="juros">—</b></div><div><span>Você paga a mais</span><b data-r="pct">—</b></div></div>
<div class="barra-juros" aria-hidden="true"><i data-r="barra"></i></div>
<div class="legenda-barra"><span><i class="l1"></i> Valor emprestado</span><span><i class="l2"></i> Juros</span></div>
</output>
<p class="calc-nota">Cálculo pela tabela Price, a mais usada no Brasil. O valor final pode mudar com seguros e tarifas: compare sempre o CET de cada proposta.</p>
</form>'''

# ---------- páginas ----------
def home():
    r = ""
    blocos = ""
    for cat in dados["categorias"]:
        ps = [p for p in POSTS if p["categoria"] == cat["slug"]][:3]
        nome_min = cat["nome"] if cat["slug"] in ("fgts", "aposentadoria") else cat["nome"].lower()
        lista = (f'<div class="grade-posts">{"".join(card(p, r) for p in ps)}</div>' if ps
                 else f'<div class="vazio vazio-mini">Os primeiros artigos sobre {esc(nome_min)} chegam em breve.</div>')
        blocos += f'''<div class="bloco-assunto revela" id="assunto-{cat["slug"]}">
<div class="bloco-topo"><span class="ic cat-{cat["slug"]}">{ic(cat["icone"], 24)}</span><div><h2>Últimas de {esc(cat["nome"])}</h2><p>{esc(cat["descricao"])}</p></div>
<a class="ver-mais" href="{u_assunto(r, cat["slug"])}">Ver mais {ic("seta", 18)}<span class="sr"> sobre {esc(cat["nome"])}</span></a></div>
{lista}</div>'''
        if cat["slug"] == "renda-extra":
            blocos += f'''<section class="faixa-calc revela"><div class="faixa-calc-texto"><span class="sobre">Calculadora</span>
<h2>Quanto de renda extra você precisa para sair do vermelho?</h2>
<p>Faça a conta em segundos e veja quanto juntar por mês, por semana e por dia.</p>
<a class="link-seta" href="{u(r, "ferramentas/")}">Ver todas as calculadoras {ic("seta", 18)}</a></div>
{calc_renda("calc-renda-home", True)}</section>'''
    chips = "".join(f'<a href="{u(r, "blog/")}?q={esc(b)}">{esc(b)}</a>' for b in SITE.get("buscas_populares", []))
    vitr = ""
    if VITRINE:
        vitr = f'''<section class="secao secao-cinza"><div class="wrap">
<div class="bloco-topo"><span class="ic">{ic("sacola", 24)}</span><div><h2>Achados que ajudam no bolso</h2><p>Produtos escolhidos para economizar no dia a dia ou começar uma renda extra.</p></div>
<a class="ver-mais" href="{u(r, "achados/")}">Ver todos {ic("seta", 18)}</a></div>
<div class="grade-produtos">{"".join(produto_html(v, r) for v in VITRINE[:4])}</div>
<p class="aviso-afil-curto">{ic("info", 16)} Links de afiliado: podemos receber comissão, sem custo extra para você.</p>
</div></section>'''
    grupo = ""
    if GRUPO:
        grupo = f'''<section class="secao"><div class="wrap"><div class="cta-grupo revela"><span class="ic">{ic("whats", 34)}</span><div><h2>Ofertas e alertas no seu celular</h2><p>{esc(GRUPO.get("texto",""))}</p></div>
<a class="btn btn-neon" href="{esc(GRUPO["url"])}" target="_blank" rel="noopener">Entrar no grupo</a></div></div></section>'''
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["nome"], "description": SITE["descricao"], "inLanguage": "pt-BR"}
    if DOM:
        jsonld["url"] = DOM + "/"
        jsonld["potentialAction"] = {"@type": "SearchAction", "target": DOM + "/blog/?q={busca}", "query-input": "required name=busca"}
    c = f'''
<section class="hero"><div class="hero-fundo" aria-hidden="true"><i></i><i></i><i></i></div><div class="wrap">
<div class="hero-texto">
<h1>O dinheiro do dia a dia, <em>explicado sem letra miúda.</em></h1>
<p class="lead">Benefícios, aposentadoria, FGTS, renda extra, dívidas e direitos do trabalhador em uma linguagem que qualquer pessoa entende.</p>
<form class="busca-hero" action="{u(r, "blog/")}" method="get" role="search">
<label class="sr" for="q-hero">O que você quer saber?</label>
{ic("lupa", 22)}<input id="q-hero" name="q" type="search" placeholder="O que você quer saber? Ex.: saque do FGTS" autocomplete="off">
<button class="btn btn-pri" type="submit">Buscar</button></form>
<div class="chips" aria-label="Buscas populares"><span>Mais buscados:</span>{chips}</div>
</div>
<div class="perguntas" aria-label="As perguntas que respondemos">
<div class="pergunta"><span class="ic">{ic("pergunta", 26)}</span><div><b>Eu tenho direito?</b><span>As regras, sem jargão.</span></div></div>
<div class="pergunta"><span class="ic">{ic("moeda", 26)}</span><div><b>Quanto vou receber?</b><span>Valores conferidos na fonte oficial.</span></div></div>
<div class="pergunta"><span class="ic">{ic("calendario", 26)}</span><div><b>Quando o dinheiro cai?</b><span>Datas e calendários atualizados.</span></div></div>
<div class="pergunta"><span class="ic">{ic("foguete", 26)}</span><div><b>Como ganhar um dinheiro a mais?</b><span>Renda extra de verdade, sem promessa.</span></div></div>
</div>
</div></section>

<section class="secao" id="assuntos"><div class="wrap">
<h2 class="sr">Últimos artigos por assunto</h2>
{blocos}
</div></section>
{vitr}
{grupo}
'''
    return pagina(r, "", SITE["nome"] + " — benefícios, FGTS, INSS, renda extra e dívidas explicados", SITE["descricao"], c, "inicio",
                  extra_head=f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')

def blog():
    r = "../"
    def n(slug): return sum(1 for p in POSTS if p["categoria"] == slug)
    botoes = f'<button type="button" data-f="" aria-pressed="true">Todos <small>{len(POSTS)}</small></button>' + "".join(f'<button type="button" data-f="{c["slug"]}" aria-pressed="false">{ic(c["icone"], 16)} {esc(c["nome"])} <small>{n(c["slug"])}</small></button>' for c in dados["categorias"])
    cards = "".join(card(p, r) for p in POSTS)
    c = f'''
<section class="pagina-topo"><div class="wrap">
<h1>Artigos</h1><p>Respostas diretas sobre o dinheiro do dia a dia, com a fonte oficial e a data da última atualização em cada página.</p>
<div class="busca"><label class="sr" for="busca">Buscar artigo</label>{ic("lupa", 22)}<input id="busca" type="search" placeholder="Buscar: FGTS, Bolsa Família, renda extra..." autocomplete="off"></div>
</div></section>
<section class="secao" style="padding-top:32px"><div class="wrap">
<div class="filtros" role="group" aria-label="Filtrar por assunto">{botoes}</div>
<p class="contagem" aria-live="polite"></p>
<div class="grade-posts" id="lista">{cards}</div>
<div id="nada" hidden>{vazio("Nenhum artigo encontrado por aqui ainda")}</div>
</div></section>'''
    return pagina(r, "blog/", "Artigos", "Todos os artigos do Dinheiro Explicado: benefícios, aposentadoria, FGTS, renda extra, crédito, dívidas, impostos e direitos do trabalhador.", c, "blog", classe="pg-blog")

def artigo(p):
    r = "../../"
    cat = CATS.get(p["categoria"], {"nome": "", "slug": "", "icone": "moeda"})
    at = p.get("atualizado") or p["data"]
    a = SITE["autora"]
    corpo, sumario = corpo_html(p["corpo"], r)
    capa = f'<div class="estreito"><div class="capa-artigo"><img src="{img_src(p["capa"], r)}" alt="{esc(p.get("alt_capa",""))}"></div></div>' if p.get("capa") else ""
    fontes = "".join(f'<li><a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f["nome"])}</a></li>' for f in p.get("fontes", []))
    rel = [x for x in POSTS if x["slug"] != p["slug"] and x["categoria"] == p["categoria"]][:3] or [x for x in POSTS if x["slug"] != p["slug"]][:3]
    rel_html = f'<section class="secao secao-cinza"><div class="wrap"><div class="bloco-topo"><span class="ic">{ic("livro", 24)}</span><div><h2>Leia também</h2></div></div><div class="grade-posts">{"".join(card(x, r) for x in rel)}</div></div></section>' if rel else ""
    toc = ""
    if len(sumario) >= 3:
        toc = '<nav class="sumario" aria-label="Neste artigo"><b>Neste artigo</b><ol>' + "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in sumario) + "</ol></nav>"
    afil = f'<div class="aviso-afiliado">{ic("info", 20)}<p>{AVISO_AFILIADO} <a href="{u(r, "quem-somos/")}#como-o-site-se-mantem">Saiba mais</a>.</p></div>' if p.get("afiliado") else ""
    url_art = abs_url(f"blog/{p['slug']}/")
    share = f'''<div class="compartilhar"><span>Compartilhe com quem precisa:</span>
<a class="btn-comp whats" href="https://wa.me/?text={html.escape(p["titulo"])}%20{url_art}" target="_blank" rel="noopener" data-whats>{ic("whats", 20)} WhatsApp</a>
<button type="button" class="btn-comp" data-copiar>{ic("link", 20)} <span>Copiar link</span></button></div>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": p["titulo"], "description": p["resumo"], "datePublished": p["data"], "dateModified": at,
         "inLanguage": "pt-BR", "author": {"@type": "Person", "name": a["nome"]}, "publisher": {"@type": "Organization", "name": SITE["nome"]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", **({"item": DOM + "/"} if DOM else {})},
            {"@type": "ListItem", "position": 2, "name": cat["nome"], **({"item": f"{DOM}/blog/?assunto={cat['slug']}"} if DOM else {})},
            {"@type": "ListItem", "position": 3, "name": p["titulo"]}]}]}
    if DOM:
        ld["@graph"][0]["mainEntityOfPage"] = url_art
        if p.get("capa"): ld["@graph"][0]["image"] = abs_url(p["capa"])
    c = f'''
<div class="progresso" aria-hidden="true"><i></i></div>
<article>
<header class="artigo-topo"><div class="estreito">
{'<div class="aviso-exemplo">Página de exemplo: só aparece na prévia, não vai para o site no ar.</div>' if p.get("rascunho") else ""}
<nav class="migalhas" aria-label="Você está em"><a href="{u(r)}">Início</a> › <a href="{u_assunto(r, cat["slug"])}">{esc(cat["nome"])}</a></nav>
<h1>{esc(p["titulo"])}</h1>
<p class="resumo">{esc(p["resumo"])}</p>
<div class="assinatura">{mini_autora(r)}<span>Por <b>{esc(a["nome"])}</b></span><span class="atualizado">{ic("calendario", 16)} Atualizado em <time datetime="{at}">{data_br(at)}</time></span><span class="leitura">{ic("relogio", 16)} {minutos(p["corpo"])} min de leitura</span></div>
</div></header>
{capa}
<div class="estreito texto">
{afil}
{toc}
{corpo}
{share}
<aside class="fontes" aria-label="Fontes"><h2>{ic("livro", 22)} Fontes oficiais consultadas</h2><ul>{fontes}</ul>
<small>Publicado em {data_br(p["data"])}. Última atualização em {data_br(at)}. A informação oficial sempre vale mais: confirme no canal do órgão responsável.</small></aside>
{bloco_autora(r, "h2")}
</div>
</article>
{rel_html}'''
    return pagina(r, f"blog/{p['slug']}/", p["titulo"], p["resumo"], c, "blog", og_img=p.get("capa") or "img/og-padrao.jpg", tipo="article", classe="pg-artigo",
                  extra_head=f'<meta property="article:published_time" content="{p["data"]}"><meta property="article:modified_time" content="{at}"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')

def ferramentas():
    r = "../"
    c = f'''
<section class="pagina-topo"><div class="wrap"><h1>Calculadoras</h1>
<p>Faça a conta antes de decidir. As calculadoras funcionam no seu celular e não guardam nem enviam nenhum dado.</p></div></section>
<section class="secao" style="padding-top:40px"><div class="wrap grade-calcs">
{calc_renda()}
{calc_emprestimo()}
</div></section>'''
    return pagina(r, "ferramentas/", "Calculadoras de renda extra e empréstimo", "Calcule quanto de renda extra você precisa para quitar uma dívida e quanto vai pagar de juros em um empréstimo.", c, "ferramentas")

def achados():
    r = "../"
    grupos = ""
    for cat in dados["categorias"]:
        vs = [v for v in VITRINE if v.get("categoria") == cat["slug"]]
        if vs:
            grupos += f'<div class="bloco-assunto revela"><div class="bloco-topo"><span class="ic cat-{cat["slug"]}">{ic(cat["icone"], 24)}</span><div><h2>{esc(cat["nome"])}</h2></div></div><div class="grade-produtos">{"".join(produto_html(v, r) for v in vs)}</div></div>'
    soltos = [v for v in VITRINE if v.get("categoria") not in CATS]
    if soltos:
        grupos += f'<div class="bloco-assunto revela"><div class="bloco-topo"><span class="ic">{ic("sacola", 24)}</span><div><h2>Outros achados</h2></div></div><div class="grade-produtos">{"".join(produto_html(v, r) for v in soltos)}</div></div>'
    c = f'''
<section class="pagina-topo"><div class="wrap"><h1>Achados</h1>
<p>Produtos que ajudam a economizar no dia a dia ou a começar uma renda extra.</p></div></section>
<section class="secao" style="padding-top:36px"><div class="wrap">
<div class="aviso-afiliado">{ic("info", 20)}<p>{AVISO_AFILIADO}</p></div>
{grupos}
</div></section>'''
    return pagina(r, "achados/", "Achados", "Produtos escolhidos para economizar no dia a dia ou começar uma renda extra.", c, "achados")

def quem_somos():
    r = "../"
    nao = "".join(f'<li>{ic("x", 22)}<span>{t}</span></li>' for t in NAO)
    fontes = "".join(f"<li>{f}</li>" for f in FONTES_OF)
    c = f'''
<section class="pagina-topo"><div class="wrap"><h1>Quem somos</h1>
<p>O Dinheiro Explicado é um veículo de comunicação independente sobre o dinheiro do dia a dia do brasileiro.</p></div></section>
<div class="estreito texto">
<h2 id="o-que-e">O que é o Dinheiro Explicado</h2>
<p>Falamos de benefícios, aposentadoria, FGTS, renda extra, crédito, dívidas, impostos e direitos do trabalhador.</p>
<h2 id="como-apuramos">Como apuramos</h2>
<p>Todo número, data, valor e regra que publicamos vem de fonte oficial:</p>
<ul class="fontes-oficiais">{fontes}</ul>
<p>A fonte é citada e linkada em todo artigo. Quando a informação muda, o artigo muda junto, e cada página mostra a data da última atualização.</p>
<h2 id="como-o-site-se-mantem">Como o site se mantém</h2>
<p>O Dinheiro Explicado é gratuito. Para se manter, alguns artigos e a página de Achados têm <strong>links de afiliado</strong>: se você comprar por eles, a loja paga uma comissão ao site, sem nenhum custo extra para você.</p>
<ul>
<li>Todo artigo com link de afiliado traz um aviso no topo, e cada produto tem o selo "Link de afiliado".</li>
<li>A comissão não muda a informação: regras, valores e datas vêm sempre de fonte oficial.</li>
<li>Só indicamos o que faz sentido para quem quer economizar ou ganhar um dinheiro a mais. Não indicamos "renda fácil" nem nada que peça pagamento para você começar a trabalhar.</li>
</ul>
<h2 id="o-que-nao-fazemos">O que não fazemos</h2>
<ul class="nao-fazemos">{nao}</ul>
<div style="margin:40px 0">{bloco_alerta()}</div>
{bloco_autora(r, "h2")}
</div>'''
    return pagina(r, "quem-somos/", "Quem somos", "Conheça o Dinheiro Explicado: o que fazemos, como apuramos cada informação em fonte oficial, como o site se mantém e o que nunca fazemos.", c, "sobre")

def privacidade():
    r = "../"
    c = f'''
<section class="pagina-topo"><div class="wrap"><h1>Política de privacidade</h1><p>Como o Dinheiro Explicado trata as informações de quem visita o site.</p></div></section>
<div class="estreito texto">
<h2>Não pedimos seus dados</h2>
<p>O Dinheiro Explicado não tem cadastro, não pede CPF, dados bancários, senha ou qualquer pagamento. Se alguém pedir essas informações em nosso nome, é golpe.</p>
<h2>Calculadoras</h2>
<p>As contas das calculadoras são feitas no seu próprio aparelho. Os valores que você digita não são enviados nem guardados.</p>
<h2>O que pode ser coletado</h2>
<p>Como em qualquer site, o servidor de hospedagem pode registrar informações técnicas de acesso, como endereço IP, navegador e páginas visitadas, para segurança e funcionamento do site. Se no futuro usarmos ferramentas de estatística de audiência ou anúncios, esta página será atualizada para dizer quais são e para que servem.</p>
<h2>Links de afiliado</h2>
<p>Alguns links levam a lojas parceiras. Ao clicar, a loja pode usar cookies próprios para saber que você veio do Dinheiro Explicado e calcular a comissão. Nesse caso vale a política de privacidade da loja.</p>
<h2>Links para outros sites</h2>
<p>Nossos artigos trazem links para sites oficiais, como gov.br, INSS, Caixa e Receita Federal. Ao sair do Dinheiro Explicado, vale a política de privacidade do site visitado.</p>
<h2>Seus direitos</h2>
<p>Você tem os direitos previstos na Lei Geral de Proteção de Dados (Lei nº 13.709/2018). Para qualquer dúvida sobre privacidade, fale com a gente pelos canais oficiais do Dinheiro Explicado.</p>
<p><small>Última atualização: {data_br(date.today().isoformat())}.</small></p>
</div>'''
    return pagina(r, "politica-de-privacidade/", "Política de privacidade", "Como o Dinheiro Explicado trata as informações de quem visita o site.", c)

def pagina404():
    r = "/" if not PREVIA else ""
    c = f'''<section class="pagina-topo" style="padding:90px 0"><div class="wrap"><h1>Página não encontrada</h1>
<p>O endereço pode ter mudado. Veja os artigos mais recentes ou volte para o início.</p>
<p style="margin-top:24px" class="acoes"><a class="btn btn-pri" href="{u(r, "blog/")}">Ver os artigos</a> <a class="btn btn-sec" href="{u(r)}">Ir para o início</a></p></div></section>'''
    return pagina(r, "404.html", "Página não encontrada", SITE["descricao"], c).replace('<meta name="description"', '<meta name="robots" content="noindex"><meta name="description"', 1)

# ---------- gravação ----------
def grava(caminho, conteudo):
    destino = os.path.join(SAIDA, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, "w", encoding="utf-8").write(conteudo)

if PREVIA:
    shutil.rmtree(SAIDA, ignore_errors=True)
    for d in ("assets", "img"):
        shutil.copytree(os.path.join(RAIZ, d), os.path.join(SAIDA, d), dirs_exist_ok=True)
    shutil.copy(os.path.join(RAIZ, "favicon.ico"), SAIDA)
else:
    pasta_blog = os.path.join(RAIZ, "blog")
    if os.path.isdir(pasta_blog):
        validos = {p["slug"] for p in POSTS}
        for d in os.listdir(pasta_blog):
            if os.path.isdir(os.path.join(pasta_blog, d)) and d not in validos:
                shutil.rmtree(os.path.join(pasta_blog, d), ignore_errors=True)

grava("index.html", home())
grava("blog/index.html", blog())
grava("ferramentas/index.html", ferramentas())
if TEM_ACHADOS:
    grava("achados/index.html", achados())
grava("quem-somos/index.html", quem_somos())
grava("politica-de-privacidade/index.html", privacidade())
grava("404.html", pagina404())
for p in POSTS:
    grava(f"blog/{p['slug']}/index.html", artigo(p))

if DOM and not PREVIA:
    urls = [("", None), ("blog/", None), ("ferramentas/", None), ("quem-somos/", None), ("politica-de-privacidade/", None)]
    if TEM_ACHADOS: urls.append(("achados/", None))
    urls += [(f"blog/{p['slug']}/", p.get("atualizado") or p["data"]) for p in POSTS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{abs_url(c)}</loc>" + (f"<lastmod>{m}</lastmod>" if m else "") + "</url>\n" for c, m in urls) + "</urlset>\n"
    grava("sitemap.xml", sm)
    grava("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOM}/sitemap.xml\n")

print(f"OK: {len(POSTS)} artigo(s), {len(VITRINE)} achado(s) gerado(s) em {SAIDA}")
