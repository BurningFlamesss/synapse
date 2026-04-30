from pydantic import BaseModel, Field
from tools.base import Tool, ToolInvocation, ToolResult, ToolKind


class EchoToolParams(BaseModel):
    message: str = Field(..., description="The message to echo")


class EchoTool(Tool):
    name = "echo_tool"
    description = (
        "An Echo tool that echoes back the input message."
    )
    kind = ToolKind.READ
    schema = EchoToolParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = EchoToolParams(**invocation.params)
        message = params.message

        output = f"ECHO: {message}\n"

        return ToolResult.success_result(output)
