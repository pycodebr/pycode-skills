Salva o mapa pra consultar quando for estudar a sua primeira API.

Uma requisição passa por cinco estações: o navegador separa o endereço em protocolo, domínio e caminho; o DNS troca o domínio pelo IP do servidor; o servidor recebe o verbo GET e o caminho; o código consulta o banco de dados; e a resposta volta com o código de status 200 e o conteúdo em JSON.

Pra ver a primeira estação no seu terminal:
from urllib.parse import urlsplit; print(urlsplit("https://exemplo.com/cursos/42").path)

Deixa o mapa salvo e volta nele quando uma API responder com erro.
