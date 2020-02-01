from ghstats.api.requests import Requester, PaginatedList


DEFAULT_BASE_URL = "https://api.github.com"


class Github(object):
    def __init__(self, base_url=DEFAULT_BASE_URL, token=None):
        self.__requester = Requester(base_url, token=token)

    def search_issues(self, query):
        """
        `GET /search/issues <http://developer.github.com/v3/search>`

        Args:
            query (str): <https://help.github.com/en/github/searching-for-information-on-github/searching-issues-and-pull-requests>
        """
        _, data = self.__requester.request_and_check("GET", f"/search/issues?q={query}&per_page=1")
        return data

    def repo_commits(self, owner, name, branch=None, since=None, until=None, per_page=100):
        """
        `GET /repos/:owner/:repo/commits <https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository>`

        Args:
            owner (str): Владелец репозитория
            name (str): Имя репозитория
            branch (str): Ветка репозитория
            since (datetime.datetime): Дата начала
            until (datetime.datetime): Дата конца
            per_page (int): Кол-во записей на страницу. Максимум 100.
        """
        params = [f"per_page={per_page}"]

        if branch:
            params.append(f"sha={branch}")
        if since:
            params.append(f"since={since.strftime('%Y-%m-%d')}")
        if until:
            params.append(f"until={until.strftime('%Y-%m-%d')}")

        query = "&".join(params)

        return PaginatedList(self.__requester, f"/repos/{owner}/{name}/commits?{query}")
