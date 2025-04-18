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

## JSON Schema of the Typst Documentation

>⚠️ The schema of the typst documentation is not stable and may change at any time. The schema is generated from the typst source code and is not guaranteed to be complete or correct. Use at your own risk.