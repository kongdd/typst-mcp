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

if __name__ == "__main__":
    # print(json.dumps(list_chapters(), indent=2))
    # print(json.dumps(get_chapter("____reference____layout____colbreak"), indent=2))