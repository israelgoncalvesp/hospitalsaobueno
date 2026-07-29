import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
NOME_TABELA = 'SaoBueno_Pacientes'
NOME_GSI = 'GSI_Telefone'

def lambda_handler(event, context):
    print("Evento recebido do Connect:", json.dumps(event))
    
    details = event.get('Details', {}).get('Parameters', {})
    telefone_str = details.get('phoneNumber') or event.get('Details', {}).get('ContactData', {}).get('CustomerEndpoint', {}).get('Address')
    
    tabela = dynamodb.Table(NOME_TABELA)
    paciente = None
    
    # BUSCA PASSIVA PELO TELEFONE (GSI_Telefone)
    if telefone_str:
        if not telefone_str.startswith('+'):
            telefone_str = f"+55{telefone_str}"
            
        resposta = tabela.query(
            IndexName=NOME_GSI,
            KeyConditionExpression=Key('Telefone').eq(telefone_str)
        )
        itens = resposta.get('Items', [])
        if itens:
            paciente = itens[0]

    # RETORNO AO CONNECT
    if paciente:
        exames_lista = paciente.get('ExamesAtribuidos', [])
        exames_texto = ", ".join(exames_lista) if exames_lista else "Nenhum exame pendente"
        
        return {
            "pacienteEncontrado": "true",
            "cpf": str(paciente.get('CPF', '')),
            "nome": str(paciente.get('Nome', '')),
            "idade": str(paciente.get('Idade', '')),
            "genero": str(paciente.get('Genero', '')),
            "nomeResponsavel": str(paciente.get('NomeResponsavel', '')),
            "planoSaude": str(paciente.get('PlanoSaude', 'Não informado')),
            "examesAtribuidos": exames_texto
        }
    else:
        return {
            "pacienteEncontrado": "false"
        }