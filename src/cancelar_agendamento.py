import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_CONSULTAS', 'SaoBueno_Consultas')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    parametros = event.get('Details', {}).get('Parameters', event)
    cpf = parametros.get('cpf')
    data_hora = parametros.get('dataHora')

    if not cpf or not data_hora:
        return {
            "sucesso": False,
            "mensagem": "CPF ou DataHora não fornecidos."
        }

    try:
        table.update_item(
            Key={
                'CPF': cpf,
                'DataHora': data_hora
            },
            UpdateExpression="SET #st = :val",
            ExpressionAttributeNames={
                '#st': 'Status'
            },
            ExpressionAttributeValues={
                ':val': False  # Salva o BOOL false no DynamoDB
            }
        )

        return {
            "sucesso": True,
            "mensagem": "Agendamento cancelado com sucesso."
        }

    except Exception as e:
        print(f"Erro ao cancelar agendamento: {str(e)}")
        return {
            "sucesso": False,
            "mensagem": "Erro interno ao tentar cancelar o agendamento."
        }