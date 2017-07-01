import pytest

try:
    import mock
except ImportError:
    from unittest import mock

import traw
from traw.exceptions import TRAWLoginError
from traw.const import ENVs, GET, API_PATH as AP

MOCK_USERNAME = 'mock username'
MOCK_USER_API_KEY = 'mock user api key'
MOCK_PASSWORD = 'mock password'
MOCK_URL = 'mock url'
PROJ1 = {'project': 'project1'}
PROJ2 = {'project': 'project2'}
PROJ3 = {'project': 'project3'}


@pytest.fixture()
def no_env_vars():
    empty_dict = dict()
    with mock.patch.dict('traw.api.os.environ', empty_dict):
        yield empty_dict


@pytest.fixture()
def env_vars():
    env_vars_dict = {ENVs.USER_KEY: MOCK_USERNAME,
                     ENVs.API_KEY: MOCK_USER_API_KEY,
                     ENVs.PASS_KEY: MOCK_PASSWORD,
                     ENVs.URL_KEY: MOCK_URL}
    with mock.patch.dict('traw.api.os.environ', env_vars_dict):
        yield env_vars_dict


@pytest.fixture()
def env_vars_no_key():
    env_vars_dict = {ENVs.USER_KEY: MOCK_USERNAME,
                     ENVs.PASS_KEY: MOCK_PASSWORD,
                     ENVs.URL_KEY: MOCK_URL}
    with mock.patch.dict('traw.api.os.environ', env_vars_dict):
        yield env_vars_dict


@pytest.fixture()
def no_path_mock():
    with mock.patch('traw.api.os.path') as path_mock:
        path_mock.exists.return_value = False
        yield path_mock


@pytest.fixture()
def config_parser_mock():
    traw_config = {'username': MOCK_USERNAME,
                   'user_api_key': MOCK_USER_API_KEY,
                   'password': MOCK_PASSWORD,
                   'url': MOCK_URL}
    cp_mock = mock.MagicMock()
    cp_mock.return_value = cp_mock
    cp_mock.read.return_value = cp_mock
    cp_mock.__getitem__.return_value = traw_config
    with mock.patch('traw.api.ConfigParser', new_callable=cp_mock):
        with mock.patch('traw.api.os.path.exists'):
            yield traw_config


@pytest.fixture()
def api():
    with mock.patch('traw.api.Session') as Session:
        Session.return_value = Session
        yield traw.api.API(username=MOCK_USERNAME,
                           user_api_key=MOCK_USER_API_KEY,
                           password=MOCK_PASSWORD,
                           url=MOCK_URL)


def test___init___with_caller_supplied_credentials(no_env_vars, no_path_mock):
    """ Verify the credentials can be set through the API init call
        Verify that the user_api_key keyword overrides the password keyword
    """
    api = traw.api.API(username=MOCK_USERNAME,
                       user_api_key=MOCK_USER_API_KEY,
                       password=MOCK_PASSWORD,
                       url=MOCK_URL)

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] == MOCK_USER_API_KEY
    assert api._session._auth[1] != MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test___init___with_caller_supplied_password(no_env_vars, no_path_mock):
    """ Verify a password can be used instead of the apk key """
    api = traw.api.API(username=MOCK_USERNAME,
                       password=MOCK_PASSWORD,
                       url=MOCK_URL)

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] != MOCK_USER_API_KEY
    assert api._session._auth[1] == MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test___init___with_env_credentials(env_vars, no_path_mock):
    """ Verify the credentials can be set through environment variables
        Verify that the user_api_key keyword overrides the password keyword
    """
    api = traw.api.API()

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] == MOCK_USER_API_KEY
    assert api._session._auth[1] != MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test___init___with_env_password(env_vars_no_key, no_path_mock):
    """ Verify the credentials can be set through environment variables
        Verify that the user_api_key keyword overrides the password keyword
    """
    api = traw.api.API()

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] != MOCK_USER_API_KEY
    assert api._session._auth[1] == MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test__env_var_exception():
    """ Verify an exception is raised if the wrong value is passed in """
    with pytest.raises(ValueError):
        traw.api._env_var('does not exist')


def test__init__with_config_file(no_env_vars, config_parser_mock):
    """ Verify the credentials can be set a configuration file
        Verify that the user_api_key keyword overrides the password keyword
    """
    api = traw.api.API()

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] == MOCK_USER_API_KEY
    assert api._session._auth[1] != MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test__init__with_config_file_w_password(no_env_vars, config_parser_mock):
    """ Verify the credentials can be set a configuration file
        Verify that the password keyword can be used
    """
    config_parser_mock['user_api_key'] = None
    api = traw.api.API()

    assert api._session._auth[0] == MOCK_USERNAME
    assert api._session._auth[1] != MOCK_USER_API_KEY
    assert api._session._auth[1] == MOCK_PASSWORD
    assert api._session._url == MOCK_URL


def test__init__no_credentials_exception(no_env_vars, no_path_mock):
    """ Verify that an exception is raised if no credentials are set """
    with pytest.raises(TRAWLoginError):
        traw.api.API()


def test_projects_no_arg(api):
    """ Verify the ``projects`` method call with no args """
    api._session.request.return_value = [PROJ1, PROJ2, PROJ3]
    proj_list = list(api.projects())

    exp_call = mock.call(method=GET, params=None, path=AP['get_projects'])

    assert all(map(lambda p: isinstance(p, dict), proj_list))
    assert len(proj_list) == 3
    assert api._session.request.call_args == exp_call


def test_projects_with_arg(api):
    """ Verify the ``projects`` method call with an arg """
    api._session.request.return_value = [PROJ1, PROJ2, PROJ3]
    ARG1 = 'arg1'
    proj_list = list(api.projects(ARG1))

    exp_call = mock.call(
        method=GET, params={'is_completed': ARG1}, path=AP['get_projects'])

    assert all(map(lambda p: isinstance(p, dict), proj_list))
    assert len(proj_list) == 3
    assert api._session.request.call_args == exp_call