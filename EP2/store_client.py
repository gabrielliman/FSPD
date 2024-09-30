#Aluno: Gabriel Lima Nunes
#Matrícula: 2021032048

import grpc
import store_pb2
import store_pb2_grpc
import wallet_pb2
import wallet_pb2_grpc
import sys

def run(wallet_id, wallet_server_address, store_server_address):
    # Configura os canais de comunicação para os servidores
    wallet_channel = grpc.insecure_channel(wallet_server_address)
    wallet_stub = wallet_pb2_grpc.WalletServiceStub(wallet_channel)
    store_channel = grpc.insecure_channel(store_server_address)
    store_stub = store_pb2_grpc.StoreServiceStub(store_channel)

    # Lê comandos da entrada padrão
    for line in sys.stdin:
        command = line.strip().split()
        
        if command[0] == 'C':
            # Obtém o preço do produto da loja
            price_response = store_stub.GetPrice(store_pb2.GetPriceRequest())
            print(price_response.price)

            # Cria uma ordem de pagamento no servidor de carteiras
            order_response = wallet_stub.CreatePaymentOrder(wallet_pb2.OrderRequest(wallet_id=wallet_id, amount=price_response.price))
            
            if order_response.order_id > 0:
                # Realiza a compra na loja utilizando a ordem de pagamento
                purchase_response = store_stub.Purchase(store_pb2.PurchaseRequest(order_id=order_response.order_id))
                print(purchase_response.status)
        
        elif command[0] == 'T':
            # Encerra o servidor da loja
            shutdown_response = store_stub.Shutdown(store_pb2.EndRequest())
            print(shutdown_response.store_balance, shutdown_response.wallet_shutdown_status)
            break
        
        else:
            # Ignora comandos não reconhecidos
            continue

if __name__ == '__main__':
    # Verifica se o número correto de argumentos foi passado
    if len(sys.argv) != 4:
        sys.exit(1)

    # Obtém os argumentos da linha de comando
    wallet_id = sys.argv[1]
    wallet_server_address = sys.argv[2]
    store_server_address = sys.argv[3]

    # Executa a função principal com os argumentos fornecidos
    run(wallet_id, wallet_server_address, store_server_address)
