#Aluno: Gabriel Lima Nunes
#Matrícula: 2021032048

PROTOC_GEN_PYTHON=python3 -m grpc_tools.protoc

# Default target to generate stubs
all: stubs

# Rule to generate Python stubs from proto files
stubs: wallet_pb2.py store_pb2.py

wallet_pb2.py: wallet.proto
	$(PROTOC_GEN_PYTHON) --proto_path=. --python_out=. --grpc_python_out=. wallet.proto

store_pb2.py: store.proto
	$(PROTOC_GEN_PYTHON) --proto_path=. --python_out=. --grpc_python_out=. store.proto

# Clean up all generated files
clean:
	rm -f *_pb2.py
	rm -f *_pb2_grpc.py
	rm -f -r __pycache__
# Run the wallet server
run_serv_banco: stubs
	python3 wallet_server.py $(arg1)

# Run the wallet client
run_cli_banco: stubs
	python3 wallet_client.py $(arg1) $(arg2)

# Run the store server
run_serv_loja: stubs
	python3 store_server.py $(arg1) $(arg2) $(arg3) $(arg4)

# Run the store client
run_cli_loja: stubs
	python3 store_client.py $(arg1) $(arg2) $(arg3)

.PHONY: all stubs clean run_serv_banco run_cli_banco run_serv_loja run_cli_loja
