#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
citability-lint — checagem mecânica de citabilidade para texto que precisa ser
recortado e citado por buscadores com IA (Google AI Mode/AI Overviews, Gemini,
Perplexity, ChatGPT, Claude).

O QUE FAZ
    Lê um arquivo (.html, .md ou .txt), divide o texto em parágrafos e aplica
    heurísticas de citabilidade a cada um:

    - tamanho do parágrafo dentro de uma banda configurável (padrão: 40-170
      palavras — parágrafo curto demais raramente é citado sozinho; longo
      demais mistura ideias e perde a passagem);
    - abertura sem pronome vago ("isso", "este", "ele"...) — um parágrafo
      recortado sozinho perde o referente se abrir assim;
    - dado numérico (percentual, milhar, "X mil/milhão") sem fonte no mesmo
      parágrafo — passagem citável é dado + atribuição juntos, não separados;
    - frases-muleta e clichê de conteúdo gerado por IA (lista embutida,
      extensível por --termos-extra).

    Não substitui leitura humana nem julgamento editorial. É o passo mecânico
    que pega o que escapa na revisão manual.

MÉTODO
    Heurísticas adaptadas do script de auditoria interno usado em
    lucasferrazseo.com desde 2026, generalizadas para uso público (sem regras
    específicas de um site ou CMS). Contagem de palavras por regex Unicode
    (letras e números), sem dependência de biblioteca de NLP.

USO
    python citability_lint.py artigo.html
    python citability_lint.py post.md --min-words 40 --max-words 170
    python citability_lint.py texto.txt --sem-contracoes
    python citability_lint.py artigo.html --termos-extra minhas-muletas.txt
    python citability_lint.py artigo.html --strict   # código de saída 1 se houver ATENÇÃO

LIMITAÇÕES
    Cobre só o pt-BR. Não avalia veracidade, profundidade ou originalidade do
    conteúdo — só a forma da passagem. Falso positivo existe: parágrafo curto
    de definição ou citação direta pode estar correto mesmo fora da banda.

Autor: Lucas Ferraz (lucasferraz.com) — dependência zero, só biblioteca padrão.
Licença: MIT.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field

PRONOMES_VAGOS = (
    "isso", "isto", "este", "esse", "esta", "essa", "estes", "esses",
    "estas", "essas", "ele", "ela", "eles", "elas", "aqui", "tais", "tal",
    "disso", "disto", "desse", "dessa", "deste", "desta", "nesse", "nessa",
    "neste", "nesta",
)

MULETAS = (
    "é importante notar", "é importante lembrar", "é importante destacar",
    "é importante ressaltar", "vale ressaltar", "vale destacar",
    "cabe destacar", "no que diz respeito a", "quando se trata de",
    "em constante evolução", "em constante mudança",
    "cada vez mais presente", "desvende", "descubra o poder",
    "libere o poder", "libere todo o potencial", "mergulhe no mundo",
    "papel crucial", "papel fundamental", "papel essencial", "peça-chave",
    "não é preciso dizer", "nem é preciso dizer", "desnecessário dizer",
    "sem mais delongas", "em resumo", "em conclusão", "no final do dia",
    "no final das contas", "vivemos em uma era", "no mundo digital",
    "hoje em dia", "com o avanço da tecnologia", "solução definitiva",
    "solução perfeita", "revolucionário", "de última geração",
    "game changer", "num mundo cada vez mais", "em um mundo cada vez mais",
)

CONTRACOES = (r"\bnum\b", r"\bnuma\b", r"\bnuns\b", r"\bnumas\b", r"\bpra\b",
              r"\bpro\b", r"\bpros\b", r"\bdum\b", r"\bduma\b", r"\btá\b")

FONTE_MARCADORES = (
    "segundo ", "de acordo com", "fonte", "estudo", "censo", "pesquisa",
    "levantamento", "relatório", "medição", "medido em", "medida em",
    "aponta", "apontam", "registrad", "divulgad", "publicad", "projeç",
)
FONTE_SIGLAS = re.compile(
    r"\b(ibge|fgv|doi|arxiv|zenodo|gartner|semrush|ahrefs|backlinko|"
    r"statista|sebrae|anvisa|receita federal|gsc|search console)\b"
)
NUMERO_ESTATISTICO = re.compile(
    r"\d+(?:[.,]\d+)?\s*%|\b\d{1,3}(?:\.\d{3})+\b|"
    r"\b\d+(?:,\d+)?\s+(?:mil|milhão|milhões|bilhão|bilhões)\b"
)


