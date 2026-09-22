# Automação Sesc Bertioga

Criei esse código para bater no [site do sesc bertioga](https://centrodeferias.sescsp.org.br/) e ler o banner verde
que fica avisando quando as inscrições estão abertas, porque eles não possuem um sistema de notificação próprio.

## Rodando manualmente

Para baixar as dependências do projeto

```shell
uv sync
```

Será criada uma venv e você poderá rodar o projeto com

```shell
uv run src/main.py
```

## Automatizando para rodar a cada vez que o notebook ligar

Eu uso um ubuntu aqui no meu notebook e quis deixar pra me notificar através do sistema de notificação do ubuntu.
Pra isso, fiz um cron pra rodar toda vez que meu notebook ligar

```shell
@reboot sleep 90 && export DISPLAY=:0 && export XDG_RUNTIME_DIR=/run/user/1000 &&
cd $HOME/projects/automacao-sesc/src && $HOME/.local/bin/uv run main.py >> $HOME/sesc_monitor.log 2>&1
```

Da pra simplificar e melhorar, mas por enquanto isso aqui ta funcionando.