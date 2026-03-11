import numpy as np
import json

from input_out_funcions import *
from pdi_algoritm import *

def main():
    # 1. Carregar configurações do arquivo (Requisito 3) 
    photo_slected = str(input("write the location of photo to apply mask: "))
    mask_config_filter = str(input("write the location of mask configure path: "))
    show_image = input("show image (y)es or (n)o: ").strip().lower()

    with open(mask_config_filter, 'r') as f:
        config = json.load(f)
    
    mask = np.array(config['mask'])
    
    num_of_loops = 1
    converter_color = 'RGB'
    # Normalização para o Gaussiano (soma dos pesos = 256)
    if "Gaussiano" in config.get("name", ""): 
        mask_normalizada = []
        
        # Verifica se a máscara está envolvida em uma camada extra de lista (3D)
        if isinstance(config['mask'][0][0], list):
            matriz_alvo = config['mask'][0] # Extrai a matriz real
            for linha in matriz_alvo:
                nova_linha = [valor / 256.0 for valor in linha]
                mask_normalizada.append(nova_linha)
            mask = [mask_normalizada] # Devolve a camada extra para não quebrar o resto do código
            
        else:
            # Estrutura 2D normal
            for linha in config['mask']:
                nova_linha = [valor / 256.0 for valor in linha]
                mask_normalizada.append(nova_linha)
            mask = mask_normalizada

    if "Sobel" in config.get("name", ""):
        num_of_loops = 2
        


    # 2. Carregar a imagem (funciona para .png ou .tiff) 
    img_array, w, h = image_input(photo_slected, converter_color) # Troque para sua imagem .tiff se preferir
    

    # 3. Aplicar a Correlação Atrous (Dilatada)
    resultado = []
    for i in range(num_of_loops):

        res = apply_matrix_atrous_manual(
            img_array, 
            mask[i], 
            config['r'], 
            config['stride'], 
            config['activation']
        )

        resultado.append(res)

    # 4. Tratamento Especial para Sobel
    if "Sobel" in config.get("name", ""):

        resultado_final = processar_sobel_manual(resultado[0], resultado[1])
    else:
        dados_originais = resultado[0]
        altura = len(dados_originais)
        largura = len(dados_originais[0])
        canais = len(dados_originais[0][0])

        resultado_final = []

        for y in range(altura):
            linha = []
            for x in range(largura):
                # Se tiver apenas 1 canal (ex: escala de cinza), extraímos o valor (Squeeze)
                if canais == 1:
                    valor = dados_originais[y][x][0]
                    # Simulação do np.clip(valor, 0, 255) e astype(uint8)
                    valor_clamped = int(max(0, min(255, valor)))
                    linha.append(valor_clamped)
                else:
                    # Se for RGB, processamos cada canal separadamente
                    pixel_rgb = []
                    for c in range(canais):
                        valor = dados_originais[y][x][c]
                        valor_clamped = int(max(0, min(255, valor)))
                        pixel_rgb.append(valor_clamped)
                    linha.append(pixel_rgb)
            resultado_final.append(linha)


    # 5. Salvar o resultado (Sem usar padding!)
    nome_arquivo_saida = f"resultado_{photo_slected}_{config.get('name', 'filtro')}.png"
    salvar_imagem(resultado_final, nome_arquivo_saida)

    if show_image == 'y':
        exibir_imagem(resultado_final, titulo=config.get('name', 'Filtro Aplicado'))
    
    print(f"Teste com {config.get('name')} finalizado com sucesso!")



if __name__ == "__main__":
    main()