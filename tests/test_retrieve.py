import pathlib

import pytest

from patapsco.retrieve import *


def test_json_results_reader():
    directory = pathlib.Path('.') / 'tests' / 'json_files'
    results_iter = JsonResultsReader(str(directory))
    results = next(results_iter)
    assert results.query.id == '001'
    assert results.query.lang == 'en'
    assert results.query.text == 'test 1'
    assert results.system == 'MockRetriever'
    assert len(results.results) == 2
    assert results.results[0].doc_id == 'aaa'
    assert results.results[0].rank == 1
    results = next(results_iter)
    assert results.query.id == '002'
    assert results.query.lang == 'en'
    assert results.query.text == 'test 2'
    assert results.system == 'MockRetriever'
    assert len(results.results) == 2
    assert results.results[0].doc_id == 'bbb'
    assert results.results[0].rank == 1
    with pytest.raises(StopIteration):
        next(results_iter)
