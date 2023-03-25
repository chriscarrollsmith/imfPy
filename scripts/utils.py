import os
import time
import requests
import json
import functools
import pandas as pd
from ratelimiter import RateLimiter
from pkg_resources import get_distribution

def _imf_rate_limited(imf_rate_limit):
    """
    (Internal) Decorator function for rate limiting the decorated function.

    Args:
        rate_limit (RateLimiter): A RateLimiter object specifying the maximum number of calls and the time period.

    Returns:
        Callable: A decorated function that is rate-limited according to the provided RateLimiter object.
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with imf_rate_limit:
                return func(*args, **kwargs)
        return wrapper
    return decorator


imf_rate_limit = RateLimiter(max_calls=5, period=5)


@_imf_rate_limited(rate_limit)
def _imf_download_parse(URL, times=3):
    """
    (Internal) Download and parse JSON content from a URL with rate limiting and retries.

    This function is rate-limited and will perform a specified number of retries in case of failure.

    Args:
        URL (str): The URL to download and parse the JSON content from.
        times (int, optional): The number of times to retry the request in case of failure. Defaults to 3.

    Returns:
        dict: The parsed JSON content as a Python dictionary.

    Raises:
        ValueError: If the content cannot be parsed as JSON after the specified number of retries.
    """
    
    app_name = os.environ.get("IMF_APP_NAME")
    if app_name:
        app_name = app_name[:255]
    else:
        app_name = f'imfr/{get_distribution("imfr").version}'

    headers = {'Accept': 'application/json', 'User-Agent': app_name}
    for _ in range(times):
        response = requests.get(URL, headers=headers)
        content = response.text
        status = response.status_code

        if ('<!DOCTYPE HTML PUBLIC' in content or
            '<!DOCTYPE html in content or
            '<string xmlns="http://schemas.m' in content or
            '<html xmlns=' in content):
            err_message = (f"API request failed. URL: '{URL}', Status: '{status}', "
                           f"Content: '{content[:30]}'")
            raise ValueError(err_message)

        try:
            json_parsed = json.loads(content)
            return json_parsed
        except json.JSONDecodeError:
            if _ < times - 1:
                time.sleep(2 ** (_ + 1))
            else:
                raise


def _imf_dimensions(database_id, times=3, inputs_only=True):
    """
    (Internal) Retrieve the list of codes for dimensions of an individual IMF database.

    Args:
        database_id (str): The ID of the IMF database.
        times (int, optional): The number of times to retry the request in case of failure. Defaults to 3.
        inputs_only (bool, optional): If True, only include input parameters. Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame containing the parameter names and their corresponding codes and descriptions.
    """
    URL = f'http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{database_id}'
    raw_dl = _download_parse(URL, times)

    code = raw_dl['Structure']['CodeLists']['CodeList']['@id']
    description = raw_dl['Structure']['CodeLists']['CodeList']['Name']['#text']
    codelist_df = pd.DataFrame({'code': [code], 'description': [description]})

    params = [dim['@conceptRef'].lower() for dim in raw_dl['Structure']['KeyFamilies']['KeyFamily']['Components']['Dimension']]
    codes = [dim['@codelist'] for dim in raw_dl['Structure']['KeyFamilies']['KeyFamily']['Components']['Dimension']]
    param_code_df = pd.DataFrame({'parameter': params, 'code': codes})

    if inputs_only:
        result_df = param_code_df.merge(codelist_df, on='code', how='left')
    else:
        result_df = param_code_df.merge(codelist_df, on='code', how='outer')

    return result_df