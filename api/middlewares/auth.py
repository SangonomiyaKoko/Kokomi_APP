from typing import Optional
from fastapi import Header, HTTPException


class AuthManager:
    """Token 鉴权管理器"""

    _tokens: dict[str, set[str]] = {}

    @classmethod
    def init(cls, tokens_data: list[dict]) -> None:
        """初始化 token 存储

        清空现有数据，从传入的 token 列表中重建映射

        Args:
            tokens_data: 格式为:
                [
                    {"token": "abc123", "permissions": ["root"]},
                ]
        """
        cls._tokens.clear()
        for item in tokens_data:
            token = item["token"]
            permissions = set(item.get("permissions", []))
            cls._tokens[token] = permissions

    @classmethod
    def reload(cls, tokens_data: list[dict]) -> None:
        """重新加载所有 token

        与 init() 行为一致，用于运行时刷新 token 数据
        """
        cls.init(tokens_data)

    @classmethod
    def get_permissions(cls, token: str) -> Optional[set[str]]:
        """获取 token 对应的权限集合

        Args:
            token: assess-token 值

        Returns:
            权限名称的集合；
            token 不存在时返回 None
        """
        return cls._tokens.get(token)

    @classmethod
    def has_permission(cls, token: str, required: str) -> bool:
        """检查 token 是否拥有指定权限

        root 权限绕过所有权限检查，视为拥有所有接口的访问权。

        Args:
            token: assess-token 值
            required: 需要的权限名称

        Returns:
            True 表示 token 有效且权限满足
        """
        permissions = cls._tokens.get(token)
        if permissions is None:
            return False
        if "root" in permissions:
            return True
        return required in permissions

    @classmethod
    def is_valid_token(cls, token: str) -> bool:
        """检查 token 是否存在于存储中"""
        return token in cls._tokens

def require_permission(permission: str):
    """要求 token 持有指定权限

    从请求头 ``assess-token`` 中提取 token 并校验权限。
    用法：

        @router.get("/secret")
        async def secret(token: str = Depends(require_permission("root"))):
            ...

    Args:
        permission: 需要的权限名称；root 权限持有者自动通过
    """

    def _check(assess_token: str = Header(..., alias="assess-token")) -> str:
        if not AuthManager.is_valid_token(assess_token):
            raise HTTPException(
                status_code=403,
                detail='Invalid Access Token',
            )
        if not AuthManager.has_permission(assess_token, permission):
            raise HTTPException(
                status_code=403,
                detail='Invalid Access Token',
            )
        return assess_token

    return _check


def get_token_info(assess_token: str = Header(..., alias="assess-token")):
    """提取 token 但不校验权限 —— 仅验证 token 有效性

    适用于需要获取 token 信息但不对具体权限做限制的接口。
    """

    if not AuthManager.is_valid_token(assess_token):
        raise HTTPException(
            status_code=403,
            detail='Invalid Access Token',
        )
    return assess_token
