import time
import math
import os
import psutil
import pykka

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

class CalculadorActor(pykka.ThreadingActor):
    def calcular(self, funcao, id_ficheiro):
        return funcao(id_ficheiro)
    
def funcao_actor_model(numero_ficheiros, funcao_trabalho, numero_atores=5):
    print(f"\n=== Processamento de {numero_ficheiros} ficheiros com ACTOR MODEL (atores={numero_atores}) ===")
    
    inicio = time.time()
    processo = psutil.Process(os.getpid())
    memoria_ant = processo.memory_info().rss / 1024 / 1024  # MB

    # Criar atores
    atores = [CalculadorActor.start() for _ in range(numero_atores)]

    # Enviar mensagens (round-robin)
    futures = []
    for i in range(numero_ficheiros):
        ator = atores[i % numero_atores]
        futures.append(ator.ask({"cmd": "calcular", "funcao": funcao_trabalho, "id": i}))

    # Recolher resultados
    resultados = [fut for fut in futures]

    # Parar atores
    for ator in atores:
        ator.stop()

    memoria_des = processo.memory_info().rss / 1024 / 1024  # MB
    tempo_processo = time.time() - inicio

    print(f"Processamento completo em: {tempo_processo:.2f} segundos")
    print(f"Memoria antes do processamento: {memoria_ant:.2f} MB")
    print(f"Memoria depois do processamento: {memoria_des:.2f} MB")
    print(f"Memoria acrescentada: {memoria_des - memoria_ant:.2f} MB")
    print(f"Resultados finais: {len(resultados)}")

    return tempo_processo, memoria_des - memoria_ant


if __name__ == "__main__":
    numero_tarefas = 100000

    tipos_tarefa = [
        calculo_simples,
        calculo_ficheiros,
        operacao_io
    ]

    for tarefa in tipos_tarefa:
        print("\n" + "=" * 60)
        print(f"TESTE COM TAREFA: {tarefa.__name__}")
        print("=" * 60)

        funcao_actor_model(numero_tarefas, tarefa, numero_atores=5)