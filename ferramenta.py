from PIL import Image
import os

# Pastas de entrada e saída
input_folder = "C:/Users/RAINNER/Downloads/teste/teste2/Hero Knight/Sprites/HeroKnight/teste"
output_folder = "C:/Users/RAINNER/Downloads/teste/teste2/Hero Knight/Sprites/HeroKnight/teste/teste_left"

# Criar a pasta de saída se não existir
os.makedirs(output_folder, exist_ok=True)

# Processar todas as imagens da pasta
for filename in os.listdir(input_folder):
    if filename.endswith((".png", ".jpg", ".jpeg")):  # Filtra formatos de imagem
        old_path = os.path.join(input_folder, filename)

        # Converter nome para minúsculas
        lowercase_filename = filename.lower()
        lowercase_path = os.path.join(input_folder, lowercase_filename)

        # Renomear o arquivo para minúsculas se necessário
        if filename != lowercase_filename:
            os.rename(old_path, lowercase_path)

        # Abrir imagem
        img = Image.open(lowercase_path)
        flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)  # Flip horizontal

        # Separar nome e extensão
        name, ext = os.path.splitext(lowercase_filename)
        new_filename = f"{name}_right{ext}"  # Adicionar _right antes da extensão
        new_path = os.path.join(output_folder, new_filename)

        # Salvar imagem modificada
        flipped_img.save(new_path)

        print(f"Processado: {lowercase_filename} -> {new_filename}")


print("Renomeação e flip concluídos!")
