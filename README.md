## Стек

* Python 3.10
* asyncio
* Poetry

## Установка и запуск

```bash
git clone <repo-url>
cd <repo-folder>

poetry install

chmod +x run_all.sh
./run_all.sh
```

Скрипт поднимет сервер и двух клиентов, подержит их 300 секунд и завершит процессы.
Логи пишутся в папку `logs/`.
