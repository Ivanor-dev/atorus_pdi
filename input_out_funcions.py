from PIL import Image
import numpy as np
import re

def image_input(file_path, convert):
    # O Pillow abre automaticamente .tif e .png 
    with Image.open(file_path) as img:
        # Força a conversão para RGB para garantir os 24 bits (8 por canal) 
        img_rgb = img.convert(convert)
        width, height = img_rgb.size
        print(f'Arquivo: {file_path} | Dimensões: {width}x{height} | Mode: {img_rgb.mode}')
        img_array = np.array(img_rgb)
    return img_array, width, height

def input_mask(mask_file):
	mask = []
	mfile = open(mask_file, 'r')
	lines = mfile.readlines()
	for i in range(len(lines)):
		line = lines[i].strip()
		values = re.split(r'\s+', line)
		for j in range(len(values)):
			value = int(values[j])
			mask.append(value)

	return mask



def salvar_imagem(img_list, filename):
    """
    Salva uma matriz de pixels (lista de listas) como imagem usando o Pillow.
    Suporta tanto imagens RGB (matriz 3D) quanto em tons de cinza (matriz 2D).
    """
    altura_out = len(img_list)
    largura_out = len(img_list[0])
    
    # Pega o primeiro pixel para checar se é uma lista/tupla (RGB) ou um int (Cinza)
    primeiro_pixel = img_list[0][0]

    if isinstance(primeiro_pixel, (list, tuple)):
        mode = 'RGB'
        # O Pillow exige uma lista plana de tuplas para RGB: [(R,G,B), (R,G,B)...]
        flat_list = [tuple(pixel) for linha in img_list for pixel in linha]
    else:
        mode = 'L' 
        # O Pillow exige uma lista plana de inteiros para tons de cinza: [val, val, val...]
        flat_list = [int(pixel) for linha in img_list for pixel in linha]

    # Cria uma imagem em branco com as dimensões corretas e insere os dados manuais
    img_out = Image.new(mode, (largura_out, altura_out))
    img_out.putdata(flat_list)
    
    img_out.save(filename)
    print(f"Imagem salva com sucesso em: {filename}")



def exibir_imagem(img_list, titulo="Imagem Processada"):
    """
    Exibe uma matriz de pixels (lista de listas) na tela.
    Suporta tanto imagens RGB (matriz 3D) quanto em tons de cinza (matriz 2D).
    """
    altura = len(img_list)
    largura = len(img_list[0])
    
    # Pega o primeiro pixel para checar se é RGB (lista/tupla) ou Cinza (int/float)
    primeiro_pixel = img_list[0][0]

    if isinstance(primeiro_pixel, (list, tuple)):
        mode = 'RGB'
        # O Pillow exige uma lista plana de tuplas para RGB
        flat_list = [tuple(pixel) for linha in img_list for pixel in linha]
    else:
        mode = 'L' 
        # O Pillow exige uma lista plana de inteiros para tons de cinza
        flat_list = [int(pixel) for linha in img_list for pixel in linha]

    # Cria uma imagem em branco e insere os dados manuais
    img_show = Image.new(mode, (largura, altura))
    img_show.putdata(flat_list)
    
    print(f"Abrindo visualizador para: {titulo}")
    # Exibe a imagem no visualizador padrão do sistema
    img_show.show(title=titulo)
