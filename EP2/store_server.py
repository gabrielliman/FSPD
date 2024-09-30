#Aluno: Gabriel Lima Nunes
#Matrícula: 2021032048

from concurrent import futures
import grpc
import store_pb2
import store_pb2_grpc
import wallet_pb2
import wallet_pb2_grpc
import threading

class StoreService(store_pb2_grpc.StoreServiceServicer):
    def __init__(self, price, wallet_server_address, vendor_wallet_id):
        self.price = price
        self.vendor_wallet_id = vendor_wallet_id
        
        # Cria um canal para comunicação com o servidor de carteiras.
        self.wallet_channel = grpc.insecure_channel(wallet_server_address)
        
        # Cria um stub para interagir com o servidor de carteiras.
        self.wallet_stub = wallet_pb2_grpc.WalletServiceStub(self.wallet_channel)
        
        self.vendor_balance = self.get_initial_balance()
        
        # Evento para sinalizar quando o servidor deve ser desligado.
        self.shutdown_event = threading.Event()

    def get_initial_balance(self):
        request = wallet_pb2.BalanceRequest(wallet_id=self.vendor_wallet_id)
        
        # Faz a chamada RPC ao servidor de carteiras para obter o saldo.
        response = self.wallet_stub.GetBalance(request)
        
        return response.balance

    def GetPrice(self, request, context):
        return store_pb2.GetPriceResponse(price=self.price)

    def Purchase(self, request, context):
        # Cria uma requisição para transferir o pagamento ao servidor de carteiras.
        transfer_request = wallet_pb2.TransferRequest(
            order_id=request.order_id,
            amount=self.price,
            target_wallet_id=self.vendor_wallet_id
        )
        try:
            # Faz a chamada RPC ao servidor de carteiras para realizar a transferência.
            transfer_response = self.wallet_stub.Transfer(transfer_request)
            
            if transfer_response.status == 0:
                self.vendor_balance += self.price
                
            return store_pb2.PurchaseResponse(status=transfer_response.status)
        
        except grpc.RpcError:
            # Se houver um erro na comunicação com o servidor de carteiras, retorna status -9.
            return store_pb2.PurchaseResponse(status=-9)

    def Shutdown(self, request, context):
        shutdown_response = self.wallet_stub.EndExecution(wallet_pb2.EndRequest())
        # Sinaliza que o servidor deve ser desligado.
        self.shutdown_event.set()
        
        # Retorna o saldo final do vendedor e o status de desligamento (0 indica sucesso).
        return store_pb2.EndResponse(
            store_balance=self.vendor_balance,
            wallet_shutdown_status=shutdown_response.pending_orders
        )

def serve(price, port, vendor_wallet_id, wallet_server_address):
    # Cria o servidor gRPC com um pool de threads para processamento das requisições.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    store_service = StoreService(price, wallet_server_address, vendor_wallet_id)
    
    # Adiciona o serviço da loja ao servidor gRPC.
    store_pb2_grpc.add_StoreServiceServicer_to_server(store_service, server)
    
    # Define a porta na qual o servidor escutará as conexões.
    server.add_insecure_port(f'[::]:{port}')
    
    server.start()
    print(f"Store server started on port {port}")

    # Aguarda o evento de desligamento ser sinalizado.
    store_service.shutdown_event.wait()

    print("Shutting down store server...")
    server.stop(0)

if __name__ == '__main__':
    import sys
    price = int(sys.argv[1])
    port = int(sys.argv[2])
    vendor_wallet_id = sys.argv[3]
    wallet_server_address = sys.argv[4]
    
    # Chama a função serve para iniciar o servidor da loja com os argumentos fornecidos.
    serve(price, port, vendor_wallet_id, wallet_server_address)
