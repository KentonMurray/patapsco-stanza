import enum

from .config import BaseConfig, SectionConfig, UncheckedSectionConfig, Optional, Union


class PipelineMode(str, enum.Enum):
    STREAMING = 'streaming'
    BATCH = 'batch'


class Tasks(str, enum.Enum):
    """Tasks that make up the system pipelines"""
    DOCUMENTS = 'documents'
    INDEX = 'index'
    TOPICS = 'topics'
    QUERIES = 'queries'
    RETRIEVE = 'retrieve'
    RERANK = 'rerank'


class PathConfig(BaseConfig):
    """Simple config with only a path variable"""
    path: str


"""""""""""""""""
Text Processing
"""""""""""""""""


class NormalizationConfig(BaseConfig):
    report: bool = False  # save a report of normalization changes
    lowercase: bool = True


class TextProcessorConfig(BaseConfig):
    """Configuration for the text processing"""
    model_path: Optional[str]  # path to spacy or stanza model directory
    normalize: NormalizationConfig = NormalizationConfig()
    tokenize: str
    stopwords: Union[bool, str] = "lucene"
    stem: Union[bool, str] = False


"""""""""""""""""
Documents
"""""""""""""""""


class DocumentsInputConfig(BaseConfig):
    """Configuration for the document corpus"""
    format: str
    lang: str
    encoding: str = "utf8"
    path: Union[str, list]


class DocumentsConfig(SectionConfig):
    """Document processing task configuration"""
    input: DocumentsInputConfig
    process: TextProcessorConfig
    output: Union[bool, str] = False


"""""""""""""""""
Topics & Queries
"""""""""""""""""


class TopicsInputConfig(BaseConfig):
    """Configuration for Topic input"""
    format: str
    lang: str
    encoding: str = "utf8"
    strip_non_digits: bool = False
    prefix: Union[bool, str] = "EN-"
    path: Union[str, list]


class TopicsConfig(SectionConfig):
    """Configuration for topics task"""
    input: TopicsInputConfig
    fields: str = "title"  # field1+field2 where field is title, desc, or narr
    output: Union[bool, str] = False


class QueriesInputConfig(BaseConfig):
    """Configuration for reading queries"""
    format: str = "json"
    encoding: str = "utf8"
    path: Union[str, list]


class PSQConfig(BaseConfig):
    """Probabilistic Structured Query configuration"""
    path: str  # path to a translation table
    threshold: float = 0.97  # cumulative probability threshold
    lang: str  # language code of documents
    # Text processing configuration after PSQ projection
    normalize: NormalizationConfig = NormalizationConfig()
    stopwords: Union[bool, str] = "lucene"
    stem: Union[bool, str] = False


class QueriesConfig(SectionConfig):
    """Configuration for processing queries"""
    input: Optional[QueriesInputConfig]
    process: TextProcessorConfig
    psq: Optional[PSQConfig]
    output: Union[bool, str] = True


"""""""""""""""""
Database
"""""""""""""""""


class DatabaseConfig(SectionConfig):
    output: Union[bool, str] = True


"""""""""""""""""
Index
"""""""""""""""""


class IndexInputConfig(BaseConfig):
    """Configuration of optional retrieval inputs"""
    documents: PathConfig


class IndexConfig(SectionConfig):
    """Configuration for building an index"""
    input: Optional[IndexInputConfig]
    name: str
    output: Union[bool, str] = True


"""""""""""""""""
Retrieve
"""""""""""""""""


class RetrieveInputConfig(BaseConfig):
    """Configuration of optional retrieval inputs"""
    index: Union[None, PathConfig]
    queries: Optional[PathConfig]


class RetrieveConfig(SectionConfig):
    """Configuration for retrieval"""
    name: str
    number: int = 1000
    input: Optional[RetrieveInputConfig]
    output: Union[bool, str] = True


"""""""""""""""""
Rerank
"""""""""""""""""


class RerankInputConfig(BaseConfig):
    """Configuration of optional rerank inputs"""
    db: Optional[PathConfig]  # if running both stages, runner will copy this from documents config
    results: Optional[PathConfig]  # set if starting stage2 at reranking


class RerankConfig(UncheckedSectionConfig):
    """Configuration for the rerank task"""
    input: Optional[RerankInputConfig]
    name: str
    script: Optional[str]  # for the shell reranker
    output: Union[bool, str] = False


"""""""""""""""""
Score
"""""""""""""""""


class ScoreInputConfig(BaseConfig):
    """Qrels downstream configuration"""
    format: str = "trec"
    path: str  # path to qrels file or glob to match multiple files


class ScoreConfig(SectionConfig):
    """Configuration for the scorer module"""
    metrics: list = ['ndcg_prime', 'ndcg', 'map', 'recall_100', 'recall_1000']
    input: ScoreInputConfig


"""""""""""""""""
Main
"""""""""""""""""


class StageConfig(BaseConfig):
    """Configuration for one of the stages"""
    mode: str = "streaming"  # streaming or batch
    batch_size: Optional[int]  # for batch, the default is a single batch
    num_jobs: int = 2  # number of parallel jobs
    progress_interval: Optional[int]  # how often should progress be logged
    # start and stop are intended for parallel processing
    start: Optional[int]  # O-based index of start position in input (inclusive)
    stop: Optional[int]  # O-based index of stop position in input (exclusive)


class ParallelConfig(BaseConfig):
    name: str  # mp or qsub
    queue: Optional[str] = "all.q"  # used for qsub jobs


class RunConfig(SectionConfig):
    """Configuration for a run of Patapsco"""
    name: str
    path: Optional[str]  # base path for run output by default created based on name
    results: str = "results.txt"  # default results filename
    parallel: Optional[ParallelConfig]  # configure for a parallel job
    stage1: Union[bool, StageConfig] = StageConfig()
    stage2: Union[bool, StageConfig] = StageConfig()


class RunnerConfig(BaseConfig):
    """Configuration for the patapsco runner"""
    run: RunConfig
    database: DatabaseConfig = DatabaseConfig()
    documents: Optional[DocumentsConfig]
    index: Optional[IndexConfig]
    topics: Optional[TopicsConfig]
    queries: Optional[QueriesConfig]
    retrieve: Optional[RetrieveConfig]
    rerank: Optional[RerankConfig]
    score: Optional[ScoreConfig]
