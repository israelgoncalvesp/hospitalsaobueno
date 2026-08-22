import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_PACIENTES', 'SaoBueno_Pacientes')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print("EVENTO COMPLETO RECEBIDO DO CONNECT:", json.dumps(event))
    
    # 1. Busca os parâmetros vindos do bloco do Connect ou de testes manuais
    # No Connect, o bloco passa os atributos em ContactData -> Attributes ou Parameters
    details = event.get('Details', {})
    parameters = details.get('Parameters', {})
    attributes = details.get('ContactData', {}).get('Attributes', {})
    
    # Unifica tudo para garantir que pega os dados de onde vierem
    dados = {**attributes, **parameters, **event}
    
    # 2. Captura do CPF (Chave Primária)
    cpf = dados.get('cpf')
    
    if not cpf:
        print("ERRO: CPF não foi encontrado nos parâmetros enviados.")
        return {
            "status": "erro",
            "mensagem": "CPF nao informado"
        }
    
    try:
        # 3. Salva no DynamoDB
        table.put_item(
            Item={
                'CPF': str(cpf),
                'Nome': str(dados.get('nome', '')),
                'Telefone': str(dados.get('telefone', '')),
                'NomeResponsavel': str(dados.get('nomeResponsavel', '')),
                'TelefoneResponsavel': str(dados.get('telefoneResponsavel', ''))
            }
        )
        print(f"SUCESSO: Paciente CPF {cpf} cadastrado com êxito!")
        
        # 4. Retorno VÁLIDO para o Amazon Connect
        return {
            "status": "sucesso",
            "mensagem": "Paciente cadastrado com sucesso"
        }
        
    except Exception as e:
        print("ERRO AO SALVAR NO DYNAMODB:", str(e))
        return {
            "status": "erro",
            "mensagem": str(e)
        }
