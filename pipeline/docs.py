import collections
import gzip
import json

from .config import BaseConfig, Union
from .error import ParseError
from .text import TextProcessor, StemConfig, TokenizeConfig, TruncStemConfig
from .util import trec, ComponentFactory
from .util.file import GlobFileGenerator

Doc = collections.namedtuple('Doc', ('id', 'lang', 'text'))


class InputConfig(BaseConfig):
    name: str
    lang: str
    encoding: str = "utf8"
    path: Union[str, list]


class ProcessorConfig(BaseConfig):
    name: str = "default"
    utf8_normalize: bool = True
    lowercase: bool = True
    tokenize: TokenizeConfig
    stem: Union[StemConfig, TruncStemConfig]


class DocumentReaderFactory(ComponentFactory):
    classes = {
        'trec': 'TrecDocumentReader',
        'json': 'JsonDocumentReader'
    }
    config_class = InputConfig


class DocumentProcessorFactory(ComponentFactory):
    classes = {
        'default': 'DocumentProcessor'
    }
    config_class = ProcessorConfig


class TrecDocumentReader:
    def __init__(self, config):
        self.lang = config.lang
        self.docs = GlobFileGenerator(config.path, trec.parse_documents, config.encoding)

    def __iter__(self):
        return self

    def __next__(self):
        doc = next(self.docs)
        return Doc(doc[0], self.lang, doc[1])


def parse_json_documents(path, encoding='utf8'):
    open_func = gzip.open if path.endswith('.gz') else open
    with open_func(path, 'rt', encoding=encoding) as fp:
        for line in fp:
            try:
                data = json.loads(line.strip())
            except json.decoder.JSONDecodeError as e:
                raise ParseError(f"Problem parsing json from {path}: {e}")
            try:
                yield data['id'], ' '.join([data['title'].strip(), data['text'].strip()])
            except KeyError as e:
                raise ParseError(f"Missing field {e} in json docs element: {data}")


class JsonDocumentReader:
    def __init__(self, config):
        self.lang = config.lang
        self.docs = GlobFileGenerator(config.path, parse_json_documents, config.encoding)

    def __iter__(self):
        return self

    def __next__(self):
        doc = next(self.docs)
        return Doc(doc[0], self.lang, doc[1])


class DocumentProcessor(TextProcessor):
    """Document Preprocessing"""

    def __init__(self, config):
        """
        Args:
            config (ProcessorConfig)
        """
        super().__init__(config)

    def run(self, doc):
        """
        Args:
            doc (Doc)

        Returns
            Doc
        """
        text = doc.text
        if self.config.utf8_normalize:
            text = self.normalize(text)
        if self.config.lowercase:
            text = self.lowercase_text(text)
        tokens = self.tokenize(text)
        if self.config.stem:
            tokens = self.stem(tokens)
        text = ' '.join(tokens)
        return Doc(doc.id, doc.lang, text)
