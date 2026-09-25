**English** · [Português (Brasil)](README.pt-BR.md)

# citability-lint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)

`citability-lint` is a free, open source command-line tool that audits a
text and flags what keeps a passage from being extracted and cited by
AI search engines: paragraphs outside the ideal length band, paragraphs
that open with a vague pronoun, numeric data without a source in the same
paragraph, and phrases typical of unedited AI-generated text. It runs
entirely on your machine, and no text is sent to any server.

The filler-phrase and vague-pronoun heuristics are specific to Brazilian
Portuguese, and the tool prints its report in Brazilian Portuguese.

## Contents

- [Background](#background)
- [What it checks](#what-it-checks)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [FAQ](#faq)
- [Limitations](#limitations)
- [Methodology](#methodology)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

## Background

Google AI Mode, AI Overviews, Gemini, Perplexity, ChatGPT and Claude do
not read a whole page before they answer. They extract a passage and use
it as the basis of the answer or of the citation. A paragraph that needs
the previous paragraph to make sense, or that drops a number without
saying where it came from, is less likely to become that citation, even
when the text is correct when read from start to finish. `citability-lint`
audits exactly that, paragraph by paragraph.

## What it checks

1. **Paragraph length.** The default band is 40 to 170 words (adjustable
   with `--min-words` and `--max-words`). A paragraph that is too short
   rarely carries a complete idea. One that is too long mixes ideas and
   loses the specific passage.
2. **No vague pronoun at the start.** Portuguese words such as "isso",
   "este" or "ele" opening a paragraph lose their referent when the
   paragraph is extracted on its own.
3. **Numeric data with a source in the same paragraph.** A percentage, a
   thousands figure or "X milhões" without attribution (source, study,
   year) in the same paragraph is not a citable passage, it is a loose
   number.
4. **Filler phrases and AI clichés.** A built-in list of expressions common
   in unedited AI-generated Portuguese text ("é importante notar", "no
   mundo digital em constante evolução", "libere todo o potencial"...),
   which you can extend with your own file.

## Requirements

Python 3.9 or newer. Standard library only, no external dependencies.

## Installation

```bash
git clone https://github.com/LucasFerrazSEO/citability-lint.git
cd citability-lint
```

## Usage

**1. Run the tool on the file you want to audit.**

```bash
python citability_lint.py meu-artigo.html
```

It works with `.html`, `.md` and `.txt`. In HTML, the tool reads the text
inside each `<p>`. In Markdown and plain text, it splits paragraphs on
blank lines.

**2. Read the report.** A real output example (the tool prints its report
in Brazilian Portuguese):

```
=== citability-lint: meu-artigo.html ===
3 parágrafo(s) | OK 2 | ATENÇÃO 4

  ATENÇÃO  parágrafo 1: abre com pronome vago ("isso") — nomear a entidade
  ATENÇÃO  parágrafo 1: muleta/clichê encontrado: hoje em dia
  ATENÇÃO  parágrafo 3: 38 palavras (abaixo de 40)
  ATENÇÃO  parágrafo 3: muleta/clichê encontrado: é importante notar

(Checagem mecânica. Leitura humana e evidência real continuam manuais.)
```

Each ATENÇÃO (warning) line gives the paragraph, the problem and, where it
applies, the exact phrase found.

**3. Adjust the length band** if your editorial format is different.

```bash
python citability_lint.py post.md --min-words 40 --max-words 170
```

**4. Add your own filler phrases.** Create a `.txt` file with one phrase
per line and pass it with `--termos-extra`.

```bash
python citability_lint.py artigo.html --termos-extra minhas-muletas.txt
```

**5. Also catch colloquial Brazilian Portuguese contractions** (`num`,
`numa`, `pra`, `pro`...).

```bash
python citability_lint.py texto.txt --sem-contracoes
```

**6. Use it in CI/CD** to block publishing text that fails the checks.

```bash
python citability_lint.py artigo.html --strict   # código de saída 1 se houver ATENÇÃO
```

With `--strict`, the exit code is 1 when there is any warning. Without it,
the tool only reports.

## FAQ

**Is citability-lint really free?**
Yes. It is open source under the MIT license, with no sign-up and no usage
limit.

**Do I need an internet connection?**
No. The tool only reads the local file you pass to it. No data leaves your
machine.

**Does it work in Portuguese and in other languages?**
The filler-phrase and vague-pronoun heuristics are specific to Brazilian
Portuguese. The paragraph-length check works in any language. The
number-without-source check recognizes attribution only through Portuguese
words (such as "segundo", "fonte", "estudo") and a fixed list of names
(IBGE, Gartner, Semrush and others), so a sourced number in another
language may still be flagged.

**Does the tool guarantee my text will be cited by an AI?**
No, and no tool can guarantee that. `citability-lint` reduces the
mechanical friction that gets in the way of citation. It does not control
what each AI decides to cite.

## Limitations

The filler-phrase and pronoun heuristics cover Brazilian Portuguese only.
False positives happen: a short, direct definition or a quotation may be
fine even outside the length band. Treat the result as a signal, not a
final verdict.

## Methodology

The heuristics come from an internal audit script used since 2026 in the
editorial process of [lucasferrazseo.com](https://lucasferrazseo.com),
generalized here for public use, with no site-specific or CMS-specific
rules.

## Contributing

Bug reports and suggestions are welcome through [GitHub Issues](https://github.com/LucasFerrazSEO/citability-lint/issues).

## Author

[Lucas Ferraz](https://lucasferraz.com) is an SEO, website development and Generative Engine Optimization specialist and the founder of [Lucas Ferraz SEO](https://lucasferrazseo.com).

## License

MIT. See [LICENSE](LICENSE).
