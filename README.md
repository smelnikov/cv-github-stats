ghstats
=======

Утилита для получения статистики публичного репозитория GitHub

Получает такие данные, как:

* Самые активные участники (топ30 по коммитам)

* Количество открытых, закрытых, старых pull requests. 
    Pull request считается старым, если он не закрывается в течение 30 дней.

* Количество открытых, закрытых, старых issues. 
    Issue считается старым, если он не закрывается в течение 14 дней.



Установка
---------

Это нативная Python 3.0+ библиотека. Для установки:

    pip install git+https://github.com/smelnikov/cv-github-stats


Консольная утилита
------------------

После установки библиотеки её можно использовать как консольную утилиту.

    $ python -m ghstats -h
    usage: ghstats [-h] [-since SINCE] [-until UNTIL] [-b BRANCH] [-t TOKEN] repo

    positional arguments:
      repo                  URL публичного репозитория на github.com
    
    optional arguments:
      -h, --help            show this help message and exit
      -r 
      -s SINCE, --since SINCE
                            Дата начала анализа (YYYY-MM-DD). Если пустая, то неограничено.
      -u UNTIL, --until UNTIL
                            Дата окончания анализа (YYYY-MM-DD). Если пустая, то неограничено.
      -b BRANCH, --branch BRANCH
                            Ветка репозитория. По умолчанию - master
      -t TOKEN, --token TOKEN
                            Токен авторизации
