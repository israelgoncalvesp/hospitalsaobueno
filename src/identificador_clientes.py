import os
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_PACIENTES', 'SaoBueno_Pacientes')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print("Evento recebido do Connect:", event)
    
    event = event or {}
    details = event.get('Details', {})
    parameters = details.get('Parameters', {})
    
    # Busca o CPF bruto em todas as origens possíveis
    cpf = (
        parameters.get('cpf') or 
        event.get('cpf') or 
        details.get('Lex', {}).get('Slots', {}).get('adquirirCPF') or
        details.get('ContactData', {}).get('Attributes', {}).get('cpf')
    )
    
    # 1. Se não recebeu o CPF
    if not cpf:
        print("Erro: CPF não foi encontrado em nenhuma chave do payload.")
        return {
            "encontrado": "false",
            "motivo": "CPF nao fornecido"
        }

    # Converte para string sem alterar a pontuação original
    cpf = str(cpf)
    print(f"CPF usado na consulta: {cpf}")

    # 2. Consulta direta no DynamoDB
    try:
        response = table.get_item(Key={'CPF': cpf})
        paciente = response.get('Item')
    except Exception as e:
        print(f"Erro ao consultar DynamoDB: {e}")
        return {
            "encontrado": "false",
            "motivo": "Erro no banco"
        }

    # 3. CPF não cadastrado
    if not paciente:
        print(f"CPF {cpf} não localizado na tabela {TABLE_NAME}.")
        return {
            "encontrado": "false",
            "motivo": "CPF nao cadastrado"
        }

    # 4. Paciente localizado com sucesso
    print(f"Paciente encontrado: {paciente.get('Nome')}")
    return {
        "encontrado": "true",
        "cpf": str(paciente.get('CPF', '')),
        "nome": str(paciente.get('Nome', '')),
        "idade": str(paciente.get('Idade', '')),
        "sexo": str(paciente.get('Sexo', '')),
        "planoSaude": str(paciente.get('PlanoSaude', 'Não informado'))
    }