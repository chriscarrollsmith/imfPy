import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.pardir)

from scripts.utils import _download_parse, _imf_metadata, _imf_dimensions

def test_download_parse():
    # Test with a valid URL
    valid_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/BOP/A.US.BXSTVPO_BP6_USD?startPeriod=2020"
    valid_result = _download_parse(valid_url)
    assert isinstance(valid_result, dict)
    assert len(valid_result) == 1
    assert 'CompactData' in valid_result
    assert len(valid_result['CompactData']) == 6

    # Test with an invalid URL
    invalid_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/not_a_real_database/"
    with pytest.raises(ValueError):
        _download_parse(invalid_url)


def test_imf_metadata_valid_url():
    URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/BOP/A.US.BXSTVPO_BP6_USD?startPeriod=2020"
    metadata = _imf_metadata(URL)
    
    assert isinstance(metadata, dict)
    assert len(metadata) == 7
    assert all(value != "NA" for value in metadata.values())


def test_imf_metadata_invalid_url():
    URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/not_a_real_database/"
    
    with pytest.raises(Exception):
        metadata = _imf_metadata(URL)


def test_imf_metadata_empty_url():
    URL = ""
    
    with pytest.raises(ValueError):
        metadata = _imf_metadata(URL)


def test_imf_metadata_times_param():
    URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/BOP/A.US.BXSTVPO_BP6_USD?startPeriod=2020"
    metadata = _imf_metadata


def test_imf_dimensions_valid_database_id():
    database_id = "PCPS"
    dimensions = _imf_dimensions(database_id)
    
    assert isinstance(dimensions, pd.DataFrame)
    assert dimensions.shape == (4, 3)
    assert dimensions.isna().sum().sum() == 0


def test_imf_dimensions_invalid_database_id():
    database_id = "not_a_real_database_id"
    
    with pytest.raises(Exception):
        dimensions = _imf_dimensions(database_id)


def test_imf_dimensions_times_param():
    database_id = "PCPS"
    dimensions = _imf_dimensions(database_id, times=2)
    
    assert isinstance(dimensions, pd.DataFrame)
    assert dimensions.shape == (4, 3)
    assert dimensions.isna().sum().sum() == 0


def test_imf_dimensions_inputs_only_param():
    database_id = "PCPS"
    dimensions_1 = _imf_dimensions(database_id, inputs_only=True)
    dimensions_2 = _imf_dimensions(database_id, inputs_only=False)

    assert isinstance(dimensions_1, pd.DataFrame)
    assert isinstance(dimensions_2, pd.DataFrame)
    assert dimensions_1.shape == (4, 3)
    assert dimensions_2.shape == (6, 3)
    assert dimensions_1.isna().sum().sum() == 0
    assert dimensions_2.isna().sum().sum() == 2