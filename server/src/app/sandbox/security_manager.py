"""
Centralized security manager for sandboxed Python execution.

This module implements a robust security layer to control file system access,
process execution, and network communication within a sandboxed environment.
It aims to prevent malicious or unintended operations by intercepting and
auditing sensitive Python built-ins and standard library functions.
"""

import builtins
import functools
import importlib
import logging
import os
import re
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from typing_extensions import override

from .utils import (
    MAX_RAW_WRITE_SIZE,
    DEFAULT_ALLOWED_EXTENSIONS,
    validate_path,
    is_allowed_file_type,
    check_write_size_limit,
    create_temp_file,
)

logger = logging.getLogger(__name__)

# --- Configuration & State ---

class SecurityPolicy:
    """
    Defines the security policies for the sandbox.
    """
    FORBIDDEN_PATH_PATTERNS: List[str] = [
        "/var/", "/root/", "/proc", "/sys", # Critical system directories
        "~/", # User home directory shortcut
        "../", # Path traversal attempts
    ]
    ALLOWED_SYSTEM_PREFIXES: List[str] = [
        "/usr/", "/lib/", "/bin/", "/sbin/", # Standard system libraries and binaries
        "/dev/null", # Harmless device
    ]
    READ_ONLY_MODE: bool = os.getenv("SANDBOX_READ_ONLY", "false").lower() == "true"
    STRICT_MODE: bool = os.getenv("SANDBOX_STRICT_MODE", "false").lower() == "true"
    DEBUG_VERBOSE: bool = os.getenv("SANDBOX_DEBUG_VERBOSE", "false").lower() == "true"
    USER_ROOT: Path = Path(os.getcwd()).resolve() # The root directory for user's files

    def _log_event(self, message: str, level: int = logging.DEBUG) -> None:
        """Internal logging utility."""
        if self.DEBUG_VERBOSE or level >= logging.WARNING:
            logger.log(level, f"[SANDBOX_SECURITY] {message}")

    def is_path_forbidden(self, target_path: str, context: str) -> bool:
        """Checks if a path contains forbidden patterns."""
        if any(p in target_path for p in self.FORBIDDEN_PATH_PATTERNS):
            self._log_event(
                f"AUDIT WARNING: Forbidden pattern '{target_path}' detected in {context}.",
                level=logging.WARNING
            )
            return True
        return False

    def check_path_access(self, file_path: str, context: str, write_attempt: bool = False) -> None:
        """
        Validates path access against forbidden patterns, read-only mode, and user root.

        Args:
            file_path (str): The path to check.
            context (str): The context of the access attempt (e.g., "file open", "shell command").
            write_attempt (bool): True if this is a write attempt, False for read.

        Raises:
            PermissionError: If access is denied by policy.
            ValueError: If the path is invalid.
        """
        if self.READ_ONLY_MODE and write_attempt:
            self._log_event(
                f"SECURITY ALERT: Blocked write attempt in Read-Only mode for '{file_path}'.",
                level=logging.ERROR
            )
            raise PermissionError(f"Sandbox: Write access is DISABLED (Read-Only mode): {file_path}")

        if self.is_path_forbidden(file_path, context):
             if self.STRICT_MODE:
                self._log_event(
                    f"SECURITY BLOCK: Strict mode active. Blocking access to forbidden path '{file_path}'.",
                    level=logging.ERROR
                )
                raise PermissionError(f"Sandbox: Access to forbidden path is DENIED in strict mode: {file_path}")
             # Allow non-strict mode to proceed with a warning

        try:
            # Use utils.validate_path to ensure path is within USER_ROOT and free of traversal
            validated_path = validate_path(file_path, self.USER_ROOT)
            # Further check against allowed system prefixes if it's an absolute path outside USER_ROOT
            if validated_path != Path(file_path).resolve() and not any(
                validated_path.as_posix().startswith(p) for p in self.ALLOWED_SYSTEM_PREFIXES
            ):
                self._log_event(
                    f"AUDIT WARNING: Path '{file_path}' resolved outside user root and not in system prefixes.",
                    level=logging.WARNING
                )
                if self.STRICT_MODE:
                    self._log_event(
                        f"SECURITY BLOCK: Strict mode active. Blocking external path '{file_path}'.",
                        level=logging.ERROR
                    )
                    raise PermissionError(f"Sandbox: Access to external path is DENIED in strict mode: {file_path}")
        except ValueError as e:
            self._log_event(f"SECURITY ALERT: Invalid path '{file_path}' detected: {e}", level=logging.ERROR)
            raise PermissionError(f"Sandbox: Invalid path detected: {file_path}") from e


