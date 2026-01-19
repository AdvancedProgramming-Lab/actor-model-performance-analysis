import threading
import time
import math
import os
import psutil
from concurrent.futures import ThreadPoolExecutor



def calculo_simples(id_ficheiro):
    return id_ficheiro + 1


def calculo_ficheiros(id_ficheiro):
    resultado = 0
    for i in range(1, 100_000):
        resultado += math.sqrt(i) * math.sin(i + id_ficheiro)
    return resultado


def operacao_io(id_ficheiro):
    time.sleep(0.01)
    return id_ficheiro

def funcao_thread_tarefa(numero_ficheiros, funcao_trabalho):

    print(f"\n=== Thread por tarefa | {funcao_trabalho.__name__} ===")

    inicio = time.time()
    processo = psutil.Process(os.getpid())
    memoria_ant = processo.memory_info().rss / 1024 / 1024

    threads = []
    resultados = []

    def worker(id_ficheiro):
        resultados.append(funcao_trabalho(id_ficheiro))

    for i in range(numero_ficheiros):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    memoria_des = processo.memory_info().rss / 1024 / 1024
    tempo = time.time() - inicio

    print(f"Tempo de execucao: {tempo:.2f} segundos")
    print(f"Memoria acrescentada: {memoria_des - memoria_ant:.2f} MB")
    print(f"Resultados finais: {len(resultados)}")

    return tempo, memoria_des - memoria_ant

def funcao_thread_pool(numero_ficheiros, funcao_trabalho, max_workers=5):

    print(f"\n=== ThreadPool | {funcao_trabalho.__name__} (workers={max_workers}) ===")

    inicio = time.time()
    processo = psutil.Process(os.getpid())
    memoria_ant = processo.memory_info().rss / 1024 / 1024

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(funcao_trabalho, i) for i in range(numero_ficheiros)]
        resultados = [future.result() for future in futures]

    memoria_des = processo.memory_info().rss / 1024 / 1024
    tempo = time.time() - inicio

    print(f"Tempo de execucao: {tempo:.2f} segundos")
    print(f"Memoria acrescentada: {memoria_des - memoria_ant:.2f} MB")
    print(f"Resultados finais: {len(resultados)}")

    return tempo, memoria_des - memoria_ant

if __name__ == "__main__":

    numero_tarefas = 10000

    tipos_tarefa = [
        calculo_simples,
        calculo_ficheiros,
        operacao_io
    ]

    for tarefa in tipos_tarefa:
        print("\n" + "=" * 70)
        print(f"Teste com a seguinte tarefa: {tarefa.__name__}")
        print("=" * 70)

        funcao_thread_tarefa(numero_tarefas, tarefa)
        funcao_thread_pool(numero_tarefas, tarefa, max_workers=5)
