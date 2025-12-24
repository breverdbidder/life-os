"""
Playwright MCP Server - Direct Browser Control via Accessibility Tree
No screenshots. Full DOM/A11y tree access. Real element targeting.

For BidDeed.AI / Lovable.dev QA automation
"""

import asyncio
import json
from typing import Any, Optional
from playwright.async_api import async_playwright, Browser, Page, Locator
from mcp.server import Server
from mcp.types import Tool, TextContent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("playwright-mcp")


class PlaywrightMCPServer:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.server = Server("playwright-browser-control")
        self.checkpoints: list[dict] = []
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="browser_launch",
                    description="Launch browser and navigate to URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to navigate to"},
                            "headless": {"type": "boolean", "default": True}
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="get_page_state",
                    description="Get full page state: DOM tree, accessibility tree, console logs, network errors",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_accessibility_tree",
                    description="Get accessibility tree - structured representation of all interactive elements",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="click",
                    description="Click element by selector, text, or role",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string", "description": "CSS selector, text content, or aria role"},
                            "method": {"type": "string", "enum": ["css", "text", "role", "testid"], "default": "css"}
                        },
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="type_text",
                    description="Type text into focused element or specified selector",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "selector": {"type": "string", "description": "Optional: target element"},
                            "clear_first": {"type": "boolean", "default": False}
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="check_visibility",
                    description="Check if element is visible on page - returns boolean + bounding box",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "selector": {"type": "string"},
                            "method": {"type": "string", "enum": ["css", "text", "role", "testid"], "default": "css"}
                        },
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="get_element_state",
                    description="Get element's current state: value, checked, disabled, visible, text content",
                    inputSchema={
                        "type": "object",
                        "properties": {"selector": {"type": "string"}},
                        "required": ["selector"]
                    }
                ),
                Tool(
                    name="wait_for",
                    description="Wait for element, navigation, or network idle",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["selector", "navigation", "network_idle", "load"]},
                            "value": {"type": "string", "description": "Selector if type=selector"},
                            "timeout": {"type": "integer", "default": 30000}
                        },
                        "required": ["type"]
                    }
                ),
                Tool(
                    name="get_console_logs",
                    description="Get all console logs (errors, warnings, info) from the page",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="create_checkpoint",
                    description="Save current page state as checkpoint for later verification",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "expected_elements": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of selectors that should be visible"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="verify_checkpoint",
                    description="Verify current state against a named checkpoint",
                    inputSchema={
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="run_assertions",
                    description="Run multiple visibility/state assertions at once",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "assertions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "selector": {"type": "string"},
                                        "should_be_visible": {"type": "boolean", "default": True},
                                        "should_contain_text": {"type": "string"},
                                        "should_have_value": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["assertions"]
                    }
                ),
                Tool(
                    name="evaluate_js",
                    description="Execute JavaScript in page context and return result",
                    inputSchema={
                        "type": "object",
                        "properties": {"script": {"type": "string"}},
                        "required": ["script"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                result = await self._handle_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def _handle_tool(self, name: str, args: dict) -> dict:
        handlers = {
            "browser_launch": self._launch,
            "get_page_state": self._get_page_state,
            "get_accessibility_tree": self._get_a11y_tree,
            "click": self._click,
            "type_text": self._type_text,
            "check_visibility": self._check_visibility,
            "get_element_state": self._get_element_state,
            "wait_for": self._wait_for,
            "get_console_logs": self._get_console_logs,
            "create_checkpoint": self._create_checkpoint,
            "verify_checkpoint": self._verify_checkpoint,
            "run_assertions": self._run_assertions,
            "evaluate_js": self._evaluate_js,
        }
        return await handlers[name](args)

    async def _launch(self, args: dict) -> dict:
        pw = await async_playwright().start()
        self.browser = await pw.chromium.launch(headless=args.get("headless", True))
        self.page = await self.browser.new_page()
        
        # Capture console logs
        self._console_logs = []
        self.page.on("console", lambda msg: self._console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        await self.page.goto(args["url"])
        await self.page.wait_for_load_state("networkidle")
        
        return {
            "status": "launched",
            "url": self.page.url,
            "title": await self.page.title()
        }

    async def _get_page_state(self, args: dict) -> dict:
        if not self.page:
            return {"error": "No page open"}
        
        # Get structured DOM representation (not raw HTML)
        dom_summary = await self.page.evaluate("""
            () => {
                const summarize = (el, depth = 0) => {
                    if (depth > 3) return null;
                    const tag = el.tagName?.toLowerCase();
                    if (!tag || ['script', 'style', 'noscript'].includes(tag)) return null;
                    
                    const info = { tag };
                    if (el.id) info.id = el.id;
                    if (el.className) info.class = el.className;
                    if (el.textContent?.trim() && el.children.length === 0) {
                        info.text = el.textContent.trim().slice(0, 100);
                    }
                    if (['input', 'select', 'textarea'].includes(tag)) {
                        info.value = el.value;
                        info.type = el.type;
                    }
                    if (['a', 'button'].includes(tag)) {
                        info.href = el.href;
                        info.disabled = el.disabled;
                    }
                    
                    const children = Array.from(el.children)
                        .map(c => summarize(c, depth + 1))
                        .filter(Boolean);
                    if (children.length) info.children = children;
                    
                    return info;
                };
                return summarize(document.body);
            }
        """)
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "dom": dom_summary,
            "console_errors": [l for l in self._console_logs if l["type"] == "error"]
        }

    async def _get_a11y_tree(self, args: dict) -> dict:
        """Get accessibility tree - the key to non-screenshot based control"""
        if not self.page:
            return {"error": "No page open"}
        
        snapshot = await self.page.accessibility.snapshot()
        return {"accessibility_tree": snapshot}

    async def _get_locator(self, selector: str, method: str) -> Locator:
        if method == "text":
            return self.page.get_by_text(selector)
        elif method == "role":
            # Parse "button:Submit" -> role=button, name=Submit
            parts = selector.split(":", 1)
            role = parts[0]
            name = parts[1] if len(parts) > 1 else None
            return self.page.get_by_role(role, name=name)
        elif method == "testid":
            return self.page.get_by_test_id(selector)
        else:
            return self.page.locator(selector)

    async def _click(self, args: dict) -> dict:
        locator = await self._get_locator(args["selector"], args.get("method", "css"))
        await locator.click()
        return {"clicked": args["selector"], "success": True}

    async def _type_text(self, args: dict) -> dict:
        if args.get("selector"):
            locator = self.page.locator(args["selector"])
            if args.get("clear_first"):
                await locator.clear()
            await locator.type(args["text"])
        else:
            await self.page.keyboard.type(args["text"])
        return {"typed": args["text"], "success": True}

    async def _check_visibility(self, args: dict) -> dict:
        locator = await self._get_locator(args["selector"], args.get("method", "css"))
        is_visible = await locator.is_visible()
        
        result = {"selector": args["selector"], "visible": is_visible}
        if is_visible:
            box = await locator.bounding_box()
            result["bounding_box"] = box
        return result

    async def _get_element_state(self, args: dict) -> dict:
        locator = self.page.locator(args["selector"])
        return {
            "selector": args["selector"],
            "visible": await locator.is_visible(),
            "enabled": await locator.is_enabled(),
            "checked": await locator.is_checked() if await locator.count() > 0 else None,
            "text_content": await locator.text_content(),
            "input_value": await locator.input_value() if await locator.count() > 0 else None
        }

    async def _wait_for(self, args: dict) -> dict:
        timeout = args.get("timeout", 30000)
        wait_type = args["type"]
        
        if wait_type == "selector":
            await self.page.wait_for_selector(args["value"], timeout=timeout)
        elif wait_type == "navigation":
            await self.page.wait_for_url(args.get("value", "**"), timeout=timeout)
        elif wait_type == "network_idle":
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
        elif wait_type == "load":
            await self.page.wait_for_load_state("load", timeout=timeout)
        
        return {"waited_for": wait_type, "success": True}

    async def _get_console_logs(self, args: dict) -> dict:
        return {"logs": self._console_logs}

    async def _create_checkpoint(self, args: dict) -> dict:
        checkpoint = {
            "name": args["name"],
            "url": self.page.url,
            "expected_elements": args.get("expected_elements", []),
            "a11y_snapshot": await self.page.accessibility.snapshot()
        }
        self.checkpoints.append(checkpoint)
        return {"checkpoint_created": args["name"], "index": len(self.checkpoints) - 1}

    async def _verify_checkpoint(self, args: dict) -> dict:
        checkpoint = next((c for c in self.checkpoints if c["name"] == args["name"]), None)
        if not checkpoint:
            return {"error": f"Checkpoint '{args['name']}' not found"}
        
        results = {"checkpoint": args["name"], "passed": True, "failures": []}
        
        for selector in checkpoint["expected_elements"]:
            visible = await self.page.locator(selector).is_visible()
            if not visible:
                results["passed"] = False
                results["failures"].append(f"Element not visible: {selector}")
        
        return results

    async def _run_assertions(self, args: dict) -> dict:
        results = {"total": len(args["assertions"]), "passed": 0, "failed": 0, "details": []}
        
        for assertion in args["assertions"]:
            selector = assertion["selector"]
            locator = self.page.locator(selector)
            detail = {"selector": selector, "passed": True, "checks": []}
            
            if assertion.get("should_be_visible", True):
                visible = await locator.is_visible()
                check = {"type": "visibility", "expected": True, "actual": visible, "passed": visible}
                detail["checks"].append(check)
                if not visible:
                    detail["passed"] = False
            
            if "should_contain_text" in assertion:
                text = await locator.text_content() or ""
                expected = assertion["should_contain_text"]
                passed = expected in text
                detail["checks"].append({"type": "text", "expected": expected, "actual": text[:100], "passed": passed})
                if not passed:
                    detail["passed"] = False
            
            if "should_have_value" in assertion:
                value = await locator.input_value()
                expected = assertion["should_have_value"]
                passed = value == expected
                detail["checks"].append({"type": "value", "expected": expected, "actual": value, "passed": passed})
                if not passed:
                    detail["passed"] = False
            
            results["details"].append(detail)
            if detail["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results

    async def _evaluate_js(self, args: dict) -> dict:
        result = await self.page.evaluate(args["script"])
        return {"result": result}


async def main():
    server = PlaywrightMCPServer()
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.server.run(read, write, server.server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
