"""生产配置校验测试。"""
import pytest

from app.config import Settings


def test_prod_requires_all_secrets():
    s = Settings(env="prod", jwt_secret="", wechat_app_id="", wechat_app_secret="")
    with pytest.raises(RuntimeError):
        s.validate_production()


def test_prod_forbids_mock_openid():
    s = Settings(
        env="prod",
        jwt_secret="x" * 32,
        wechat_app_id="appid",
        wechat_app_secret="secret",
        wechat_mock_openid="mock_openid",
    )
    with pytest.raises(RuntimeError):
        s.validate_production()


def test_prod_ok_with_valid_config():
    s = Settings(
        env="prod",
        jwt_secret="x" * 32,
        wechat_app_id="appid",
        wechat_app_secret="secret",
        wechat_mock_openid="",  # 显式置空，避免被测试环境变量污染
    )
    s.validate_production()  # 不应抛异常


def test_dev_skips_validation():
    s = Settings(env="dev", jwt_secret="", wechat_mock_openid="mock")
    s.validate_production()  # dev 环境不校验，不应抛异常
