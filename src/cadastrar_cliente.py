import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_PACIENTES', 'SaoBueno_Pacientes')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # Extrai os parâmetros vindos do Amazon Connect / Lex (ou direto no evento em testes)
    parametros = event.get('Details', {}).get('Parameters', event)

    cpf = parametros.get('cpf')

    # Validação simples da chave primária
    if not cpf:
        return False

    # Salva diretamente no DynamoDB respeitando os tipos e nomes já tratados no Lex
    table.put_item(
        Item={
            'CPF': cpf,
            'Nome': parametros.get('nome'),
            'Idade': parametros.get('idade'),
            'Sexo': parametros.get('sexo'),
            'Telefone': parametros.get('celular'),
            'NomeResponsavel': parametros.get('nomeResponsavel'),
            'TelefoneResponsavel': parametros.get('telefoneResponsavel'),
            'PlanoSaude': parametros.get('planoSaude', 'Não informado')
        }
    )