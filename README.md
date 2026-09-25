# citability-lint — ferramenta grátis e de código aberto de checagem de citabilidade de texto

`citability-lint` é uma ferramenta gratuita, de código aberto, que audita um
texto e aponta o que atrapalha uma passagem de ser recortada e citada por
buscadores com IA: parágrafo fora da banda de tamanho ideal, abertura com
pronome vago, dado numérico sem fonte no mesmo parágrafo e clichês típicos
de texto gerado por IA sem revisão. Roda inteiramente na sua máquina, via
linha de comando — nenhum texto é enviado para servidor nenhum.

## O que é citabilidade e por que auditar

Um Google AI Mode, um AI Overview, o Gemini, a Perplexity, o ChatGPT ou o
Claude não leem a página inteira antes de responder: recortam um trecho e
usam esse trecho como base da resposta ou da citação. Um parágrafo que
depende do parágrafo anterior para fazer sentido, ou que solta um número
sem dizer de onde veio, tem menos chance de virar essa citação — mesmo que
o texto, lido do início ao fim, esteja correto. `citability-lint` audita
exatamente essa característica, parágrafo por parágrafo.

## O que a ferramenta verifica

1. **Tamanho do parágrafo** — banda padrão de 40 a 170 palavras (ajustável
   por `--min-words`/`--max-words`). Parágrafo curto demais raramente
   carrega uma ideia completa; parágrafo longo demais mistura ideias e
   perde a passagem específica.
2. **Abertura sem pronome vago** — "isso", "este", "ele" e afins abrindo um
   parágrafo perdem o referente quando o parágrafo é recortado sozinho.
3. **Dado numérico com fonte no mesmo parágrafo** — percentual, milhar ou
   "X milhões" sem atribuição (fonte, estudo, ano) no mesmo parágrafo não é
   uma passagem citável, é um número solto.
4. **Muletas e clichês de IA** — lista embutida de expressões comuns em
   texto gerado por IA sem revisão ("é importante notar", "no mundo digital
   em constante evolução", "libere todo o potencial"...), extensível por
   arquivo próprio.

## Instalação

Só biblioteca padrão do Python (3.9 ou mais recente). Sem dependência
externa nenhuma para instalar.

```bash
git clone https://github.com/lucasferrazseo/citability-lint.git
cd citability-lint
```

## Como usar, passo a passo

**1. Rode a ferramenta apontando para o arquivo que quer auditar.**

```bash
python citability_lint.py meu-artigo.html
```

Funciona com `.html`, `.md` ou `.txt`. Em HTML, a ferramenta lê o texto de
dentro de cada `<p>`; em markdown e texto puro, divide por linha em branco.

**2. Leia o relatório.** Um exemplo de saída real:

```
=== citability-lint: meu-artigo.html ===
3 parágrafo(s) | OK 2 | ATENÇÃO 4

  ATENÇÃO  parágrafo 1: abre com pronome vago ("isso") — nomear a entidade
  ATENÇÃO  parágrafo 1: muleta/clichê encontrado: hoje em dia
  ATENÇÃO  parágrafo 3: 38 palavras (abaixo de 40)
  ATENÇÃO  parágrafo 3: muleta/clichê encontrado: é importante notar

(Checagem mecânica. Leitura humana e evidência real continuam manuais.)
```

Cada linha de ATENÇÃO diz o parágrafo, o problema e, quando cabe, o trecho
exato encontrado.

**3. Ajuste a banda de tamanho, se seu formato editorial for diferente.**

```bash
python citability_lint.py post.md --min-words 40 --max-words 170
```

**4. Adicione suas próprias muletas.** Crie um `.txt` com uma expressão por
linha e aponte com `--termos-extra`:

```bash
python citability_lint.py artigo.html --termos-extra minhas-muletas.txt
```

**5. Também quer pegar contração coloquial em pt-BR** (num, numa, pra,
pro...)?

```bash
python citability_lint.py texto.txt --sem-contracoes
```

**6. Use em CI/CD**, bloqueando publicação de texto fora do padrão:

```bash
python citability_lint.py artigo.html --strict   # código de saída 1 se houver ATENÇÃO
```

## Perguntas frequentes

**citability-lint é realmente grátis?**
Sim, código aberto sob licença MIT, sem cadastro, sem limite de uso.

**Preciso de internet para usar?**
Não. A ferramenta só lê o arquivo local que você passar; nenhum dado sai
da sua máquina.

**Funciona em português e em outro idioma?**
As heurísticas de muleta e pronome vago são específicas de português
brasileiro. Tamanho de parágrafo e checagem de dado-com-fonte funcionam em
qualquer idioma.

**A ferramenta garante que meu texto vai ser citado por uma IA?**
Não, e nenhuma ferramenta garante isso. `citability-lint` reduz o atrito
mecânico que atrapalha a citação; não controla o que cada IA decide citar.

## Limitações

Cobre só português brasileiro nas heurísticas de muleta e pronome. Falso
positivo existe: um parágrafo curto de definição direta ou uma citação
entre aspas pode estar correto mesmo fora da banda de tamanho. Trate o
resultado como sinal, não como veredito final.

## Método e origem

As heurísticas vêm de um script de auditoria interno usado desde 2026 no
processo editorial de [lucasferrazseo.com](https://lucasferrazseo.com),
generalizado aqui para uso público, sem nenhuma regra específica de site ou
CMS.

## Autor

[Lucas Ferraz](https://lucasferraz.com) — especialista em SEO, criação de
sites e SEO para IA, fundador da [Lucas Ferraz SEO](https://lucasferrazseo.com).

## Licença

MIT — ver [LICENSE](LICENSE).