def conta_palavras(texto: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+", texto))


def strip_tags(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return re.sub(r"(?s)<[^>]+>", " ", html)


def normaliza(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def primeira_frase(texto: str) -> str:
    texto = normaliza(texto)
    partes = re.split(r"(?<=[.!?])\s", texto, maxsplit=1)
    return partes[0] if partes else texto


def extrai_paragrafos(conteudo: str, formato: str) -> list[str]:
    if formato == "html":
        return [normaliza(strip_tags(p))
                for p in re.findall(r"(?is)<p[^>]*>(.*?)</p>", conteudo)]
    # markdown/texto: parágrafos separados por linha em branco
    blocos = re.split(r"\n\s*\n", conteudo)
    return [normaliza(b) for b in blocos if normaliza(b)]


def detecta_formato(caminho: str) -> str:
    if caminho.lower().endswith((".html", ".htm")):
        return "html"
    return "texto"


@dataclass
class Relatorio:
    ok: list[str] = field(default_factory=list)
    atencao: list[str] = field(default_factory=list)

    def registra_ok(self, msg: str) -> None:
        self.ok.append(msg)

    def registra_atencao(self, msg: str) -> None:
        self.atencao.append(msg)


def linta(paragrafos: list[str], min_w: int, max_w: int,
          checar_contracoes: bool, termos_extra: list[str]) -> Relatorio:
    rel = Relatorio()
    muletas = list(MULETAS) + [t.strip().lower() for t in termos_extra if t.strip()]

    for i, p in enumerate(paragrafos, start=1):
        etiqueta = f"parágrafo {i}"
        baixo = p.lower()
        n = conta_palavras(p)

        if n < min_w:
            rel.registra_atencao(f"{etiqueta}: {n} palavras (abaixo de {min_w})")
        elif n > max_w:
            rel.registra_atencao(f"{etiqueta}: {n} palavras (acima de {max_w}, considerar quebrar)")
        else:
            rel.registra_ok(f"{etiqueta}: {n} palavras (dentro da banda {min_w}-{max_w})")

        primeira = primeira_frase(p).lower()
        primeira_palavra = primeira.split()[0].strip(",.;:") if primeira.split() else ""
        if primeira_palavra in PRONOMES_VAGOS:
            rel.registra_atencao(f"{etiqueta}: abre com pronome vago (\"{primeira_palavra}\") — nomear a entidade")

        achadas = sorted({m for m in muletas if m in baixo})
        if achadas:
            rel.registra_atencao(f"{etiqueta}: muleta/clichê encontrado: " + ", ".join(achadas))

        if checar_contracoes:
            hits = sorted({re.sub(r"\\b", "", c) for c in CONTRACOES if re.search(c, baixo)})
            if hits:
                rel.registra_atencao(f"{etiqueta}: contração coloquial: " + ", ".join(hits))

        limpo = re.sub(r"R\$\s?[\d.,]+", " ", p)
        limpo = re.sub(r"\b(19|20)\d{2}\b", " ", limpo)
        if NUMERO_ESTATISTICO.search(limpo):
            tem_fonte = any(m in baixo for m in FONTE_MARCADORES) or FONTE_SIGLAS.search(baixo)
            if not tem_fonte:
                rel.registra_atencao(f"{etiqueta}: dado numérico sem fonte no mesmo parágrafo")

    return rel


def main() -> None:
    ap = argparse.ArgumentParser(description="Checagem mecânica de citabilidade de texto.")
    ap.add_argument("arquivo", help="arquivo .html, .md ou .txt")
    ap.add_argument("--min-words", type=int, default=40, help="mínimo de palavras por parágrafo (padrão 40)")
    ap.add_argument("--max-words", type=int, default=170, help="máximo de palavras por parágrafo (padrão 170)")
    ap.add_argument("--sem-contracoes", action="store_true",
                     help="também checa contrações coloquiais em pt-BR (num, pra, pro...)")
    ap.add_argument("--termos-extra", default="",
                     help="arquivo .txt com uma muleta/clichê extra por linha")
    ap.add_argument("--strict", action="store_true",
                     help="código de saída 1 se houver qualquer ATENÇÃO (padrão: só relata)")
    args = ap.parse_args()

    try:
        with open(args.arquivo, encoding="utf-8") as fh:
            conteudo = fh.read()
    except OSError as exc:
        print(f"Não consegui ler {args.arquivo}: {exc}", file=sys.stderr)
        sys.exit(2)

    termos_extra: list[str] = []
    if args.termos_extra:
        with open(args.termos_extra, encoding="utf-8") as fh:
            termos_extra = fh.readlines()

    formato = detecta_formato(args.arquivo)
    paragrafos = extrai_paragrafos(conteudo, formato)
    if not paragrafos:
        print("Nenhum parágrafo encontrado no arquivo.", file=sys.stderr)
        sys.exit(2)

    relatorio = linta(paragrafos, args.min_words, args.max_words,
                       args.sem_contracoes, termos_extra)

    print(f"\n=== citability-lint: {args.arquivo} ===")
    print(f"{len(paragrafos)} parágrafo(s) | OK {len(relatorio.ok)} | ATENÇÃO {len(relatorio.atencao)}\n")
    for m in relatorio.atencao:
        print("  ATENÇÃO  " + m)
    if not relatorio.atencao:
        print("  Nenhum ponto de atenção nas checagens mecânicas.")
    print("\n(Checagem mecânica. Leitura humana e evidência real continuam manuais.)")

    sys.exit(1 if (args.strict and relatorio.atencao) else 0)


if __name__ == "__main__":
    main()
