# Typst MCP Server

## Getting Started

- clone this repository
  - `git clone https://github.com/johannesbrandenburger/typst-mcp.git`
- clone the [typst repository](https://github.com/typst/typst.git)
  - `git clone https://github.com/typst/typst.git`
- run the docs generation in the typst repository
  - `cargo run --package typst-docs -- --assets-dir ../typst-mcp/typst-docs --out-file ../typst-mcp/typst-docs/main.json`
    - make sure to adjust the path to your local clone of the typst-mcp repository
    - this will generate the `main.json` and the assets in the `typst-docs` folder
