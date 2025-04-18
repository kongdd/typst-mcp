# Typst MCP Server

Typst MCP Server is an MCP (Model Context Protocol) implementation that helps AI models interact with Typst, a markup-based typesetting system. The server provides tools for converting between LaTeX and Typst, validating Typst syntax, and generating images from Typst code.

## Available Tools

>⚠️ Currently all the functionality is implemented as `tools`, because Cursor and VS Code are not able to handle the other primitives yet.

The server provides the following tools:

1. **`list_docs_chapters()`**: Lists all chapters in the Typst documentation.
   - Lets the LLM get an overview of the documentation and select a chapter to read.
   - The LLM should select the relevant chapter to read based on the task at hand.

2. **`get_docs_chapter(route)`**: Retrieves a specific chapter from the Typst documentation.
   - Based on the chapter selected by the LLM, this tool retrieves the content of the chapter.

3. **`latex_to_typst(latex_text)`**: Converts LaTeX code to Typst using Pandoc.
   - LLMs are better at writing LaTeX than Typst, so this tool helps convert LaTeX code to Typst.

5. **`check_if_valid_typst_syntax(typst_text)`**: Validates Typst code.
   - Before sending Typst code to the user, the LLM should check if the code is valid.

7. **`typst_to_image(typst_text)`**: Renders Typst code to a PNG image.
   - Before sending complex Typst illustrations to the user, the LLM should render the code to an image and check if it looks correct.
   - Only relevant for multi modal models.

## Getting Started

- Clone this repository
  - `git clone https://github.com/johannesbrandenburger/typst-mcp.git`
- Clone the [typst repository](https://github.com/typst/typst.git)
  - `git clone https://github.com/typst/typst.git`
- Run the docs generation in the typst repository
  - `cargo run --package typst-docs -- --assets-dir ../typst-mcp/typst-docs --out-file ../typst-mcp/typst-docs/main.json`
    - Make sure to adjust the path to your local clone of the typst-mcp repository
    - This will generate the `main.json` and the assets in the `typst-docs` folder
- Install required dependencies: `uv sync`
- Install Typst

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