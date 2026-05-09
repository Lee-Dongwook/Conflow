import logging

from .protocol import McpAuthProtocol

logger = logging.getLogger(__name__)

class NoneAuthHandler(McpAuthProtocol):
    async def get_headers(self, mcp_config, state, config, resolve_template_function, agent_model=None) -> dict[str, str]:  # noqa: E501
        return {}

    async def refresh_if_needed(self, error, mcp_config, state, agent_model, config, resolve_template_function, endpoint_url=None  # noqa: E501
    ) -> bool: 
        return False


class ApiKeyAuthHandler(McpAuthProtocol):
    async def get_headers(self, mcp_config, state, config, resolve_template_function, agent_model=None) -> dict[str, str]:  # noqa: E501
        raw_headers = mcp_config.get("headers", {}) or mcp_config.get("env", {})
        return resolve_template_function(raw_headers, state, agent_model=agent_model, config=config)


class OAuth2AuthHandler(McpAuthProtocol):
    async def get_headers(self, mcp_config, state, config, resolve_template_function, agent_model=None) -> dict[str, str]:  # noqa: E501 
        raw_headers = mcp_config.get('headers', {})
        return resolve_template_function(raw_headers, state, agent_model=agent_model, config=config)

    async def refresh_if_needed(
        self, error, mcp_config, state, agent_model, config, resolve_template_function, endpoint_url=None  # noqa: E501
    ) -> bool:
        from .executor import refresh_mcp_oauth2_token

        refresh_config = mcp_config.get('refresh_config') or mcp_config.get('oauth2_config') or {}

        new_token = await refresh_mcp_oauth2_token(
            refresh_config, state, agent_model, config, resolve_template_function, endpoint_url=endpoint_url  # noqa: E501
        )

        if new_token and new_token.get('access_token'):
            sec = config["configurable"].setdefault("secrets", {})
            sec["ACCESS_TOKEN"] = new_token["access_token"]
            if new_token.get("refresh_token"):
                sec["REFRESH_TOKEN"] = new_token["refresh_token"]
            return True

        return False
    
