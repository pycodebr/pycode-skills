"""Revisão mecânica de texto em PT-BR: acentuação esquecida, pontuação de efeito e vícios de texto gerado por IA.

A checagem ajuda, mas não substitui a leitura. Código, URLs e trechos entre crases são ignorados.
"""
import html
import json
import re
from pathlib import Path

# palavras que quase sempre indicam acento esquecido quando aparecem sem ele
UNACCENTED = {
    "nao": "não", "voce": "você", "voces": "vocês", "tambem": "também", "alem": "além", "atraves": "através",
    "entao": "então", "sao": "são", "estao": "estão", "serao": "serão", "ninguem": "ninguém", "alguem": "alguém",
    "porem": "porém", "apos": "após", "atras": "atrás", "tres": "três", "portugues": "português", "ingles": "inglês",
    "codigo": "código", "codigos": "códigos", "pagina": "página", "paginas": "páginas", "proximo": "próximo",
    "proxima": "próxima", "ultimo": "último", "ultima": "última", "numero": "número", "numeros": "números",
    "unico": "único", "unica": "única", "facil": "fácil", "dificil": "difícil", "rapido": "rápido", "rapida": "rápida",
    "possivel": "possível", "disponivel": "disponível", "util": "útil", "video": "vídeo", "videos": "vídeos",
    "audio": "áudio", "conteudo": "conteúdo", "conteudos": "conteúdos", "modulo": "módulo", "modulos": "módulos",
    "topico": "tópico", "topicos": "tópicos", "analise": "análise", "tecnico": "técnico", "tecnica": "técnica",
    "basico": "básico", "basica": "básica", "logica": "lógica", "memoria": "memória", "historia": "história",
    "experiencia": "experiência", "referencia": "referência", "referencias": "referências", "sequencia": "sequência",
    "ciencia": "ciência", "inteligencia": "inteligência", "negocio": "negócio", "negocios": "negócios",
    "usuario": "usuário", "usuarios": "usuários", "necessario": "necessário", "comentario": "comentário",
    "comentarios": "comentários", "relatorio": "relatório", "repositorio": "repositório", "diretorio": "diretório",
    "formulario": "formulário", "calendario": "calendário", "exercicio": "exercício", "exercicios": "exercícios",
    "inicio": "início", "servico": "serviço", "servicos": "serviços", "preco": "preço", "precos": "preços",
    "comeco": "começo", "licao": "lição", "opcao": "opção", "opcoes": "opções", "acao": "ação", "acoes": "ações",
    "decisao": "decisão", "visao": "visão", "conclusao": "conclusão", "introducao": "introdução",
    "descricao": "descrição", "atencao": "atenção", "criacao": "criação", "educacao": "educação",
    "programacao": "programação", "integracao": "integração", "publicacao": "publicação", "navegacao": "navegação",
    "animacao": "animação", "animacoes": "animações", "transicao": "transição", "selecao": "seleção",
    "edicao": "edição", "revisao": "revisão", "versao": "versão", "sessao": "sessão", "botao": "botão",
    "padrao": "padrão", "funcao": "função", "funcoes": "funções", "informacao": "informação",
    "informacoes": "informações", "solucao": "solução", "producao": "produção", "configuracao": "configuração",
    "instalacao": "instalação", "aplicacao": "aplicação", "apresentacao": "apresentação", "automacao": "automação",
    "operacao": "operação", "carrossel": None, "carrosseis": "carrosséis", "icone": "ícone", "titulo": "título",
    "titulos": "títulos", "subtitulo": "subtítulo", "paragrafo": "parágrafo", "grafico": "gráfico",
    "graficos": "gráficos", "codificacao": "codificação", "responsavel": "responsável", "voce": "você",
}
UNACCENTED = {k: v for k, v in UNACCENTED.items() if v}

# chaves de JSON que guardam identificadores, não texto para leitura
ID_KEYS = {"id", "ids", "slug", "archetype", "group", "script", "file", "key", "layout", "style", "fonts", "font", "example", "after", "before"}

