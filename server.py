from mcp.server.fastmcp import FastMCP
import json

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

if __name__ == "__main__":
    print(json.dumps(list_chapters(), indent=2))