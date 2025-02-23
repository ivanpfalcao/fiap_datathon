import requests
import json

URL = "http://127.0.0.1:8000/add_news/"
API_KEY = "your_default_api_token"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "news_list": [
        {
            "page": "9c3d2660-7294-4306-b76a-84b6a32366cc",
            "issued": "2021-04-14T12:32:52.000Z",
            "body": """
Na média global, 45% dos cerca de 21 mil entrevistados pelo Ipsos afirmaram que sua saúde mental piorou pouco ou muito no último ano, sob a pandemia
Getty Images via BBC
Mais da metade dos brasileiros entrevistados por uma pesquisa declararam que sua saúde emocional e mental piorou desde o início da pandemia, em índice superior à média dos 30 países e territórios pesquisados.
Senado aprova atendimento no SUS para transtornos mentais agravados pela pandemia
Um terço dos ex-pacientes de Covid desenvolveu transtorno neurológico ou psiquiátrico
Depressão não é tudo igual: conheça os tipos menos comuns
Segundo pesquisa do instituto Ipsos, encomendada pelo Fórum Econômico Mundial e cedida à BBC News Brasil, 53% dos brasileiros declararam que seu bem-estar mental piorou um pouco ou muito no último ano. Essa porcentagem só é maior em quatro países: Itália (54%), Hungria (56%), Chile (56%) e Turquia (61%).
"A gente já havia percebido isso em outra pesquisa global que fizemos em março do ano passado, quando 41% dos brasileiros relatavam ter sintomas como ansiedade, insônia ou depressão já por consequência da pandemia", diz à BBC News Brasil Helena Junqueira, gerente de pesquisas digitais do Ipsos.
Em meio à devastação causada pela Covid-19 no país e a necessidade de isolamento social, "a percepção é de que a saúde mental das pessoas está piorando, e além disso o tema se tornou mais discutido recentemente. É um assunto mais presente", prossegue Junqueira.
Outros estudos sobre o mesmo tema também trazem dados preocupantes.
Um deles, publicado pela Fiocruz com outras seis universidades em meados do ano passado, dizia que "sentimentos frequentes de tristeza e depressão afetavam 40% da população adulta brasileira, e sensação frequente de ansiedade e nervosismo foi relatada por mais de 50% das pessoas".
Um relatório de 2017 da Organização Mundial da Saúde (OMS) apontava o Brasil como o país com a maior prevalência de transtornos de ansiedade nas Américas: o problema afetava 9,3% da população, o equivalente a 18,6 milhões de pessoas.
Transtornos depressivos foram relatados por 5,8% dos brasileiros, ou 11,5 milhões de pessoas.
"De fato, vemos como isso é um problema aqui no Brasil (com as pesquisas), e a situação atual da pandemia tem pesado muito", diz Junqueira. "As notícias são muito tristes, e (com o isolamento social e a perda de redes de apoio) as pessoas têm perdido as estratégias para lidar com isso."
Efeito pandemia: isolamento leva a depressão
Saúde mental global
É claro que não é um problema exclusivo do Brasil: na média global, 45% dos cerca de 21 mil entrevistados pelo Ipsos afirmaram que sua saúde mental piorou um pouco ou muito no último ano, na vida sob a pandemia. 
E em apenas três países (Índia, China continental e Arábia Saudita) dos 30 pesquisados, houve mais gente dizendo que sua saúde mental melhorou do que gente que acha que ela piorou.
"O impacto da pandemia na saúde mental das pessoas já é extremamente preocupante", afirmou, ainda em maio de 2020, o diretor-geral da OMS, Tedros Adhanom Ghebreyesus. 
"O isolamento social, o medo de contágio e a perda de membros da família são agravados pelo sofrimento causado pela perda de renda e, muitas vezes, de emprego".
Na época, a OMS alertou que entre os grupos de risco estavam, por exemplo, "mulheres, particularmente aquelas que estão fazendo malabarismos com a educação em casa e trabalhando em tarefas domésticas; pessoas idosas e quem possui condições de saúde mental pré-existentes". 
Transtornos mentais não aumentaram durante a pandemia, dizem pesquisadores
É importante, porém, fazer a ressalva que pesquisadores consultados em uma reportagem da BBC News Brasil viram a quantidade de diagnósticos de transtornos mentais se manter relativamente estável durante a pandemia.
Portanto, não é possível afirmar que o isolamento social ou o contexto de luto tenham levado, por exemplo, a um aumento nos casos de suicídio - como chegou a insinuar o presidente Jair Bolsonaro, no mês passado, ao criticar medidas de lockdown.
Suicídios diminuem em países ricos durante primeiros meses da pandemia de Covid
Lockdown causa depressão e suicídio? O que um ano de Covid-19 nos revela
Um estudo publicado pela revista científica Lancet nesta terça-feira (13/4) sobre tendências de suicídio em cidades ou regiões de 21 países (Brasil incluído) não identificou aumento de casos durante o período da pandemia, embora faça a ressalva de que os dados oficiais dos países podem ainda não estar completos e de que o tema precisa ser constantemente monitorado.
O que não quer dizer - tal como mostram as pesquisas - que a pandemia não esteja cobrando um preço do bem-estar mental das pessoas.
"É esperado sentir-se mal, triste, confuso e revoltado diante de uma situação nova e ruim, como foi o aparecimento da Covid-19. Mas há todo um processo entre esses sentimentos e o desenvolvimento de um transtorno mental", disse à BBC News Brasil em março psiquiatra André Brunoni, professor associado da Faculdade de Medicina da Universidade de São Paulo.
Volta à normalidade?
De volta às respostas dos brasileiros na pesquisa do Ipsos, além dos 53% que viram sua saúde mental piorar, cerca de um terço (34%) dos entrevistados afirmou que sua saúde mental mudou pouco no último ano, e cerca de 13% sentiram melhora no bem-estar emocional.
Ao serem questionados sobre quando esperavam voltar à normalidade como era antes da Covid-19, metade dos entrevistados afirmou esperar que isso aconteça ao longo deste ano. Pouco mais de um terço (35%), porém, diz acreditar que isso vai levar ainda mais tempo.
Em média, no mundo, 45% da população dos países entrevistados espera voltar à normalidade neste ano, e 41% acham que vai ser necessário mais tempo.
A pesquisa entrevistou 21 mil pessoas (sendo mil delas no Brasil) de 16 a 74 anos, entre 19 de fevereiro e 5 de março.
As entrevistas foram feitas online, o que limita o alcance da pesquisa à população mais urbana e conectada, mas o Ipsos informa que a representatividade da amostra é de todo o território nacional.
VÍDEOS: Mais vistos do G1 nos últimos dias
            """
        }
    ]
}

try:
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    print(json.dumps(response.json()))  # Print the JSON response
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:
    print("Response is not valid JSON")
    print(response.text)