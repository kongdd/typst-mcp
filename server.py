from mcp.server.fastmcp import FastMCP, Image
import json
import subprocess
import os
import tempfile
import shutil
import hashlib
from PIL import Image as PILImage
import io

temp_dir = tempfile.mkdtemp()

mcp = FastMCP("Demo")

# load the typst docs JSON file
raw_typst_docs = ""
with open("typst-docs/main.json", "r") as f:
    raw_typst_docs = f.read()
typst_docs = json.loads(raw_typst_docs)

@mcp.resource("docs://chapters")
def list_chapters() -> str:
    """
    Lists all chapters in the typst docs.
    The LLM should use this in the beginning to get the list of chapters and then decide which chapter to read.
    """
    print("mcp.resource('docs://chapters') called")
    def list_child_routes(chapter: dict) -> list[dict]:
        """
        Lists all child routes of a chapter.
        """
        if "children" not in chapter:
            return []
        child_routes = [] # { "route": str, content_length: int }[]
        for child in chapter["children"]:
            if "route" in child:
                child_routes.append({
                    "route": child["route"],
                    "content_length": len(json.dumps(child))
                })
            child_routes += list_child_routes(child)
        return child_routes
    chapters = []
    for chapter in typst_docs:
        chapters.append({
            "route": chapter["route"],
            "content_length": len(json.dumps(chapter))
        })
        chapters += list_child_routes(chapter)
    return json.dumps(chapters)

@mcp.resource("docs://chapters/{route}")
def get_chapter(route: str) -> str:
    """
    Gets a chapter by route.
    The route is the path to the chapter in the typst docs.
    For example, the route "____reference____layout____colbreak" corresponds to the chapter "reference/layout/colbreak".
    The route is a string with underscores ("____") instead of slashes (because MCP uses slashes to separate the input parameters).
    """
    print(f"mcp.resource('docs://chapters/{route}') called")

    # the rout could also be in the form of "____reference____layout____colbreak" -> "/reference/layout/colbreak"
    # replace all underscores with slashes
    route = route.replace("____", "/")

    def route_matches(chapter_route: str, input_route: str) -> bool:
        return chapter_route.strip("/") == input_route.strip("/")

    def get_child(chapter: dict, route: str) -> dict:
        """
        Gets a child chapter by route.
        """
        if "children" not in chapter:
            return {}
        for child in chapter["children"]:
            if route_matches(child["route"], route):
                return child
            child = get_child(child, route)
            if child:
                return child
        return {}
    for chapter in typst_docs:
        if route_matches(chapter["route"], route):
            return json.dumps(chapter)
        child = get_child(chapter, route)
        if child:
            return json.dumps(child)
    return json.dumps({})

