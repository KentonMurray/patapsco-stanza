import collections
import json
import pathlib

from .config import BaseConfig, Union
from .text import TextProcessor, StemConfig, TokenizeConfig, TruncStemConfig
from .util import trec, ComponentFactory
from .util.file import GlobFileGenerator

Topic = collections.namedtuple('Topic', ('id', 'lang', 'title', 'desc', 'narr'))
Query = collections.namedtuple('Query', ('id', 'lang', 'text'))


class InputConfig(BaseConfig):
    name: str
    lang: str
    encoding: str = "utf8"
    strip_non_digits: bool = False
    path: Union[str, list]


class ProcessorConfig(BaseConfig):
    name: str = "default"
    query: str = "title"  # field1+field2 where field is title, desc, narr
    utf8_normalize: bool = True
    lowercase: bool = True
    tokenize: TokenizeConfig
    stem: Union[StemConfig, TruncStemConfig]


class TopicReaderFactory(ComponentFactory):
    classes = {
        'trec': 'TrecTopicReader'
    }
    config_class = InputConfig


class TopicProcessorFactory(ComponentFactory):
    classes = {
        'default': 'TopicProcessor'
    }
    config_class = ProcessorConfig


class TrecTopicReader:
    def __init__(self, config):
        self.lang = config.lang
        self.strip_non_digits = config.strip_non_digits
        self.topics = GlobFileGenerator(config.path, trec.parse_topics, 'EN-', config.encoding)

    def __iter__(self):
        return self

    def __next__(self):
        topic = next(self.topics)
        identifier = ''.join(filter(str.isdigit, topic[0])) if self.strip_non_digits else topic[0]
        return Topic(identifier, self.lang, topic[1], topic[2], topic[3])


class QueryWriter:
    def __init__(self, path):
        dir = pathlib.Path(path)
        dir.mkdir(parents=True)
        path = dir / 'queries.json'
        self.file = open(path, 'w')

    def write(self, query):
        self.file.write(json.dumps(query._asdict()) + "\n")

    def close(self):
        self.file.close()


class TopicProcessor(TextProcessor):
    """Topic Preprocessing"""

    def __init__(self, config):
        """
        Args:
            config (ProcessorConfig)
        """
        super().__init__(config)
        self.fields = config.query.split('+')

    def run(self, topic):
        """
        Args:
            topic (Topic)

        Returns
            Query
        """
        text = self._select_text(topic)
        if self.config.utf8_normalize:
            text = self.normalize(text)
        if self.config.lowercase:
            text = self.lowercase_text(text)
        tokens = self.tokenize(text)
        if self.config.stem:
            tokens = self.stem(tokens)
        text = ' '.join(tokens)
        return Query(topic.id, topic.lang, text)

    def _select_text(self, topic):
        return ' '.join([getattr(topic, f).strip() for f in self.fields])
