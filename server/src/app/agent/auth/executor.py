import logging
from typing import Any

import httpx
from langchain_core.runnables import RunnableConfig

from ..model import Agent

logger = logging.getLogger(__name__)

async def discover_mcp_oauth_config(endpoint_url: str | None) -> dict | None:
    if not endpoint_url:
        return None
    try:
        base_url = endpoint_url.split("/mcp")[0] if "/mcp" in endpoint_url else endpoint_url
        discovery_url = f"{base_url.rstrip('/')}/.well-known/oauth-protected-resource/mcp"

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(discovery_url)
            if response.status_code != 200:
                return None
            
            discovery_info = response.json()
            auth_servers = discovery_info.get("authorization_servers")
            if not auth_servers:
                return None

            as_url = auth_servers[0].rstrip("/")
            for meta_path in ["/.well-known/oauth-authorization-server", "/.well-known/openid-configuration"]:  # noqa: E501
                try:
                    meta_response = await client.get(f"{as_url}{meta_path}")
                    if meta_response.status_code == 200:
                        meta_data = meta_response.json()
                        return {
                            "token_url": meta_data.get("token_endpoint"),
                            "authorization_url": meta_data.get("authorization_endpoint"),
                            "registration_url": meta_data.get("registration_endpoint"),
                            "issuer": meta_data.get("issuer"),
                            "scopes": discovery_info.get("scopes", []),
                        }
                except Exception as e:
                        logger.debug(f"Error discovering OAuth2 configuration: {e}")
                        continue
    except Exception as e:
        logger.debug(f"Error discovering OAuth2 configuration: {e}")
    return None

async def refresh_mcp_oauth2_token(
    refresh_config: dict,
    state: dict,
    agent_model: Agent,
    config: RunnableConfig,
    resolve_template_function: Any,
    endpoint_url: str | None = None,
) -> dict[str, str] | None:
    try:
        if not refresh_config.get("url") and not refresh_config.get("token_url") and endpoint_url:
            discovered = await discover_mcp_oauth_config(endpoint_url)
            if discovered:
                refresh_config = {**discovered, **refresh_config}
        
        token_url = resolve_template_function(
            refresh_config.get("url") or refresh_config.get("token_url"), state, agent_model=agent_model, config=config  # noqa: E501
        )

        refresh_token = resolve_template_function(
            refresh_config.get("refresh_token"), state, agent_model=agent_model, config=config
        )
        client_id = resolve_template_function(
            refresh_config.get("client_id", ""), state, agent_model=agent_model, config=config
        )
        client_secret = resolve_template_function(
            refresh_config.get("client_secret", ""), state, agent_model=agent_model, config=config
        )

        if not token_url:
            return None

        async with httpx.AsyncClient() as auth_client:
            if refresh_token:
                payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
            else:
                payload = {"grant_type": "client_credentials"}
            
            if client_id:
                payload["client_id"] = client_id
            if client_secret:
                payload["client_secret"] = client_secret
            
            auth = (client_id, client_secret) if client_id and client_secret else None

            for k,v in refresh_config.items():
                if k not in [
                    "url",
                    "token_url",
                    "refresh_token",
                    "client_id",
                    "client_secret",
                    "token_type",
                    "grant_type"
                ]:
                    if isinstance(v, str | int | bool):
                        payload[k] = resolve_template_function(v, state, agent_model=agent_model, config=config)  # noqa: E501
            
            response = await auth_client.post(token_url, data=payload, auth=auth)

            if response.status_code == 401 and auth:
                payload["client_id"], payload["client_secret"] = client_id, client_secret
                response = await auth_client.post(token_url, data=payload)
            
            response.raise_for_status()
            new_data = response.json()

            return {
                "access_token": new_data.get("access_token"),
                "refresh_token": new_data.get("refresh_token")
            }
    
    except Exception as e:
        logger.error(f"Error discovering OAuth2 configuration: {e}")
        return None
