# IEML REPL

A command-line REPL for interacting with the IEML dictionary, powered by the [IEMLdev](https://github.com/IEMLdev/ieml) library.

## Prerequisites

* Python 3.6 or higher
* [ieml](https://github.com/IEMLdev/ieml) library
* Ollama

Install via pip:

```bash
pip install ieml
```

**!!! You need to patch `version.py` for Windows !!!**

The dictionary file is stored with colon in filename which is unsupported on Windows. 

Copy paste `version.py` from this repo's `patch` folder to
 `..\site-packages\ieml\dictionary`

 **Models used:**
```
nomic-embed-text - gloss_embeddings.npz
gemma3 - classification
```
## Installation

Clone this repository and make the script executable:

```bash
git clone <your-repo-url>
cd ieml-repl
chmod +x ieml-repl.py
```

### Embeddings
Embedded IEML dictionary used for candidate selection
```
gloss_embeddings.npz
gloss_embeddings.json
```

They can be generated yourself with your model of choice using `bake_embeddings.py` or downloaded below
[https://3to.moe/ieml/embeddings/](vhttps://3to.moe/ieml/embeddings/)

## Usage

Start the REPL:

```bash
./ieml-repl.py
```

You will see the prompt:

```
IEML REPL 
Type 'help' for commands and 'exit' to quit.
>
```

### Available Commands

* `parse <TERM>`: Validate & show term details
* `neighbors <TERM>`: List semantic neighbours
* `relation <TERM1> <TERM2>`: Check semantic connection
* `search <QUERY>`: Search by English gloss
* `exit`: Quit the REPL

**Example:**

```
> parse A:
Term: [A:]
  Index:        2
  Layer:        0
  English:      actual
  Neighbours: 221

> neighbors s.o.-s.o.-' 
[s.o.-]                         (thought)
[s.o.-s.o.-']                   (mind)
...
```

## Term Normalization

Input codes are normalized using Unicode NFKC, and curly quotes (`‘ ’`) and dashes (`– —`) are converted to ASCII equivalents

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
