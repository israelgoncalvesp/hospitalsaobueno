import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
NOME_TABELA_CONSULTAS = 'SaoBueno_Consultas'

def lambda_handler(event, context):
    print("Evento recebido para consulta:", json.dumps(event))
    
    # 1. Extração do CPF
    details = event.get('Details', {}).get('Parameters', {})
    cpf_str = details.get('cpf')
    
    if not cpf_str:
        return {
            "temAgendamento": "false",
            "erro": "CPF nao fornecido"
        }
        
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf_str)))
    tabela = dynamodb.Table(NOME_TABELA_CONSULTAS)
    
    # 2. Query buscando agendamentos por CPF
    resposta = tabela.query(
        KeyConditionExpression=Key('CPF').eq(cpf_limpo)
    )
    
    itens = resposta.get('Items', [])
    
    # 3. Filtro de agendamentos ativos
    agendamentos_ativos = [i for i in itens if i.get('Status') == 'AGENDADO']
    
    # 4. Retorno puro de dados
    if agendamentos_ativos:
        proxima_consulta = agendamentos_ativos[0]
        
        return {
            "temAgendamento": "true",
            "quantidadeAgendamentos": str(len(agendamentos_ativos)),
            "dataHora": str(proxima_consulta.get('DataHora', '')),
            "medico": str(proxima_consulta.get('Medico', '')),
            "especialidade": str(proxima_consulta.get('Especialidade', ''))
        }
    else:
        return {
            "temAgendamento": "false",
            "quantidadeAgendamentos": "0"
        }