class SecurityManager:
    """
    Manages the application of security policies by patching built-ins and modules.
    """
    _policy: SecurityPolicy
    _original_open: Callable = builtins.open
    _original_os_system: Optional[Callable[[str], int]] = None
    _original_os_popen: Optional[Callable[..., Any]] = None
    _original_subprocess_popen: Optional[Type[Any]] = None
    _original_socket_connect: Optional[Callable[..., Any]] = None
    _original_requests_request: Optional[Callable[..., Any]] = None
    _is_active: bool = False

    def __init__(self, policy: Optional[SecurityPolicy] = None) -> None:
        self._policy = policy or SecurityPolicy()

    def _log_debug(self, message: str) -> None:
        """Debug logging utility."""
        if self._policy.DEBUG_VERBOSE:
            logger.debug(f"[SECURITY_MANAGER] {message}")

    def _log_security_alert(self, message: str, level: int = logging.ERROR) -> None:
        """Security alert logging utility."""
        logger.log(level, f"[SECURITY_MANAGER] {message}")


    def _secure_open(
        self,
        file: Any,
        mode: str = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Callable[..., Any]] = None,
    ) -> Any:
        """Secure wrapper for builtins.open."""
        path_str = str(file)
        write_attempt = any(m in mode for m in ["w", "a", "+", "x"])
        self._policy.check_path_access(path_str, "file open", write_attempt)

        if not is_allowed_file_type(path_str, DEFAULT_ALLOWED_EXTENSIONS):
            self._log_security_alert(f"Blocked access to disallowed file type: {path_str}", logging.WARNING)
            if self._policy.STRICT_MODE:
                raise PermissionError(f"Sandbox: Access to disallowed file type is DENIED: {path_str}")

        return self._original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)

    def _secure_os_system(self, command: str) -> int:
        """Secure wrapper for os.system."""
        self._policy.check_path_access(command, "os.system command", write_attempt=True) # Assuming system calls can modify
        self._log_debug(f"Auditing os.system command: {command}")
        return self._original_os_system(command) if self._original_os_system else os.system(command) # Fallback

    def _secure_os_popen(self, *args: Any, **kwargs: Any) -> Any:
        """Secure wrapper for os.popen."""
        command = args[0] if args else kwargs.get("command", "unknown") # heuristic
        self._policy.check_path_access(str(command), "os.popen command", write_attempt=True)
        self._log_debug(f"Auditing os.popen command: {command}")
        return self._original_os_popen(*args, **kwargs) if self._original_os_popen else os.popen(command) # Fallback

    def _block_os_dangerous_function(self, func_name: str) -> Callable[..., None]:
        """Returns a function that blocks specific os module functions."""
        def blocked_func(*args: Any, **kwargs: Any) -> None:
            self._log_security_alert(f"Blocked attempt to call os.{func_name}", logging.ERROR)
            raise PermissionError(f"Sandbox: os.{func_name} is DISABLED")
        return blocked_func

    def _secure_subprocess_popen(self, *args: Any, **kwargs: Any) -> Any:
        """Secure wrapper for subprocess.Popen."""
        command_args = args[0] if args else kwargs.get("args", "unknown")
        command_str = str(command_args)
        self._policy.check_path_access(command_str, "subprocess.Popen command", write_attempt=True)
        self._log_debug(f"Auditing subprocess.Popen command: {command_str}")
        return self._original_subprocess_popen(*args, **kwargs) if self._original_subprocess_popen else importlib.import_module("subprocess").Popen(*args, **kwargs) # Fallback

    def _secure_socket_connect(self, sock_self: Any, address: Any) -> Any:
        """Secure wrapper for socket.socket.connect."""
        self._log_debug(f"Auditing socket.connect to {address}")
        # In a real sandbox, this is where you'd check a whitelist of allowed network addresses.
        # For now, we just audit.
        return self._original_socket_connect(sock_self, address) if self._original_socket_connect else self._original_socket_connect(sock_self, address) # Fallback to original again to avoid infinite recursion

    def _secure_requests_request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Secure wrapper for requests.api.request."""
        self._log_debug(f"Auditing requests.{method} to {url}")
        # Similar to socket, this is where a network whitelist could be applied.
        return self._original_requests_request(method, url, **kwargs) if self._original_requests_request else importlib.import_module("requests.api").request(method, url, **kwargs) # Fallback


    def _patch_builtins_and_os(self) -> None:
        """Applies security patches to built-in functions and the os module."""
        builtins.open = self._secure_open

        # Patch os module functions
        if hasattr(os, "system"):
            self._original_os_system = os.system
            os.system = self._secure_os_system
        if hasattr(os, "popen"):
            self._original_os_popen = os.popen
            os.popen = self._secure_os_popen
        
        # Block dangerous os functions
        for dangerous_func in ["spawnl", "spawnv", "execl", "execv", "fork", "forkpty", "execvpe"]:
            if hasattr(os, dangerous_func):
                setattr(os, dangerous_func, self._block_os_dangerous_function(dangerous_func))
        
        self._log_debug("Built-ins and os module patched.")

    def _patch_subprocess(self, subprocess_module: ModuleType) -> None:
        """Applies security patches to the subprocess module."""
        if hasattr(subprocess_module, "Popen"):
            self._original_subprocess_popen = subprocess_module.Popen
            subprocess_module.Popen = self._secure_subprocess_popen
        self._log_debug("Subprocess module patched.")

    def _patch_socket(self, socket_module: ModuleType) -> None:
        """Applies security patches to the socket module."""
        if hasattr(socket_module, "socket"):
            # We need to patch the connect method of the socket class, not the module itself
            # This requires creating a subclass to override the method.
            _original_socket_class = socket_module.socket
            class SecureSocket(_original_socket_class): # type: ignore
                def connect(self, address: Any) -> Any:
                    return self._policy.check_path_access(str(address), "socket connect") # Reuse path_access for now
                    # In a real scenario, this should be a dedicated network access check
                    # e.g., self._policy.check_network_access(address)
                    return super().connect(address)
            socket_module.socket = SecureSocket
            # Also store the original connect method if possible, for finer control
            # This approach replaces the class, making direct original_connect storage tricky.
            # A more advanced pattern would involve patching the method directly, not the class.
        self._log_debug("Socket module patched.")

    def _patch_requests(self, requests_module: ModuleType) -> None:
        """Applies security patches to the requests module."""
        if hasattr(requests_module, "api") and hasattr(requests_module.api, "request"):
            self._original_requests_request = requests_module.api.request
            requests_module.api.request = self._secure_requests_request
        self._log_debug("Requests module patched.")


    def install_security_hooks(self) -> None:
        """
        Installs all security hooks for built-ins and critical modules.
        """
        if self._is_active:
            self._log_debug("Security hooks already active.")
            return

        self._patch_builtins_and_os()

        # Register import hook for other modules
        sys.meta_path.insert(0, _SecurityImportFinder(self))

        # Force-patch already loaded sensitive modules
        for mod_name, patch_func in {
            "subprocess": self._patch_subprocess,
            "socket": self._patch_socket,
            "requests": self._patch_requests,
        }.items():
            if mod_name in sys.modules:
                self._log_debug(f"Force-patching already loaded module: {mod_name}")
                patch_func(sys.modules[mod_name]) # type: ignore

        self._is_active = True
        self._log_debug("Security Manager ACTIVATED.")

    def uninstall_security_hooks(self) -> None:
        """Uninstalls all security hooks and restores original functions."""
        if not self._is_active:
            self._log_debug("Security hooks not active.")
            return

        builtins.open = self._original_open
        if self._original_os_system:
            os.system = self._original_os_system
        if self._original_os_popen:
            os.popen = self._original_os_popen
        
        # Restore original dangerous os functions if they existed
        for dangerous_func in ["spawnl", "spawnv", "execl", "execv", "fork", "forkpty", "execvpe"]:
            if hasattr(os, dangerous_func) and hasattr(self, f"_original_os_{dangerous_func}"):
                setattr(os, dangerous_func, getattr(self, f"_original_os_{dangerous_func}"))

        # Restore original subprocess Popen if it was patched
        if self._original_subprocess_popen:
            subprocess_module = importlib.import_module("subprocess")
            subprocess_module.Popen = self._original_subprocess_popen
        
        # Restore original socket.socket if it was patched
        if hasattr(sys.modules.get("socket"), "_original_socket_class"): # type: ignore
            socket_module = importlib.import_module("socket")
            socket_module.socket = socket_module._original_socket_class # type: ignore

        # Restore original requests.api.request if it was patched
        if self._original_requests_request:
            requests_api_module = importlib.import_module("requests.api")
            requests_api_module.request = self._original_requests_request

        # Remove import hook
        for i, finder in enumerate(sys.meta_path):
            if isinstance(finder, _SecurityImportFinder):
                sys.meta_path.pop(i)
                break
        
        self._is_active = False
        self._log_debug("Security Manager DEACTIVATED.")


class _SecurityImportFinder(MetaPathFinder):
    """
    A MetaPathFinder that intercepts imports of sensitive modules
    and applies security patches via the SecurityManager.
    """
    _manager: SecurityManager
    _intercepting_modules: List[str] = ["os", "subprocess", "socket", "requests"]
    _in_patching_process: set[str] = set()

    def __init__(self, manager: SecurityManager) -> None:
        self._manager = manager

    @override
    def find_spec(
        self,
        fullname: str,
        path: Optional[List[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        if not self._manager._is_active or fullname not in self._intercepting_modules:
            return None

        if fullname in self._in_patching_process:
            # Prevent re-entry if we're already trying to patch this module
            return None

        self._in_patching_process.add(fullname)
        try:
            # Create a ModuleSpec with a custom loader
            return ModuleSpec(fullname, _SecurityModuleLoader(self._manager, fullname))
        finally:
            self._in_patching_process.remove(fullname)


class _SecurityModuleLoader(Loader):
    """
    A custom Loader that applies security patches to modules
    after they have been loaded.
    """
    _manager: SecurityManager
    _fullname: str

    def __init__(self, manager: SecurityManager, fullname: str) -> None:
        self._manager = manager
        self._fullname = fullname

    @override
    def create_module(self, spec: ModuleSpec) -> Optional[ModuleType]:
        # Let the default import machinery create the module
        return None

    @override
    def exec_module(self, module: ModuleType) -> None:
        # Load the module normally first
        if self._fullname == "os":
            self._manager._patch_builtins_and_os() # os patching includes builtins.open
        elif self._fullname == "subprocess":
            self._manager._patch_subprocess(module)
        elif self._fullname == "socket":
            self._manager._patch_socket(module)
        elif self._fullname == "requests":
            self._manager._patch_requests(module)
        
        self._manager._log_debug(f"Module '{self._fullname}' secured during import.")


# --- Initialization ---

def initialize_security_manager(policy: Optional[SecurityPolicy] = None) -> SecurityManager:
    """
    Initializes and installs the global security manager.

    Returns:
        SecurityManager: The initialized security manager instance.
    """
    manager = SecurityManager(policy)
    manager.install_security_hooks()
    return manager

# Global instance for easy access if needed (e.g., for uninstall)
_global_security_manager: Optional[SecurityManager] = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(levelname)s: %(message)s')
    # Example usage:
    # Set environment variables for testing
    os.environ["SANDBOX_READ_ONLY"] = "true"
    os.environ["SANDBOX_STRICT_MODE"] = "true"
    os.environ["SANDBOX_DEBUG_VERBOSE"] = "true"

    print("--- Initializing Security Manager ---")
    _global_security_manager = initialize_security_manager()

    print("\n--- Testing file operations ---")
    try:
        with open("test_read.txt", "w") as f:
            f.write("This should fail.")
    except PermissionError as e:
        print(f"Caught expected error: {e}")

    # Create a dummy file for read test
    Path("test_read.txt").write_text("Hello, sandbox!")
    try:
        with open("test_read.txt", "r") as f:
            content = f.read()
            print(f"Read content (should succeed if file exists and read-only): {content}")
    except Exception as e:
        print(f"Caught unexpected error during read: {e}")
    os.remove("test_read.txt")

    print("\n--- Testing os.system ---")
    try:
        os.system("echo 'This is os.system'")
    except PermissionError as e:
        print(f"Caught expected error: {e}") # Should not fail in this implementation, just audit.

    print("\n--- Testing os.spawnl ---")
    try:
        os.spawnl(os.P_WAIT, "/bin/echo", "echo", "This is os.spawnl")
    except PermissionError as e:
        print(f"Caught expected error: {e}")

    print("\n--- Testing subprocess.Popen ---")
    try:
        from subprocess import Popen, PIPE
        p = Popen(["echo", "This is subprocess.Popen"], stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        print(f"Subprocess output: {out.decode().strip()}")
    except PermissionError as e:
        print(f"Caught expected error: {e}")

    print("\n--- Testing socket ---")
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("google.com", 80)) # This will fail in strict mode if not allowed
        s.close()
        print("Socket connection successful (should be audited).")
    except Exception as e:
        print(f"Caught expected error during socket connect: {e}")

    print("\n--- Testing requests ---")
    try:
        import requests
        response = requests.get("http://example.com") # This will fail in strict mode if not allowed
        print(f"Requests get successful (should be audited): {response.status_code}")
    except Exception as e:
        print(f"Caught expected error during requests.get: {e}")

    print("\n--- Uninstalling Security Manager ---")
    if _global_security_manager:
        _global_security_manager.uninstall_security_hooks()
    
    print("\n--- Testing file operations after uninstall ---")
    try:
        with open("test_write_after_uninstall.txt", "w") as f:
            f.write("This should succeed after uninstall.")
        print("Write after uninstall successful.")
        os.remove("test_write_after_uninstall.txt")
    except Exception as e:
        print(f"Caught unexpected error after uninstall: {e}")