AI_PATTERNS = [
    (r"\bn[ãa]o é (?:apenas |só |somente |sobre )?[^.!?;:\n]{2,60}[.;,] ?(?:é|mas sim|e sim)\b", "antítese de fórmula (\"não é X, é Y\"): diga direto o que é"),
    (r"\bresultado\? ", "pergunta de efeito (\"Resultado?\")"),
    (r"\b(?:e )?é aqui que (?:o jogo muda|entra|tudo muda)", "antecipação dramática"),
    (r"\ba verdade é que\b", "antecipação vazia (\"a verdade é que\")"),
    (r"\bo segredo (?:é|está)\b", "preparação dramática (\"o segredo é\")"),
    (r"\bno mundo (?:de hoje|atual|cada vez mais)\b", "abertura genérica"),
    (r"\b(?:em um|num) cenário cada vez mais\b", "abertura genérica"),
    (r"\bvamos mergulhar\b|\bmergulhe (?:no|na|em)\b", "clichê (\"mergulhar\")"),
    (r"\bgame[- ]changer\b", "clichê (\"game changer\")"),
    (r"\bdesbloque(?:ar|ie|ando)\b|\bdestrav(?:ar|e|ando)\b", "clichê (\"desbloquear/destravar\")"),
    (r"\brevolucion(?:e|ar|ário|ária)\b", "adjetivo sem demonstração (\"revolucionário\")"),
    (r"\beleve (?:seu|sua|seus|suas)\b|\bleve (?:seu|sua) \w+ (?:para o|ao) próximo nível\b", "clichê de anúncio"),
    (r"\bespero que (?:isso )?ajude\b|\baqui está\b|\bcomo (?:um modelo|uma IA)\b", "resíduo de chatbot"),
]


def extract(path):
    """Texto legível de .html, .md, .json ou .txt, sem código nem URLs."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in (".html", ".htm", ".svg"):
        raw = re.sub(r"(?is)<(script|style|code|pre|template)\b.*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
        attrs = re.findall(r'(?:alt|title|aria-label|content|placeholder)="([^"]*)"', raw)
        raw = re.sub(r"(?s)<[^>]+>", "\n", raw) + "\n" + "\n".join(attrs)
        raw = html.unescape(raw)
    elif suffix == ".json":
        def walk(node):
            if isinstance(node, str):
                yield node
            elif isinstance(node, dict):
                for k, v in node.items():
                    if k in ID_KEYS and isinstance(v, (str, list)):
                        continue
                    yield from walk(v)
            elif isinstance(node, list):
                for v in node:
                    yield from walk(v)
        raw = "\n".join(walk(json.loads(raw)))
    elif suffix == ".md":
        # no frontmatter, `name:` é identificador (igual ao nome da pasta) e não prosa
        raw = re.sub(r"\A---\n(.*?)\n---\n", lambda m: re.sub(r"(?m)^name:.*$", "", m.group(0)), raw, count=1, flags=re.S)
    return clean(raw)


def clean(text):
    text = re.sub(r"(?s)```.*?```", " ", text)
    text = re.sub(r"`[^`\n]*`", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+|\S+@\S+\.\S+", " ", text)
    text = re.sub(r"[\w./-]+\.(?:py|js|css|html|json|md|sh|png|jpg|webp|svg|woff2)\b", " ", text)
    return text


def lint(text, allow_dash=False):
    """Devolve lista de (nível, mensagem, trecho). Níveis: erro, aviso."""
    issues = []
    lowered = text.lower()
    for m in re.finditer(r"[a-zà-ÿ0-9_]+(?:-[a-zà-ÿ0-9_]+)*", lowered):
        word = m.group(0)
        if "-" in word or "_" in word:
            continue  # identificador composto (nome de skill, slug, variável), não prosa
        if word in UNACCENTED:
            issues.append(("erro", f"acento esquecido: \"{word}\" → \"{UNACCENTED[word]}\"", _ctx(text, m.start())))
    letters = len(re.findall(r"[a-zA-Z]", text))
    accents = len(re.findall(r"[áéíóúâêôãõçàÁÉÍÓÚÂÊÔÃÕÇÀ]", text))
    if letters > 400 and accents == 0:
        issues.append(("erro", "texto longo sem nenhum acento: confira se a acentuação PT-BR foi perdida", ""))
    if not allow_dash:
        for m in re.finditer(r"—| – ", text):
            issues.append(("aviso", "travessão como pontuação: prefira vírgula, dois-pontos ou outra frase", _ctx(text, m.start())))
    for m in re.finditer(r"\.{3,}|…", text):
        issues.append(("aviso", "reticências de suspense", _ctx(text, m.start())))
    for m in re.finditer(r"!{2,}|\?{2,}|\?!|!\?", text):
        issues.append(("aviso", "pontuação empilhada", _ctx(text, m.start())))
    for pattern, label in AI_PATTERNS:
        for m in re.finditer(pattern, lowered):
            issues.append(("aviso", label, _ctx(text, m.start())))
    return issues


def _ctx(text, pos, span=38):
    return re.sub(r"\s+", " ", text[max(0, pos - span):pos + span]).strip()


def words(text):
    return len(re.findall(r"[\wÀ-ÿ]+(?:[-'][\wÀ-ÿ]+)*", text))
