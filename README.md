# Typst MCP Server

Typst MCP Server is an MCP (Model Context Protocol) implementation that helps AI models interact with Typst, a markup-based typesetting system. The server provides tools for converting between LaTeX and Typst, validating Typst syntax, and generating images from Typst code.

## Getting Started

- Clone this repository
  - `git clone https://github.com/johannesbrandenburger/typst-mcp.git`
- Clone the [typst repository](https://github.com/typst/typst.git)
  - `git clone https://github.com/typst/typst.git`
- Run the docs generation in the typst repository
  - `cargo run --package typst-docs -- --assets-dir ../typst-mcp/typst-docs --out-file ../typst-mcp/typst-docs/main.json`
    - Make sure to adjust the path to your local clone of the typst-mcp repository
    - This will generate the `main.json` and the assets in the `typst-docs` folder
- Install required dependencies:
  - Python MCP SDK: `pip install mcp`
  - Typst: Install according to [official instructions](https://github.com/typst/typst#installation)
  - Pandoc: Install according to [official instructions](https://pandoc.org/installing.html)
  - Python libraries: `pip install pillow numpy`

## Available Tools

The server provides the following tools:

1. **`list_docs_chapters()`**: Lists all chapters in the Typst documentation.
   - Useful for exploring available documentation before diving in.

2. **`get_docs_chapter(route)`**: Retrieves a specific chapter from the Typst documentation.
   - Accepts routes like "____reference____layout____colbreak" (corresponds to "/reference/layout/colbreak").

3. **`latex_to_typst(latex_text)`**: Converts LaTeX code to Typst using Pandoc.
   - Helpful for translating familiar LaTeX syntax to Typst's equivalent.

4. **`check_if_valid_typst_syntax(typst_text)`**: Validates Typst code.
   - Returns "VALID" if the syntax is correct, or an error message if not.

5. **`typst_to_image(typst_text)`**: Renders Typst code to a PNG image.
   - Creates a visual representation of the Typst code output.

## Usage Examples

### Converting LaTeX to Typst

```python
result = latex_to_typst(r"$f\in K ( t^ { H } , \beta ) _ { \delta }$")
# Returns: "$f in K \( t^H \, beta \)_delta$"
```

### Validating Typst Syntax

```python
result = check_if_valid_typst_syntax("$f in K \( t^H \, beta \)_delta$")
# Returns: "VALID"
```

### Rendering Typst to Image

```python
image = typst_to_image("#set page(width: 10cm, height: auto)\n$f in K \( t^H \, beta \)_delta$")
# Returns: Image object with rendered PNG content
```

### Accessing Typst Documentation

```python
chapters = list_docs_chapters()
# Returns: JSON list of all available chapters

chapter = get_docs_chapter("____reference____layout____colbreak")
# Returns: JSON content of the specific chapter
```

## Running the Server

Execute the server script:

```bash
python server.py
```

Or install it in Claude Desktop with MCP:

```bash
mcp install server.py --name "Typst MCP"
```

## JSON Schema of the Typst Documentation

>⚠️ The schema of the typst documentation is not stable and may change at any time. The schema is generated from the typst source code and is not guaranteed to be complete or correct. Use at your own risk.