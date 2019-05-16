import yaml
from constants import ROOT_DIR
from utils.initializer import initializer


class Config:
    @classmethod
    def from_dict(cls, config: dict):
        return cls(**config)


class DatabaseConfiguration(Config):
    @initializer
    def __init__(self, provider: str,
                 database: str,
                 user: str,
                 password: str,
                 host: str,
                 port: str,
                 table_info: dict):
        pass


class RedisConfiguration(Config):
    @initializer
    def __init__(self, host: str, port: [str, int], db: [int, str]):
        pass


class ModelConfiguration(Config):
    @initializer
    def __init__(self, module: str, class_name: str):
        pass


class PreprocessingConfiguration(Config):
    @initializer
    def __init__(self, module: str, class_name: str):
        pass


class CelerySettings:
    def __init__(self):
        try:
            yml = ROOT_DIR / 'configuration.yml'
            with open(yml) as config_file:
                configs = yaml.load(config_file)
        except FileNotFoundError as ex:
            print(ex)
            exit(-1)

        self.database_configuration = DatabaseConfiguration.from_dict(configs['database'])
        self.redis_configuration = RedisConfiguration.from_dict(configs['redis'])
        self.model_configuration = ModelConfiguration.from_dict(configs['model'])
        self.preprocessing_configuration = None
        if 'preprocessing' in configs:
            self.preprocessing = PreprocessingConfiguration.from_dict(configs['preprocessing'])


class ServerSettings:
    def __init__(self):
        self.redis_configuration = None
        self.use_jwt = False
        self.debug_recognition = False


settings = CelerySettings()
server_settings = ServerSettings()
