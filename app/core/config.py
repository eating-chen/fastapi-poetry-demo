"""config param"""
from functools import lru_cache

from opensearchpy import OpenSearch
from pydantic import BaseSettings, Field


class SkillConfig:
    """SkillConfig"""

    SKILL_CLASS_MAP = {
        "Retrieve": "RetrievalSkillManager",
        "SLU": "SluSkillManager",
        "KBQA": "KbqaSkillManager",
        "ModelManager": "ModelSkillManager",
    }


class InferenceConfig(BaseSettings):
    min_max_normalization_parameter: int = 6.4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    db_url: str = "sqlite:///./db.sqlite3"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class OpensearchConnectSettings(BaseSettings):
    host: str = "localhost"
    port: int = 9200
    username: str = "admin"
    password: str = "admin"
    use_ssl: bool = True
    verify_certs: bool = False
    ssl_assert_hostname: bool = False
    ssl_show_warn: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class OpensearchIndexSettings(BaseSettings):
    settings: dict = {
        "number_of_shards": 1,
        "number_of_replicas": 3,
        "index": {
            "similarity": {
                "default": {"type": "BM25", "k1": 1.2, "b": 0.75, "discount_overlaps": True}
            }
        },
    }

    type_mapping: dict = {
        "properties": {
            "content": {"type": "text"},
            "articleID": {"type": "integer"},
            "content_sentences": {
                "type": "nested",
                "properties": {
                    "sentence_content": {"type": "text"},
                    "sentence_id": {"type": "integer"},
                    "sentence_order": {"type": "integer"},
                },
            },
        }
    }

    index_mapping = {
        "settings": settings,
        "mappings": type_mapping,
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RetrievalEmbeddingModel(BaseSettings):
    onnx_model_id: str = "multilingual-e5-large/onnx/model.onnx"
    model_id: str = "intfloat/multilingual-e5-base"
    embedding_length: int = 768


class TrainingArgumentsDefault(BaseSettings):
    train_batch_size: int = Field(
        default=16,
        ge=1,
        le=64,
        description="固定的訓練batch size，使用者如果輸入超過這個設定值則會用gradient_accumulation_steps來累積gradient",
    )
    learning_rate: float = Field(
        default=5e-5, ge=1e-5, le=1e-3, description="訓練的預設學習率，給定範圍[1e-5, 1e-3]"
    )
    epoch: int = Field(default=2, ge=1, le=30, description="訓練的預設epoch數量，給定範圍[1, 30]")
    weight_decay: float = Field(
        default=0.01,
        ge=1e-5,
        le=1,
        description="訓練的預設weight decay，值越大容易導致underfitting，給定範圍[1e-5, 1]",
    )
    eval_batch_size_ratio: int = Field(
        default=2, const=True, description="每次evaluate的資料量，預設為使用者輸入train_batch_size的2倍"
    )
    save_steps_ratio: float = Field(
        default=0.5, const=True, desciprtion="多少steps會儲存一次model，預設steps數為訓練半個epoch"
    )
    warmup_steps_ratio: float = Field(
        default=0.1, const=True, description="warmup steps的數量，預設steps數為訓練1/10的總steps"
    )
    save_strategy: str = Field(default="steps", const=True, description="儲存策略固定為steps")
    evaluation_strategy: str = Field(default="steps", const=True, description="評估策略固定為steps")
    slu_label_names: list = ["intent", "label"]
    save_total_limit: int = Field(default=1, const=True, description="最多儲存幾個model，設定為1會是儲存表現最好的")
    load_best_model_at_end: bool = Field(
        default=True, const=True, description="是否在訓練結束後載入表現最好的model"
    )
    remove_unused_columns: bool = Field(default=False, const=True, description="是否移除不需要的column")
    early_stop_patience: int = Field(
        default=2, ge=1, le=5, description="early stop的patience,模型如果在設定回合數內表現沒有更好則會自動停止訓練"
    )
    early_stop_threshold: float = Field(
        default=0, ge=0, le=0.001, description="評估是否要early_stop的門檻值"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SluModelConfig(BaseSettings):
    slu_model_id: str = Field(
        default="distiluse-base-multilingual-cased-v1", description="Slu使用的模型"
    )
    inference_topk: int = Field(default=1, gt=0, description="Slu intent 推論所要顯示的前k個結果")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()


def get_opensearch_connect():
    opensearch_connect_settings = OpensearchConnectSettings()
    client = OpenSearch(
        hosts=[
            {"host": opensearch_connect_settings.host, "port": opensearch_connect_settings.port}
        ],
        http_auth=(
            opensearch_connect_settings.username,
            opensearch_connect_settings.password,
        ),
        use_ssl=opensearch_connect_settings.use_ssl,
        verify_certs=opensearch_connect_settings.verify_certs,
        ssl_assert_hostname=opensearch_connect_settings.ssl_assert_hostname,
        ssl_show_warn=opensearch_connect_settings.ssl_show_warn,
    )
    return client
