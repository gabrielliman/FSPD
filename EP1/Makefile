# Comportamento padrão é 'build'
.DEFAULT_GOAL := build

# Compilador e opções
CC := g++
CFLAGS := -std=c++11 -Wall -Wextra -pthread

# Diretórios
SRC_DIR := .
BUILD_DIR := .

# Nome do executável
TARGET := ex1

# Fontes
SRCS := $(wildcard $(SRC_DIR)/*.cpp)
OBJS := $(SRCS:.cpp=.o)

# Regras
.PHONY: clean build

clean:
	@echo "Removendo arquivos temporários e executáveis..."
	@rm -rf $(TARGET) $(OBJS)

build: $(TARGET)

$(TARGET): $(OBJS)
	@echo "Compilando e gerando o executável $@..."
	@$(CC) $(CFLAGS) $^ -o $@

%.o: %.cpp
	@echo "Compilando $<..."
	@$(CC) $(CFLAGS) -c $< -o $@
