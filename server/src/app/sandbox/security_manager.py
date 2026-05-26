"""Centralized security manager for sandboxed Python execution."""

from __future__ import annotations

import builtins
import importlib
import logging
import os
import sys
from collections.abc import Callable  # typing.List 대신 내장 list 사용을 위한 빌드업
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, Type  # noqa: UP035

from .utils import (
    DEFAULT_ALLOWED_EXTENSIONS,
    MAX_RAW_WRITE_SIZE,
    check_write_size_limit,
    create_temp_file,
    is_allowed_file_type,
    validate_path,
)

logger = logging.getLogger(__name__)

# --- Configuration & State ---

class SecurityPolicy:
    """Defines the security policies for the sandbox."""
    # List 대신 python 3.9+ 표준 규격인 list 로 가드
    FORBIDDEN_PATH_PATTERNS: list[str] = [
        "/var/", "/root/", "/proc", "/sys", 
        "~/", "../"
    ]
    ALLOWED_SYSTEM_PREFIXES: list[str] = [
        "/usr/", "/lib/", "/bin/", "/sbin/", 
        "/dev/null"
    ]
    READ_ONLY_MODE: bool = os.getenv("SANDBOX_READ_ONLY", "false").lower() == "true"
    STRICT_MODE: bool = os.getenv("SANDBOX_STRICT_MODE", "false").lower() == "true"
    DEBUG_VERBOSE: bool = os.getenv("SANDBOX_DEBUG_VERBOSE", "false").lower() == "true"
    USER_ROOT: Path = Path(os.getcwd()).resolve()

    def _log_event(self, message: str, level: int = logging.DEBUG) -> None:
        if self.DEBUG_VERBOSE or level >= logging.WARNING:
            logger.log(level, f"[SANDBOX_SECURITY] {message}")

    def is_path_forbidden(self, target_path: str, context: str) -> bool:
        if any(p in target_path for p in self.FORBIDDEN_PATH_PATTERNS):
            self._log_event(
                f"AUDIT WARNING: Forbidden pattern '{target_path}' detected in {context}.",
                level=logging.WARNING
            )
            return True
        return False

    def check_path_access(self, file_path: str, context: str, write_attempt: bool = False) -> None:
        if self.READ_ONLY_MODE and write_attempt:
            raise PermissionError(f"Sandbox: Write access is DISABLED (Read-Only mode): {file_path}")

        if self.is_path_forbidden(file_path, context):
             if self.STRICT_MODE:
                raise PermissionError(f"Sandbox: Access to forbidden path is DENIED in strict mode: {file_path}")

        try:
            validated_path = validate_path(file_path, self.USER_ROOT)
            if validated_path != Path(file_path).resolve() and not any(
                validated_path.as_posix().startswith(p) for p in self.ALLOWED_SYSTEM_PREFIXES
            ):
                if self.STRICT_MODE:
                    raise PermissionError(f"Sandbox: Access to external path is DENIED in strict mode: {file_path}")
        except ValueError as e:
            raise PermissionError(f"Sandbox: Invalid path detected: {file_path}") from e


