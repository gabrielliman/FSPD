import os

# Diretório de entrada
input_dir = "./inputs"

# Diretório de saída
output_dir = "./outputs"

# Lista todos os arquivos na pasta de entrada
input_files = os.listdir(input_dir)

# Executa o comando para cada arquivo de entrada
for input_file in input_files:
    # Verifica se o arquivo termina com ".in"
    if input_file.endswith(".in"):
        # Monta o caminho completo para o arquivo de entrada
        input_path = os.path.join(input_dir, input_file)
        
        # Monta o caminho completo para o arquivo de saída (baseado no nome do arquivo de entrada)
        output_file = input_file.replace(".in", ".out")
        output_path = os.path.join(output_dir, output_file)
        
        # Executa o comando
        print(f"running {input_file}")
        os.system(f"./ex1 < {input_path} > {output_path}")
