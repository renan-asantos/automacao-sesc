import httpx2
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from dateparser.search import search_dates

from notify import notificar_sistema, notificar_zenity

url = "https://centrodeferias.sescsp.org.br/"

def extrair_datas(texto: str) -> tuple:
    """
    Extrai todas as datas do texto usando dateparser e
    retorna as datas de inscrição, do sorteio e do pagamento.
    """
    texto_sem_horas = re.sub(r'\d{1,2}h\*?', '', texto)
    resultado = search_dates(texto_sem_horas, languages=['pt'], settings={'TIMEZONE': 'America/Sao_Paulo'})

    datas = [data for _, data in resultado]
    datas.sort()
    datas_inscricao = datas[0:2]
    data_sorteio = datas[2]
    data_pagamento = datas[3]

    return datas_inscricao, data_sorteio, data_pagamento

def find_banner_text(soup: BeautifulSoup) -> str | None:
    """Encontra e retorna o texto do banner verde de inscrições."""

    script = next(
        (s.string for s in soup.find_all('script') if s.string and 'window.__WP_DATA__' in s.string),
        None
    )
    if not script:
        return None

    dados = json.loads(script[script.find('{'):script.rfind('}') + 1])

    banners = dados.get('settings', {}).get('banners', {})
    html_banner = next((v for v in banners.values() if v and 'COMUNICADO' in v), None)
    if not html_banner:
        return None

    soup_banner = BeautifulSoup(html_banner, 'html.parser')
    textos = (p.get_text(separator=' ', strip=True) for p in soup_banner.find_all('p'))
    texto = ' '.join(t for t in textos if t)

    return ' '.join(texto.split()) or None

def main():
    try:
        with httpx2.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        if comunicado := find_banner_text(soup):
            print("-" * 50)
            print(comunicado)
            print("-" * 50)

            datas_inscricao, data_sorteio, data_pagamento = extrair_datas(comunicado)
            data_inicio_inscricao, data_fim_inscricao = datas_inscricao
            hoje = datetime.now()
            dias_para_abrir = (data_inicio_inscricao - hoje).days

            if hoje < data_inicio_inscricao and dias_para_abrir <= 7:
                message = f"🔔 Faltam {dias_para_abrir} dias para as inscrições abrirem."
                notificar_zenity(mensagem=f"{message}\n\n{comunicado[:200]}...")

            elif data_inicio_inscricao < hoje < data_fim_inscricao:
                notificar_zenity(mensagem="🚨 INSCRIÇÕES ABERTAS!\nCorra para se inscrever!")
            else:
                message = "⏰ Já passou as inscrições"
                print(message)
                notificar_zenity(mensagem=message)

        else:
            message = "⚠️ Não encontrei o banner COMUNICADO na estrutura esperada."
            notificar_zenity(mensagem=message)
            print(message)

    except httpx2.HTTPStatusError as e:
        print(f"❌ Erro HTTP (status {e.response.status_code}): {e}")
    except httpx2.ConnectTimeout:
        print("❌ Erro de timeout: o site não respondeu a tempo.")
    except httpx2.RequestError as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()