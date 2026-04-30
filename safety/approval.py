from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any, Callable
from config.config import ApprovalPolicy
from tools.base import ToolConfirmation



class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CONFIRMATION = "needs_confirmation"


@dataclass
class ApprovalContext:

    tool_name: str
    params: dict[str, Any]
    is_mutating: bool
    affected_paths: list[Path]
    command: str | None = None
    is_dangerous: bool = False


DANGEROUS_PATTERNS = [
    r"rm\s+(-rf?|--recursive)\s+[/~]",
    r"rm\s+-rf?\s+\*",
    r"rmdir\s+[/~]",
    r"dd\s+if=",
    r"mkfs",
    r"fdisk",
    r"parted",
    r"shutdown",
    r"reboot",
    r"halt",
    r"poweroff",
    r"init\s+[06]",
    r"chmod\s+(-R\s+)?777\s+[/~]",
    r"chown\s+-R\s+.*\s+[/~]",
    r"nc\s+-l",
    r"netcat\s+-l",
    r"curl\s+.*\|\s*(bash|sh)",
    r"wget\s+.*\|\s*(bash|sh)",
    r":\(\)\s*\{\s*:\|:&\s*\}\s*;",
]

SAFE_PATTERNS = [
    r"^(ls|dir|pwd|cd|echo|cat|head|tail|less|more|wc)(\s|$)",
    r"^(find|locate|which|whereis|file|stat)(\s|$)",
    r"^git\s+(status|log|diff|show|branch|remote|tag)(\s|$)",
    r"^(npm|yarn|pnpm)\s+(list|ls|outdated)(\s|$)",
    r"^pip\s+(list|show|freeze)(\s|$)",
    r"^cargo\s+(tree|search)(\s|$)",
    r"^(grep|awk|sed|cut|sort|uniq|tr|diff|comm)(\s|$)",
    r"^(date|cal|uptime|whoami|id|groups|hostname|uname)(\s|$)",
    r"^(env|printenv|set)$",
    r"^(ps|top|htop|pgrep)(\s|$)",
]


def is_dangerous_command(command: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


def is_safe_command(command: str) -> bool:
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


class ApprovalManager:
    def __init__(self, approval_policy: ApprovalPolicy, cwd: Path, confirmation_callback: Callable[[ToolConfirmation], bool] | None = None) -> None:
        
        self.approval_policy = approval_policy
        self.cwd = cwd
        self.confirmation_callback = confirmation_callback

    def _assess_command_safety(self, command: str) -> ApprovalDecision:
        
        if self.approval_policy == ApprovalPolicy.YOLO:
            return ApprovalDecision.APPROVED

        if is_dangerous_command(command):
            return ApprovalDecision.REJECTED

        if self.approval_policy == ApprovalPolicy.NEVER:
            
            if is_safe_command(command):
                return ApprovalDecision.APPROVED
            
            return ApprovalDecision.REJECTED

        if self.approval_policy in {ApprovalPolicy.AUTO, ApprovalPolicy.ON_FAILURE}:
            return ApprovalDecision.APPROVED

        if self.approval_policy == ApprovalPolicy.AUTO_EDIT:
            
            if is_safe_command(command):
                return ApprovalDecision.APPROVED

            return ApprovalDecision.NEEDS_CONFIRMATION

        # For ON_REQUEST and others, check command safety
        if is_safe_command(command):
            return ApprovalDecision.APPROVED

        return ApprovalDecision.NEEDS_CONFIRMATION

    async def check_approval(self, context: ApprovalContext) -> ApprovalDecision:
        
        if not context.is_mutating:
            return ApprovalDecision.APPROVED

        if context.command:
            
            decision = self._assess_command_safety(context.command)
            
            if decision != ApprovalDecision.NEEDS_CONFIRMATION:
                return decision

        for path in context.affected_paths:
            
            path_decision = ApprovalDecision.NEEDS_CONFIRMATION
            
            if path.is_relative_to(self.cwd):
                path_decision = ApprovalDecision.APPROVED
            else:
                return path_decision

        if context.is_dangerous:
            
            if self.approval_policy == ApprovalPolicy.YOLO:
                return ApprovalDecision.APPROVED
            
            return ApprovalDecision.NEEDS_CONFIRMATION

        if self.approval_policy == ApprovalPolicy.ON_REQUEST:
            return ApprovalDecision.APPROVED # CHANGE IF NECESSARY, it will auto approve all the request if they donot lie under dangerous

        return ApprovalDecision.APPROVED

    def request_confirmation(self, confirmation: ToolConfirmation) -> bool:
        
        if self.confirmation_callback:
            result = self.confirmation_callback(confirmation)
            return result

        return True