class SecurityManager:
    """Manages the application of security policies by patching built-ins and modules."""
    _policy: SecurityPolicy
    _original_open: Callable = builtins.open
    _original_os_system: Callable[[str], int] | None = None
    _original_os_popen: Callable[..., Any] | None = None
    _original_subprocess_popen: Type[Any] | None = None
    _original_socket_class: Type[Any] | None = None  # 소켓 클래스 원본 백업용 레이어 확장
    _original_requests_request: Callable[..., Any] | None = None
    _is_active: bool = False

    def __init__(self, policy: Optional[SecurityPolicy] = None) -> None:
        self._policy = policy or SecurityPolicy()

    def _log_debug(self, message: str) -> None:
        if self._policy.DEBUG_VERBOSE:
            logger.debug(f"[SECURITY_MANAGER] {message}")

    def _log_security_alert(self, message: str, level: int = logging.ERROR) -> None:
        logger.log(level, f"[SECURITY_MANAGER] {message}")

    def _secure_open(self, file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        path_str = str(file)
        write_attempt = any(m in mode for m in ["w", "a", "+", "x"])
        self._policy.check_path_access(path_str, "file open", write_attempt)

        if not is_allowed_file_type(path_str, DEFAULT_ALLOWED_EXTENSIONS):
            self._log_security_alert(f"Blocked access to disallowed file type: {path_str}", logging.WARNING)
            if self._policy.STRICT_MODE:
                raise PermissionError(f"Sandbox: Access to disallowed file type is DENIED: {path_str}")

        return self._original_open(file, mode, *args, **kwargs)

    def _secure_os_system(self, command: str) -> int:
        self._policy.check_path_access(command, "os.system command", write_attempt=True)
        return self._original_os_system(command) if self._original_os_system else os.system(command)

    def _secure_os_popen(self, *args: Any, **kwargs: Any) -> Any:
        command = args[0] if args else kwargs.get("command", "unknown")
        self._policy.check_path_access(str(command), "os.popen command", write_attempt=True)
        return self._original_os_popen(*args, **kwargs) if self._original_os_popen else os.popen(command)

    def _block_os_dangerous_function(self, func_name: str) -> Callable[..., None]:
        def blocked_func(*args: Any, **kwargs: Any) -> None:
            raise PermissionError(f"Sandbox: os.{func_name} is DISABLED")
        return blocked_func

    def _secure_subprocess_popen(self, *args: Any, **kwargs: Any) -> Any:
        command_args = args[0] if args else kwargs.get("args", "unknown")
        command_str = str(command_args)
        self._policy.check_path_access(command_str, "subprocess.Popen command", write_attempt=True)
        return self._original_subprocess_popen(*args, **kwargs)

    def _patch_builtins_and_os(self) -> None:
        builtins.open = self._secure_open
        if hasattr(os, "system") and not self._original_os_system:
            self._original_os_system = os.system
            os.system = self._secure_os_system
        if hasattr(os, "popen") and not self._original_os_popen:
            self._original_os_popen = os.popen
            os.popen = self._secure_os_popen
        
        for dangerous_func in ["spawnl", "spawnv", "execl", "execv", "fork", "forkpty", "execvpe"]:
            if hasattr(os, dangerous_func):
                setattr(os, dangerous_func, self._block_os_dangerous_function(dangerous_func))

    def _patch_subprocess(self, subprocess_module: ModuleType) -> None:
        if hasattr(subprocess_module, "Popen") and not self._original_subprocess_popen:
            self._original_subprocess_popen = subprocess_module.Popen
            subprocess_module.Popen = self._secure_subprocess_popen

    def _patch_socket(self, socket_module: ModuleType) -> None:
        """Patch socket to enforce network access policy."""
        if hasattr(socket_module, "socket") and not self._original_socket_class:
            self._original_socket_class = socket_module.socket
            origin_class = self._original_socket_class
            policy = self._policy

            class SecureSocket(origin_class):  # type: ignore
                def connect(self, address: Any) -> Any:
                    if len(address) >= 2:
                        host = str(address[0])
                        policy.check_path_access(host, "socket connect")

                    return super().connect(address)

            socket_module.socket = SecureSocket

    def _patch_requests(self, requests_module: ModuleType) -> None:
        if hasattr(requests_module, "api") and hasattr(requests_module.api, "request") and not self._original_requests_request:  # noqa: E501
            self._original_requests_request = requests_module.api.request
            requests_module.api.request = self._secure_requests_request

    def _secure_requests_request(self, method: str, url: str, **kwargs: Any) -> Any:
        self._log_debug(f"Auditing requests.{method} to {url}")
        return self._original_requests_request(method, url, **kwargs)

    def install_security_hooks(self) -> None:
        if self._is_active:
            return

        self._patch_builtins_and_os()
        sys.meta_path.insert(0, _SecurityImportFinder(self))

        for mod_name, patch_func in {
            "subprocess": self._patch_subprocess,
            "socket": self._patch_socket,
            "requests": self._patch_requests,
        }.items():
            if mod_name in sys.modules:
                patch_func(sys.modules[mod_name]) # type: ignore

        self._is_active = True
        self._log_debug("Security Manager ACTIVATED.")

    def uninstall_security_hooks(self) -> None:
        if not self._is_active:
            return

        builtins.open = self._original_open
        if self._original_os_system:
            os.system = self._original_os_system
            self._original_os_system = None
        if self._original_os_popen:
            os.popen = self._original_os_popen
            self._original_os_popen = None
        
        if self._original_subprocess_popen:
            if "subprocess" in sys.modules:
                sys.modules["subprocess"].Popen = self._original_subprocess_popen
            self._original_subprocess_popen = None
        
        if self._original_socket_class:
            if "socket" in sys.modules:
                sys.modules["socket"].socket = self._original_socket_class
            self._original_socket_class = None

        if self._original_requests_request:
            if "requests.api" in sys.modules:
                sys.modules["requests.api"].request = self._original_requests_request
            self._original_requests_request = None

        for i, finder in enumerate(sys.meta_path):
            if isinstance(finder, _SecurityImportFinder):
                sys.meta_path.pop(i)
                break
        
        self._is_active = False
        self._log_debug("Security Manager DEACTIVATED.")


class _SecurityImportFinder(MetaPathFinder):
    """A MetaPathFinder that intercepts imports of sensitive modules."""
    _manager: SecurityManager
    _intercepting_modules: list[str] = ["os", "subprocess", "socket", "requests"]

    def __init__(self, manager: SecurityManager) -> None:
        self._manager = manager

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if not self._manager._is_active or fullname not in self._intercepting_modules:
            return None
        return ModuleSpec(fullname, _SecurityModuleLoader(self._manager, fullname))


class _SecurityModuleLoader(Loader):
    """A custom Loader that applies security patches to modules."""
    _manager: SecurityManager
    _fullname: str

    def __init__(self, manager: SecurityManager, fullname: str) -> None:
        self._manager = manager
        self._fullname = fullname

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        return None

    def exec_module(self, module: ModuleType) -> None:
        # 내장 스펙 복원 후 모듈 로드 진행 허용하여 교착 상태 방어
        sys.modules[self._fullname] = module
        
        if self._fullname == "os":
            self._manager._patch_builtins_and_os()
        elif self._fullname == "subprocess":
            self._manager._patch_subprocess(module)
        elif self._fullname == "socket":
            self._manager._patch_socket(module)
        elif self._fullname == "requests":
            self._manager._patch_requests(module)