@mcp.tool()
def latex_to_typst(latex_text) -> str:
    """
    Converts a latex text to typst using pandoc.

    LLMs are way better at writing latex than typst.
    So the LLM should write the wanted output in latex and use this tool to convert it to typst.
    
    If it was not valid latex, the tool returns "ERROR: in latex_to_typst. Failed to convert latex to typst. Error message from pandoc: {error_message}".

    This should be used primarily for converting small snippets of latex to typst but it can also be used for larger snippets.

    Example 1:
    ```latex
    $ f\in K ( t^ { H } , \beta ) _ { \delta } $
    ```
    gets converted to:
    ```typst
    $f in K \( t^H \, beta \)_delta$
    ```

    Example 2:
    ```latex
    \begin{figure}[t]
        \includegraphics[width=8cm]{"placeholder.png"}
        \caption{Placeholder image}
        \label{fig:placeholder}
        \centering
    \end{figure}
    ```
    gets converted to:
    ```typst
    #figure(image("placeholder.png", width: 8cm),
        caption: [
            Placeholder image
        ]
    )
    <fig:placeholder>
    ```
    """
    # create a main.tex file with the latex_text
    with open(os.path.join(temp_dir, "main.tex"), "w") as f:
        f.write(latex_text)

    # run the pandoc command line tool and capture error output
    try:
        result = subprocess.run(
            ["pandoc", os.path.join(temp_dir, "main.tex"), "--from=latex", "--to=typst", "--output", os.path.join(temp_dir, "main.typ")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        return f"ERROR: in latex_to_typst. Failed to convert latex to typst. Error message from pandoc: {error_message}"
    
    # read the typst file
    with open(os.path.join(temp_dir, "main.typ"), "r") as f:
        typst = f.read()
        typst = typst.strip()

    return typst

@mcp.tool()
def check_if_valid_typst_syntax(typst_text) -> str:
    """
    Checks if the given typst text is valid typst syntax.
    Returns "VALID" if it is valid, otherwise returns "INVALID! Error message: {error_message}".
    
    The LLM should use this to check if the typst syntax it generated is valid.
    If not valid, the LLM should try to fix it and check again.
    This should be used primarily for checking small snippets of typst syntax but it can also be used for larger snippets.

    Example 1:
    ```typst
    $f in K \( t^H \, beta \)_delta$
    ```
    returns: VALID

    Example 2:
    ```typst
    $a = \frac{1}{2}$ // not valid typst syntax (\frac is a latex command and not a typst command)
    ```
    returns: INVALID! Error message: {error: unknown variable: rac
        ┌─ temp.typ:1:7
        │
        1 │ $a = \frac{1}{2}$
        │        ^^^
        │
        = hint: if you meant to display multiple letters as is, try adding spaces between each letter: `r a c`
        = hint: or if you meant to display this as text, try placing it in quotes: `"rac"`}
    
    """

    # create a main.typ file with the typst
    with open(os.path.join(temp_dir, "main.typ"), "w") as f:
        f.write(typst_text)
    # run the typst command line tool and capture the result
    try:
        subprocess.run(
            ["typst", "compile", os.path.join(temp_dir, "main.typ")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return "VALID"
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        return f"INVALID! Error message: {error_message}"

# typst compile temp.typ --format png --ppi 500 page{0p}.png -> page1.png, page2.png, etc.
@mcp.tool()
def typst_to_image(typst_text) -> Image | str:
    """
    Converts a typst text to an image using the typst command line tool.

    The LLM should use this to convert typst to an image and then evaluate if the image is what it wanted.
    If not valid, the LLM should try to fix it and check again.
    This should be used primarily for converting small snippets of typst to images but it can also be used for larger snippets.

    Example 1:
    ```typst
    $f in K \( t^H \, beta \)_delta$
    ```
    gets converted to:
    ```image
    <image object>
    ```

    Example 2:
    ```typst
    #figure(image("placeholder.png", width: 8cm),
        caption: [
            Placeholder image
        ]
    )
    <fig:placeholder>
    ```
    gets converted to:
    ```image
    <image object>
    ```

    """
    
    # create a main.typ file with the typst
    with open(os.path.join(temp_dir, "main.typ"), "w") as f:
        f.write(typst_text)
    
    # run the typst command line tool and capture the result
    try:
        subprocess.run(
            ["typst", "compile", os.path.join(temp_dir, "main.typ"), "--format", "png", "--ppi", "500", os.path.join(temp_dir, "page{0p}.png")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        # Find all generated pages
        page_files = []
        page_num = 1
        while os.path.exists(os.path.join(temp_dir, f"page{page_num}.png")):
            page_files.append(os.path.join(temp_dir, f"page{page_num}.png"))
            page_num += 1
        
        if not page_files:
            return "ERROR: in typst_to_image. No pages were generated."
        
        # Load all pages using PIL
        pages = [PILImage.open(page) for page in page_files]
        
        # Calculate total height
        total_width = pages[0].width
        total_height = sum(page.height for page in pages)
        
        # Create a new image with the combined dimensions
        combined_image = PILImage.new('RGB', (total_width, total_height), (255, 255, 255))
        
        # Paste all pages vertically
        y_offset = 0
        for page in pages:
            combined_image.paste(page, (0, y_offset))
            y_offset += page.height
            
        # Save combined image to bytes
        img_bytes_io = io.BytesIO()
        combined_image.save(img_bytes_io, format="PNG")
        img_bytes = img_bytes_io.getvalue()
        
        # Clean up temp files
        os.remove(os.path.join(temp_dir, "main.typ"))
        for page_file in page_files:
            os.remove(page_file)
            
        return Image(data=img_bytes, format="png")
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error"
        return f"ERROR: in typst_to_image. Failed to convert typst to image. Error message from typst: {error_message}"


if __name__ == "__main__":
    # print(json.dumps(list_chapters(), indent=2))
    # print(json.dumps(get_chapter("____reference____layout____colbreak"), indent=2))
    # print(latex_to_typst("$ f\in K ( t^ { H } , \beta ) _ { \delta } $"))
    # img : Image = typst_to_image("$f in K \( t^H \, beta \)_delta$")
    # if isinstance(img, str):
    #     # print(img)
    #     print("Error: ", img)
    # elif img.data is not None:
    #     with open("test.png", "wb") as f:
    #         f.write(img.data)
    pass
