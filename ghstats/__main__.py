"""
Скрипт для вывода статистики по коммитам, PR и задачам.

Внимание!
    По-умолчанию кол-во неавторизованных запросов ограничено (60 запросов в час)!
    <https://developer.github.com/v3/#rate-limiting>

    Авторизация, увеличит лимит запросов (5000 запросов в час) [используйте параметр `--token`]
    <https://github.com/settings/tokens>

    Авторизация под средством нескольких токенов не поддерживается!
"""
import argparse
import re
from datetime import datetime
from sys import stderr, stdout

from ghstats import StatsGithub
from ghstats.api.exceptions import RateLimitExceededException

REPO_REGEX = "(?P<host>(git@|https://)([\w\.@]+)(/|:))(?P<owner>[\w,\-,\_]+)/(?P<name>[\w,\-,\_]+)(.git){0,1}((/){0,1})"


def valid_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        msg = f'Not a valid date: "{d}".'
        raise argparse.ArgumentTypeError(msg)


def valid_repo(s):
    match = re.match(REPO_REGEX, s)
    if not match:
        msg = f'Not a valid repository URL: "{s}"'
        raise argparse.ArgumentTypeError(msg)
    return match.groupdict()


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog='ghstats',
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__
    )

    parser.add_argument(
        'repo',
        type=valid_repo,
        help='URL публичного репозитория на github.com'
    )
    parser.add_argument(
        '-s', '--since',
        type=valid_date,
        help='Дата начала анализа (YYYY-MM-DD). Если пустая, то неограничено.',
        default=None,
        required=False,
    )
    parser.add_argument(
        '-u', '--until',
        type=valid_date,
        help='Дата окончания анализа (YYYY-MM-DD). Если пустая, то неограничено.',
        default=None,
        required=False)
    parser.add_argument(
        '-b', '--branch',
        type=str,
        help='Ветка репозитория. По умолчанию - master',
        default='master'
    )

    parser.add_argument(
        '-t', '--token',
        type=str,
        help='Токен авторизации. См. <https://github.com/settings/tokens>',
        default=None
    )

    args = parser.parse_args() if args is None else parser.parse_args(args)

    return args


def main(*test_args):
    args = parse_args()
    stats = StatsGithub(
        args.repo['owner'],
        args.repo['name'],
        args.branch,
        since=args.since,
        until=args.until,
        token=args.token
    )

    parameters = [
        f"{'Repository:':<32}\n",
        f"{'- host':<32} {args.repo['host']}\n",
        f"{'- owner':<32} {args.repo['owner']}\n",
        f"{'- name':<32} {args.repo['name']}\n",
        f"{'- branch':<32} {args.branch}\n"
    ]

    if args.since or args.until:
        parameters.append(f"{'Period:':<32}\n")
        if args.since:
            parameters.append(f"{'- since:':<32} {args.since.strftime('%Y-%m-%d')}\n")
        if args.until:
            parameters.append(f"{'- until:':<32} {args.until.strftime('%Y-%m-%d')}\n")

    stdout.writelines(parameters)

    try:
        opened, closed, oldest = stats.issues()
        stdout.writelines([
            f"{'Issues:':<32}\n",
            f"{'- opened':<32} {opened}\n",
            f"{'- closed':<32} {closed}\n",
            f"{'- oldest':<32} {oldest}\n"
        ])

        opened, closed, oldest = stats.pull_requests()
        stdout.writelines([
            f"{'Pull requests:':<32}\n",
            f"{'- opened':<32} {opened}\n",
            f"{'- closed':<32} {closed}\n",
            f"{'- oldest':<32} {oldest}\n"
        ])

        contributions = stats.contributions()

        lines = [f"{'Contributors:':<32}\n"]
        if contributions:
            for username, commits in contributions:
                lines.append(f"{'- ' + username:<32} {commits:<8}\n")
        stdout.writelines(lines)
        stdout.close()
    except RateLimitExceededException:
        err = "Количество неавторизованных запросов к GitHub API исчерпано. "
        if not args.token:
            err += "Для увеличения лимита авторизуйтесь с помощью токена."
        stderr.write(err)


if __name__ == '__main__':
    main()
