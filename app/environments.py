from enum import Enum

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig


class Environment(Enum):
    DEVELOPMENT = 'development'
    PRODUCTION = 'production'
    TESTING = 'testing'


CONFIG_MAP = {
    Environment.DEVELOPMENT: DevelopmentConfig,
    Environment.PRODUCTION: ProductionConfig,
    Environment.TESTING: TestingConfig
}
