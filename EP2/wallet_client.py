#Aluno: Gabriel Lima Nunes
#Matrícula: 2021032048

import grpc
import wallet_pb2
import wallet_pb2_grpc
import sys

def run(wallet_id, server_address):
    # Cria um canal de comunicação inseguro com o endereço do servidor
    channel = grpc.insecure_channel(server_address)
    # Cria um stub para o serviço de carteiras
    stub = wallet_pb2_grpc.WalletServiceStub(channel)

    for line in sys.stdin:
        command = line.strip().split()
        if command[0] == 'S':
            # Comando 'S' para obter o saldo da carteira
            # Faz uma solicitação para obter o saldo da carteira e imprime o saldo retornado
            response = stub.GetBalance(wallet_pb2.BalanceRequest(wallet_id=wallet_id))
            print(response.balance)
        elif command[0] == 'O':
            # Comando 'O' para criar uma ordem de pagamento
            amount = int(command[1])
            # Faz uma solicitação para criar uma ordem de pagamento e imprime o ID da ordem retornado ou codigo de erro
            response = stub.CreatePaymentOrder(wallet_pb2.OrderRequest(wallet_id=wallet_id, amount=amount))
            print(response.order_id)
        elif command[0] == 'X':
            # Comando 'X' para realizar uma transferência
            order_id = int(command[1])
            amount = int(command[2])
            target_wallet_id = command[3]
            # Faz uma solicitação para realizar a transferência e imprime o status retornado
            response = stub.Transfer(wallet_pb2.TransferRequest(order_id=order_id, amount=amount, target_wallet_id=target_wallet_id))
            print(response.status)
        elif command[0] == 'F':
            # Comando 'F' para finalizar a execução e obter o estado final das carteiras
            # Faz uma solicitação para encerrar a execução e obtém a resposta
            response = stub.EndExecution(wallet_pb2.EndRequest())
            # Imprime o número de ordens de pagamento pendentes
            print(response.pending_orders)
            break  # Encerra o loop e finaliza o programa

if __name__ == '__main__':
    wallet_id = sys.argv[1]
    server_address = sys.argv[2]
    run(wallet_id, server_address)
