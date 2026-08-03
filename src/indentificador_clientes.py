import os
import boto3
from boto3.dynamodb.conditions import Key

# 1. Warm Start: Inicialização fora da função para reuso de conexões
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_PACIENTES', 'SaoBueno_Pacientes')
table = dynamodb.Table(TABLE_NAME)

INDEX_TELEFONE = 'GSI_Telefone'

def lambda_handler(event, context):
    print("Evento recebido:", event)
    
    # 2. Extrai os parâmetros considerando o envelope do Amazon Connect E chamadas diretas
    details = event.get('Details', {}).get('Parameters', {})
    contact_data = event.get('Details', {}).get('ContactData', {})
    
    # Busca o CPF (seja enviado no evento direto ou pelos Parâmetros do Connect)
    cpf = event.get('cpf') or details.get('cpf')
    
    # Busca o Telefone (direto, via parâmetros configurados no Connect ou pelo número de origem da chamada)
    telefone = (
        event.get('telefone') 
        or details.get('telefone')
        or details.get('phoneNumber') 
        or contact_data.get('CustomerEndpoint', {}).get('Address')
    )

    paciente = None

    # 3. Busca Primária por CPF (Mais rápida e barata)
    if cpf:
        response = table.get_item(Key={'CPF': str(cpf)})
        paciente = response.get('Item')

    # 4. Busca Secundária por Telefone (Fallback via GSI_Telefone)
    if not paciente and telefone:
        # Garante o formato com +55 caso o número venha sem DDI do Connect
        telefone_str = str(telefone)
        if not telefone_str.startswith('+'):
            telefone_str = f"+55{telefone_str}"

        response = table.query(
            IndexName=INDEX_TELEFONE,
            KeyConditionExpression=Key('Telefone').eq(telefone_str)
        )
        items = response.get('Items', [])
        if items:
            paciente = items[0]

    # 5. Se não encontrar o paciente em nenhuma das buscas
    if not paciente:
        return False

    # 6. Mapeamento e formato final de retorno para o Amazon Connect
    return {
        "cpf": str(paciente.get('CPF', '')),
        "nome": str(paciente.get('Nome', '')),
        "idade": str(paciente.get('Idade', '')),
        "sexo": str(paciente.get('Sexo', '')),
        "celular": str(paciente.get('Telefone', paciente.get('Celular', ''))),
        "nomeResponsavel": str(paciente.get('NomeResponsavel', '')),
        "telefoneResponsavel": str(paciente.get('TelefoneResponsavel', '')),
        "planoSaude": str(paciente.get('PlanoSaude', 'Não informado'))
    }