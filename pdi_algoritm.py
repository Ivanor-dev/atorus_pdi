
def apply_matrix_atrous_manual(img_list, mask, r, stride, activation):
    # img_list é uma lista de listas 3D: [altura][largura][canal]
    h_in = len(img_list)
    w_in = len(img_list[0])
    channels = len(img_list[0][0])
    
    m = len(mask)    # Altura da máscara
    n = len(mask[0]) # Largura da máscara

    # Cálculo das dimensões de saída sem padding
    h_out = (h_in - (m - 1) * r - 1) // stride + 1
    w_out = (w_in - (n - 1) * r - 1) // stride + 1

    # Inicializa matriz de resultado com zeros
    image_result = [[[0.0 for _ in range(channels)] for _ in range(w_out)] for _ in range(h_out)]

    for c in range(channels):
        for y in range(h_out):
            for x in range(w_out):
                soma = 0.0
                for i in range(m):
                    for j in range(n):
                        # Cálculo do pixel correspondente com Dilatação (r) e Stride
                        py = y * stride + i * r
                        px = x * stride + j * r
                        soma += img_list[py][px][c] * mask[i][j]

                # Função de Ativação
                if activation == "ReLU":
                    image_result[y][x][c] = max(0.0, soma)
                else:
                    image_result[y][x][c] = soma

    return image_result


def expandir_histograma_manual(img_list):
    # 1. Aplicar valor absoluto e identificar min/max manualmente
    # Assume-se que img_list pode ser 2D (Cinza) ou 3D (RGB)
    
    # Inicializa com valores extremos para comparação
    max_val = -float('inf')
    min_val = float('inf')
    
    # Criar uma cópia com valores absolutos para não alterar a original
    # e já buscar o mínimo e máximo em uma única passada
    img_abs = []
    
    for row in img_list:
        new_row = []
        for pixel in row:
            # Trata se o pixel for um valor único (escala de cinza) ou lista (RGB)
            if isinstance(pixel, (list, tuple)):
                new_pixel = [abs(canal) for canal in pixel]
                for canal_val in new_pixel:
                    if canal_val < min_val: min_val = canal_val
                    if canal_val > max_val: max_val = canal_val
            else:
                new_pixel = abs(pixel)
                if new_pixel < min_val: min_val = new_pixel
                if new_pixel > max_val: max_val = new_pixel
            
            new_row.append(new_pixel)
        img_abs.append(new_row)

    # 2. Expansão para o intervalo [0, 255]
    diff = max_val - min_val
    resultado = []
    
    for row in img_abs:
        new_row = []
        for pixel in row:
            if diff == 0:
                # Caso a imagem seja de uma cor só, evita divisão por zero
                if isinstance(pixel, list):
                    new_row.append([0 for _ in pixel])
                else:
                    new_row.append(0)
            else:
                if isinstance(pixel, list):
                    # Processa cada canal RGB individualmente
                    pixel_expandido = [int(255 * (val - min_val) / diff) for val in pixel]
                    new_row.append(pixel_expandido)
                else:
                    # Processa valor único
                    val_expandido = int(255 * (pixel - min_val) / diff)
                    new_row.append(val_expandido)
        resultado.append(new_row)
        
    return resultado


def processar_sobel_manual(gx, gy, ganho=4.0):
    h = len(gx)
    w = len(gx[0])
    
    is_rgb = isinstance(gx[0][0], list)
    canais = len(gx[0][0]) if is_rgb else 1
    
    # A matriz de magnitude e resultado final serão SEMPRE 2D (tons de cinza)
    magnitude = [[0.0 for _ in range(w)] for _ in range(h)]
    resultado_final = [[0 for _ in range(w)] for _ in range(h)]
    
    max_val = -float('inf')
    min_val = float('inf')

    # 1. Calcular Magnitude Combinada (Média dos canais)
    for y in range(h):
        for x in range(w):
            if is_rgb:
                soma_quadrados = 0.0
                for c in range(canais):
                    val_gx = gx[y][x][c]
                    val_gy = gy[y][x][c]
                    soma_quadrados += (val_gx**2 + val_gy**2)
                
                # Tira a média entre as cores e aplica a raiz quadrada
                mag = (soma_quadrados / canais)**0.5
            else:
                val_gx = gx[y][x]
                val_gy = gy[y][x]
                mag = (val_gx**2 + val_gy**2)**0.5
            
            magnitude[y][x] = mag
            
            if mag > max_val: max_val = mag
            if mag < min_val: min_val = mag

    # 2. Expansão de Histograma com Ganho de Contraste
    diff = max_val - min_val
    
    for y in range(h):
        for x in range(w):
            if diff == 0:
                resultado_final[y][x] = 0
            else:
                valor_expandido = (255.0 * (magnitude[y][x] - min_val) / diff)
                valor_com_ganho = valor_expandido * ganho
                
                # Salva como um único inteiro (escala de cinza puro)
                resultado_final[y][x] = int(max(0, min(255, valor_com_ganho)))
                
    return resultado_final