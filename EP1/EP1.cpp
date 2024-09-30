#include <iostream>
#include <vector>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <algorithm> // Necessário para std::remove

using namespace std;

#define MAX_N 20 // Dimensão máxima do tabuleiro

// Estrutura que representa uma posição no tabuleiro e o tempo que deve ser gasto nela
struct Position {
    int x, y, time;
};

// Estrutura que representa as informações de uma thread
struct ThreadInfo {
    int tid; // Identificador da thread
    int group; // Grupo da thread
    vector<Position> path; // Caminho que a thread deve seguir
};

// Matrizes para mutexes e variáveis de condição, uma para cada posição do tabuleiro
pthread_mutex_t boardMutex[MAX_N][MAX_N];
pthread_cond_t boardCond[MAX_N][MAX_N];
int occupancyCount[MAX_N][MAX_N]; // Número de threads ocupando cada posição
vector<int> occupyingGroups[MAX_N][MAX_N]; // Grupos das threads ocupando cada posição
int N, n_threads; // Dimensão do tabuleiro e número de threads

// Função fornecida que faz a thread "dormir" pelo tempo especificado em décimos de segundo
void passa_tempo(int tid, int x, int y, int decimos)
{
    struct timespec zzz, agora;
    static struct timespec inicio = {0, 0};
    int tstamp;

    if ((inicio.tv_sec == 0) && (inicio.tv_nsec == 0)) {
        clock_gettime(CLOCK_REALTIME, &inicio);
    }

    zzz.tv_sec = decimos / 10;
    zzz.tv_nsec = (decimos % 10) * 100L * 1000000L;

    clock_gettime(CLOCK_REALTIME, &agora);
    tstamp = (10 * agora.tv_sec + agora.tv_nsec / 100000000L)
        - (10 * inicio.tv_sec + inicio.tv_nsec / 100000000L);

    printf("%3d [ %2d @(%2d,%2d) z%4d\n", tstamp, tid, x, y, decimos);

    nanosleep(&zzz, NULL);

    clock_gettime(CLOCK_REALTIME, &agora);
    tstamp = (10 * agora.tv_sec + agora.tv_nsec / 100000000L)
        - (10 * inicio.tv_sec + inicio.tv_nsec / 100000000L);

    printf("%3d ) %2d @(%2d,%2d) z%4d\n", tstamp, tid, x, y, decimos);
}

// Função que verifica se a posição (x, y) pode ser ocupada pela thread de um certo grupo
bool can_enter(int group, int x, int y) {
    // Verifica se a posição está vazia ou ocupada por apenas uma thread de um grupo diferente
    if (occupancyCount[x][y] == 0) {
        return true;
    } else if (occupancyCount[x][y] == 1) {
        return occupyingGroups[x][y][0] != group;
    }
    return false;
}

// Função que faz a thread entrar na posição (x, y)
void entra(int group, int x, int y) {
    pthread_mutex_lock(&boardMutex[x][y]);

    // Espera enquanto a posição está ocupada por duas threads ou por uma thread do mesmo grupo
    while (!can_enter(group, x, y)) {
        pthread_cond_wait(&boardCond[x][y], &boardMutex[x][y]);
    }

    // Marca a posição como ocupada e registra o grupo
    occupancyCount[x][y]++;
    occupyingGroups[x][y].push_back(group);

    pthread_mutex_unlock(&boardMutex[x][y]);
}

// Função que faz a thread sair da posição (x, y)
void sai(int group, int x, int y) {
    pthread_mutex_lock(&boardMutex[x][y]);

    // Atualiza a contagem de ocupação e remove o grupo da lista
    occupancyCount[x][y]--;
    auto it = remove(occupyingGroups[x][y].begin(), occupyingGroups[x][y].end(), group);
    occupyingGroups[x][y].erase(it, occupyingGroups[x][y].end());

    // Notifica outras threads esperando para entrar nesta posição
    pthread_cond_broadcast(&boardCond[x][y]);

    pthread_mutex_unlock(&boardMutex[x][y]);
}

// Função executada por cada thread
void* thread_func(void* arg) {
    ThreadInfo* info = (ThreadInfo*)arg;
    int tid = info->tid;
    int group = info->group;
    vector<Position> path = info->path;

    if (path.empty()) {
        return NULL; // Retorna imediatamente se o caminho estiver vazio
    }

    // Percorre o caminho especificado para a thread
    for (size_t i = 0; i < path.size(); ++i) {
        int x = path[i].x;
        int y = path[i].y;
        int time = path[i].time;

        entra(group, x, y);

        if (i > 0) {
            // Sai da posição anterior depois de entrar na nova posição
            int prev_x = path[i - 1].x;
            int prev_y = path[i - 1].y;
            sai(group, prev_x, prev_y);
        }

        passa_tempo(tid, x, y, time);
    }

    // Sai da última posição do caminho
    int last_x = path.back().x;
    int last_y = path.back().y;
    sai(group, last_x, last_y);

    return NULL;
}

int main() {
    cin >> N >> n_threads;

    vector<ThreadInfo> threadsInfo(n_threads);
    pthread_t threads[n_threads];

    // Lê as informações de cada thread da entrada padrão
    for (int i = 0; i < n_threads; ++i) {
        ThreadInfo& info = threadsInfo[i];
        cin >> info.tid >> info.group;
        int path_length;
        cin >> path_length;

        for (int j = 0; j < path_length; ++j) {
            Position pos;
            cin >> pos.x >> pos.y >> pos.time;
            info.path.push_back(pos);
        }
    }

    // Inicializa mutexes e variáveis de condição
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            pthread_mutex_init(&boardMutex[i][j], NULL);
            pthread_cond_init(&boardCond[i][j], NULL);
            occupancyCount[i][j] = 0; // Inicializa a posição como vazia
        }
    }

    // Cria as threads
    for (int i = 0; i < n_threads; ++i) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&threadsInfo[i]);
    }

    // Espera as threads terminarem
    for (int i = 0; i < n_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Destroi mutexes e variáveis de condição
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            pthread_mutex_destroy(&boardMutex[i][j]);
            pthread_cond_destroy(&boardCond[i][j]);
        }
    }

    return 0;
}
