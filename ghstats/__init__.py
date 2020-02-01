from collections import Counter
from datetime import datetime, timedelta

from ghstats.api import Github


class StatsGithub(object):
    def __init__(self, owner, name, branch, since=None, until=None, token=None):
        """
        Args:
            owner (str): Владелец репозитория
            name (str): Имя репозитория
            branch (str): Ветка репозитория
            since (datetime.datetime): Дата начала анализа
            until (datetime.datetime): Дата конца анализа
        """
        self.__api = Github(token=token)
        self.__owner = owner
        self.__name = name
        self.__repo = f"{owner}/{name}"
        self.__branch = branch
        self.__since = since
        self.__until = until

    def __query_date_range(self, since, until):
        query = []
        if since:
            query.append(f"created:>={since.strftime('%Y-%m-%d')}")
        if until:
            query.append(f"created:<{until.strftime('%Y-%m-%d')}")
        return query

    def issues(self, issue="issue", delta=14):
        """
        Количество открытых, закрытых и старых issues.
        Issue считается старым, если он не закрывается в течение 14 дней.

        Args:
            issue (str): тип задачи:
                * `issue`: issue
                * `pr`: pull request
            delta (int): интервал для "старых" задач
        """
        oldest_date = (self.__since or datetime.now()) - timedelta(days=delta)

        query = [
            f"repo:{self.__repo}",
            f"is:{issue}"
        ]

        issue_query = "+".join(query + self.__query_date_range(self.__since, self.__until))

        opened = self.__api.search_issues(f"{issue_query}+is:open").get('total_count', None)
        closed = self.__api.search_issues(f"{issue_query}+is:closed").get('total_count', None)

        old_issue_query = "+".join(query + self.__query_date_range(self.__since, oldest_date))
        oldest = self.__api.search_issues(f"{old_issue_query}+is:open").get('total_count', None)

        return opened, closed, oldest

    def pull_requests(self):
        """
        Количество открытых, закрытых и старых pull requests.
        Pull request считается старым, если он не закрывается в течение 30 дней.
        """
        return self.issues(issue="pr", delta=30)

    def contributions(self):
        """
        Самые активные участники. Таблица из 2 столбцов: login автора, количество его коммитов.
        Таблица отсортирована по количеству коммитов по убыванию. Не более 30 строк.
        """
        commits = self.__api.repo_commits(
            self.__owner,
            self.__name,
            self.__branch,
            since=self.__since,
            until=self.__until)

        ret = Counter()

        for commit in commits:
            username = commit['commit']['author']['name']

            author = commit['author']
            if author:
                username = author['login']

            ret[username] += 1

        return sorted(ret.items(), key=lambda el: el[1], reverse=True)[:30]
