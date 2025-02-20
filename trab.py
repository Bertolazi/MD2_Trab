def encontrar_pontos_na_curva(a, b, p):
    """
    Encontra pontos na curva elíptica y² ≡ x³ + ax + b (mod p) de forma otimizada
    usando o fato de que y² é um quadrado perfeito módulo p
    Retorna uma lista de duplas (x,y) representando os pontos
    """
    pontos = []
    
    # Pré-computar quadrados módulo p para melhor custo da função
    quadrados = set(pow(i, 2, p) for i in range((p + 1) // 2))
    
    for x in range(p):
        # Calcular lado direito da equação: x³ + ax + b
        rhs = (pow(x, 3, p) + (a * x) % p + b) % p
        
        # Verificar se rhs é um resíduo quadrático módulo p
        if rhs in quadrados:
            # Encontrar y tal que y² ≡ rhs (mod p)
            for y in range(p):
                if pow(y, 2, p) == rhs:
                    pontos.append((x, y))
                    if y != 0:  # Se y ≠ 0, -y também é solução
                        pontos.append((x, p - y))
                    break
    
    return pontos


def soma_pontos(P, Q, a, p):
    """ 
    Soma dois pontos na curva elíptica sobre um campo finito 
    Usa as fórmulas:
        Para pontos diferentes m = (y2-y1)/(x2-x1)
        Para pontos duplicados m = (2x1^2+a)/2y1
    Calcula o novo ponto (x3, y3), onde:
        x3 = m^2 - x1 - x2
        y3 = m(x1-x3) - y1
    """
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    
    if P == Q:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        if x1 == x2:
            return None
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p

    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)


def multiplicar_ponto(P, k, a, p):
    """ 
    Multiplica um ponto P por um escalar k usando o método de duplicação e adição 
    Implementando a multiplicação escalar do ponto
    Usa método de duplicação e adição (double and add)
    Mais eficiente que somar P consigo mesmo k vezes
    """
    R = None
    Q = P
    while k:
        if k & 1:
            R = soma_pontos(R, Q, a, p)
        Q = soma_pontos(Q, Q, a, p)
        k >>= 1
    return R


def calcular_ordem(P, a, p):
    """ Calcula a ordem de um ponto P na curva elíptica """
    Q = P
    ordem = 1
    while Q is not None:
        Q = soma_pontos(Q, P, a, p)
        ordem += 1
        if Q == P:  # Se voltamos ao ponto inicial, algo deu errado
            return float('inf')
    return ordem


def encontrar_maiores_ordens(pontos, a, p):
    """ Encontra até 50 pontos de maior ordem na curva """
    pontos_ordenados = sorted(pontos, key=lambda P: calcular_ordem(P, a, p), reverse=True)
    return pontos_ordenados[:50]


if __name__ == "__main__":
    """
    Recebe os parâmetros da curva (a, b, p)
    Encontra todos os pontos da curva
    Identifica pontos de maior ordem
    Permite que escolha manual ou automática do ponto gerador
    Implementa o protocolo Diffie-Hellman
        Gera chaves públicas: A = mG e B = nG
        Calcula chaves compartilhadas: R = mB e S = nA
        Verifica se R = S (deve ser igual pela propriedade comutativa)
    """
    a = int(input("Digite o valor de a: "))
    b = int(input("Digite o valor de b: "))
    p = int(input("Digite um número primo p: "))
    
    print("\nBuscando pontos na curva elíptica...\n")
    pontos = encontrar_pontos_na_curva(a, b, p)
    print(f"Encontrados {len(pontos)} pontos na curva.\n")
    
    if not pontos:
        print("Nenhum ponto encontrado. Verifique os parâmetros e tente novamente.")
        exit()
    
    print("Pontos encontrados:")
    maiores_pontos = encontrar_maiores_ordens(pontos, a, p)
    for i, ponto in enumerate(maiores_pontos):
        print(f"G{i+1} = {ponto}")
    
    escolha = input("\nDeseja inserir um ponto gerador manualmente? (s/n): ").strip().lower()
    if escolha == 's':
        x = int(input("Digite a coordenada x do ponto gerador: "))
        y = int(input("Digite a coordenada y do ponto gerador: "))
        G = (x, y)
        print(f"Usando ponto gerador fornecido: G = {G}\n")
    else:
        print("\nDeterminando o ponto de maior ordem...\n")
        G = maiores_pontos[0] if maiores_pontos else None
        print(f"Ponto gerador de maior ordem: G = {G}\n")
    
    m = int(input("Digite a chave privada m: "))
    n = int(input("Digite a chave privada n: "))
    
    A = multiplicar_ponto(G, m, a, p)
    B = multiplicar_ponto(G, n, a, p)
    print(f"A = {A}, B = {B}\n")
    
    R = multiplicar_ponto(B, m, a, p)
    S = multiplicar_ponto(A, n, a, p)
    print(f"R = {R}, S = {S}\n")
    
    if R == S:
        print("O programa está OK: R = S")
    else:
        print("Erro: R != S")