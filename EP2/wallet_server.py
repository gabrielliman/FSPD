#Aluno: Gabriel Lima Nunes
#Matrícula: 2021032048

import grpc
from concurrent import futures
import wallet_pb2
import wallet_pb2_grpc
import sys
import threading

class WalletService(wallet_pb2_grpc.WalletServiceServicer):
    def __init__(self):
        self.wallets = {} 
        self.orders = {} 
        self.order_id_counter = 1  
        self.shutdown_event = threading.Event() 

    def GetBalance(self, request, context):
        # Recebe uma solicitação para obter o saldo de uma carteira
        wallet_id = request.wallet_id
        if wallet_id in self.wallets:
            # Se a carteira for encontrada, retorna o saldo
            return wallet_pb2.BalanceResponse(balance=self.wallets[wallet_id])
        else:
            # Se a carteira não for encontrada, retorna saldo -1
            return wallet_pb2.BalanceResponse(balance=-1)

    def CreatePaymentOrder(self, request, context):
        # Recebe uma solicitação para criar uma ordem de pagamento
        wallet_id = request.wallet_id
        amount = request.amount
        if wallet_id not in self.wallets:
            # Se a carteira não existir, retorna um ID de ordem inválido (-1)
            return wallet_pb2.OrderResponse(order_id=-1)
        if self.wallets[wallet_id] < amount:
            # Se o saldo da carteira for insuficiente, retorna um ID de ordem inválido (-2)
            return wallet_pb2.OrderResponse(order_id=-2)
        self.wallets[wallet_id] -= amount
        order_id = self.order_id_counter
        self.orders[order_id] = amount
        self.order_id_counter += 1
        # Retorna o ID da ordem criada
        return wallet_pb2.OrderResponse(order_id=order_id)

    def Transfer(self, request, context):
        # Recebe uma solicitação para transferir um valor entre carteiras
        order_id = request.order_id
        amount = request.amount
        target_wallet_id = request.target_wallet_id
        if order_id not in self.orders:
            # Se a ordem não existir, retorna status -1
            return wallet_pb2.TransferResponse(status=-1)
        if self.orders[order_id] != amount:
            # Se o valor da ordem não corresponder ao valor solicitado, retorna status -2
            return wallet_pb2.TransferResponse(status=-2)
        if target_wallet_id not in self.wallets:
            # Se a carteira de destino não existir, retorna status -3
            return wallet_pb2.TransferResponse(status=-3)
        
        self.wallets[target_wallet_id] += amount
        del self.orders[order_id]
        # Retorna status 0 para indicar sucesso
        return wallet_pb2.TransferResponse(status=0)

    def EndExecution(self, request, context):
        # Imprime o saldo de todas as carteiras
        for wallet_id, balance in self.wallets.items():
            print(f"{wallet_id} {balance}")
        
        # Sinaliza o evento de desligamento para que o servidor possa parar
        self.shutdown_event.set()
        # Retorna o número de ordens pendentes
        return wallet_pb2.EndResponse(pending_orders=len(self.orders))

def serve():
    port = sys.argv[1]
    
    # Instancia o servidor gRPC com um pool de threads para lidar com as solicitações
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    wallet_servicer = WalletService()  # Cria a instância do WalletService

    for line in sys.stdin:
        line = line.strip() 
        if line == "":
            break 
        else:
            # Divide a linha em uma string (ID da carteira) e um inteiro (saldo)
            parts = line.rsplit(maxsplit=1)
            wallet_servicer.wallets[parts[0]] = int(parts[1])
    
    # Adiciona o WalletService ao servidor gRPC
    wallet_pb2_grpc.add_WalletServiceServicer_to_server(wallet_servicer, server)
    
    # Configura o servidor para escutar na porta especificada
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    # Aguarda o evento de desligamento para parar o servidor
    wallet_servicer.shutdown_event.wait()
    
    server.stop(0)

if __name__ == '__main__':
    serve()
