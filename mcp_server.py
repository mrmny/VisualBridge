# MCP (Model Context Protocol) szerver szimuláció a VisualBridge projekthez
# Model Context Protocol (MCP) Server for VisualBridge
import os
import sys

# A helyi importok helyes működésének biztosítása, ha más könyvtárakból futtatják
# Ensure local imports work correctly when run from other directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from skills import fetch_pictogram_by_keyword, generate_non_verbal_quiz

# FastMCP szerver indítása
# Initialize FastMCP Server
mcp = FastMCP("VisualBridge MCP Server")

@mcp.tool()
def fetch_pictogram(keyword: str, locale: str = "hu") -> dict:
    """
    HU:
    ARASAAC API-ból keres piktogramot a megadott kulcsszóra és nyelvi lokalizációra (hu vagy en).

    Args:
        keyword (str): A keresett piktogram kulcsszava.
        locale (str): A nyelvi lokalizáció ('hu' vagy 'en').
    EN:
    Fetch pictogram details (success status, word, and image URL) from the ARASAAC API
    for a given keyword and language locale (hu or en).

    Args:
        keyword (str): The term or concept to find a pictogram for.
        locale (str): The language locale ('hu' for Hungarian, 'en' for English).
    """
    # TISZTÍTÁS
    # Clean inputs
    keyword = keyword.strip()
    locale = locale.strip().lower()
    return fetch_pictogram_by_keyword(keyword, locale)

@mcp.tool()
def generate_quiz(correct_word: str, distractor_1: str, distractor_2: str, locale: str = "hu") -> dict:
    """
    HU:
    Generál egy 3 válaszos vizuális kvízt egy kérdéssel és opciókkal (tartalmazza a kép URL-eket és a helyességi zászlókat).

    Args:
        correct_word (str): A helyes válasz kulcsszava.
        distractor_1 (str): Az első rossz válasz (distractor).
        distractor_2 (str): A második rossz válasz (distractor).
        locale (str): A nyelvi lokalizáció ('hu' vagy 'en').

    EN:
    Generate a 3-option visual quiz with a question and options (containing image URLs and correctness flags).

    Args:
        correct_word (str): The correct answer keyword.
        distractor_1 (str): The first wrong answer (distractor).
        distractor_2 (str): The second wrong answer (distractor).
        locale (str): The language locale ('hu' or 'en').
    """
    correct_word = correct_word.strip()
    distractor_1 = distractor_1.strip()
    distractor_2 = distractor_2.strip()
    locale = locale.strip().lower()

    return generate_non_verbal_quiz(correct_word, [distractor_1, distractor_2], locale)

if __name__ == "__main__":
    # MCP szerver indítása stdio transzporton keresztül
    # Start the MCP server using standard input/output (stdio) transport
    mcp.run(transport="stdio")
