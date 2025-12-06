import mysql.connector
from mysql.connector import Error


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}


def main():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS banco;")
        cursor.execute("USE banco;")

        # It's helpful to temporarily disable foreign key checks when creating or
        # re-creating schema in case of residual inconsistent data from prior runs.
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

        # Create users table first (so foreign keys referencing it succeed)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(200),
                email VARCHAR(100),
                cpf VARCHAR(14) UNIQUE,
                senha VARCHAR(100),
                planeta VARCHAR(45),
                logado BOOLEAN DEFAULT FALSE
            ) ENGINE=InnoDB;
            """
        )

        # Create heroes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS herois (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                classe VARCHAR(100) NOT NULL,
                nivel INT NOT NULL DEFAULT 1,
                imagem_url TEXT,
                habilidades TEXT,
                forca INT NOT NULL DEFAULT 0,
                defesa INT NOT NULL DEFAULT 0,
                velocidade INT NOT NULL DEFAULT 0
            ) ENGINE=InnoDB;
            """
        )

        # Create equipes (teams) table referencing usuarios
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS equipes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                nome VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """
        )

        # Create linking table between equipes and herois
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS herois_equipe (
                id INT AUTO_INCREMENT PRIMARY KEY,
                equipe_id INT NOT NULL,
                heroi_id INT NOT NULL,
                FOREIGN KEY (equipe_id) REFERENCES equipes(id) ON DELETE CASCADE,
                FOREIGN KEY (heroi_id) REFERENCES herois(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """
        )

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

        # Insert sample heroes only if table is empty
        cursor.execute("SELECT COUNT(*) FROM herois;")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                """
                INSERT INTO herois (nome, classe, nivel, imagem_url, habilidades, forca, defesa, velocidade)
                VALUES
                ('Superman', 'Kryptoniano', 50, 'https://preview.redd.it/what-about-superman-do-you-think-makes-him-the-greatest-v0-08c9a7jru54d1.jpeg?width=1080&crop=smart&auto=webp&s=2805c3c1d1d78470e1bf1b19a7b537685652b824', 'Visão de calor, voo, superforça', 50, 45, 48),
                ('Batman', 'Justiceiro', 30, 'https://admin.cnnbrasil.com.br/wp-content/uploads/sites/12/2024/09/quadrinho-de-batman.jpg?w=1200&h=900&crop=1', 'Artes marciais, furtividade, gadgets', 20, 25, 22),
                ('Mulher-Maravilha', 'Amazona', 45, 'https://s3.amazonaws.com/blog.dentrodahistoria.com.br/wp-content/uploads/2021/10/19174636/thumb_aniversario_mulher_maravilha-800x500.jpg', 'Laço da Verdade, superforça, combate avançado', 48, 42, 35),
                ('Homem-Aranha', 'Herói Aracnídeo', 28, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSsUr0-yCHjqtbx8QXk57a60Me0amG4PxM_Pg&s', 'Sentido aranha, teias, agilidade extrema', 18, 16, 30),
                ('Capitão América', 'Soldado Super-Humano', 32, 'https://acdn-us.mitiendanube.com/stores/001/340/682/products/quadro-decorativo-marvel-super-heroi-capitao-america1-61c2879e9733ae64fc16619582803880-1024-1024.jpg', 'Escudo indestrutível, liderança, força aprimorada', 22, 30, 20),
                ('Thor', 'Deus do Trovão', 48, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnkH0lYyVnPU1SitkWWvManHeUg6FSNEEY8Q&s', 'Relâmpagos, voo, força divina', 50, 40, 30),
                ('Hulk', 'Colosso Gama', 50, 'https://t.ctcdn.com.br/asq-AOPmO1NYsnU_wzz_baQJHNQ=/1200x675/smart/i379845.jpeg', 'Fúria crescente, resistência extrema', 60, 50, 18),
                ('Pantera Negra', 'Rei de Wakanda', 30, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1mFdupDPPn4i-bKcsm7-oc-A7pn4MhwF-rw&s', 'Agilidade aprimorada, traje vibranium, rastreamento', 23, 24, 27),
                ('Homem de ferro', 'Inventor em Armadura', 35, 'https://cdn.ome.lt/legacy/images/galerias/Superior-Iron-Man/Superior-Iron-Man-1-preview-1.jpg', 'Arsenal tecnológico, voo, repulsores', 28, 32, 25),
                ('Flash', 'Velocista', 40, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTkLNw3vsBGaU1lw7V0SxBwlY1Mtvw7qd-gBw&s', 'Velocidade da luz, vibração, viagem temporal', 12, 15, 60),
                ('Aquaman', 'Rei Atlante', 34, 'https://t.ctcdn.com.br/TBQgk-TTRl9to9_rO6WoJdHVVlI=/1200x675/smart/i972291.jpeg', 'Controle marinho, força elevada', 27, 26, 18),
                ('Doutor Estranho', 'Mago Supremo', 46, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_q9btbVL1s3i8EFrnR3LmxMa9-BWv3Ln3wQ&s', 'Magias místicas, portais, manipulação temporal', 10, 20, 24),
                ('Wolverine', 'Mutante Selvagem', 30, 'https://img.odcdn.com.br/wp-content/uploads/2023/07/wolverine.jpg', 'Fator de cura, garras, sentidos aguçados', 22, 28, 20),
                ('Deadpool', 'Mercenário Imortal', 29, 'https://s-media-cache-ak0.pinimg.com/originals/eb/18/bf/eb18bff9b9f8cdb16cf52e338a6e6f0e.png', 'Regeneração absurda, armas variadas', 20, 25, 23),
                ('Capitã Marvel', 'Guerreira Cósmica', 47, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKcRUlnmWRmQHc9i_jqIjwS79kaFtzdHziHA&s', 'Energia cósmica, voo, força extrema', 50, 38, 40),
                ('Viúva Negra', 'Espiã', 21, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdZvtqUnDLJoPgGCwmhNeEVCEFMonudjh3BQ&s', 'Artes marciais, espionagem', 14, 12, 25),
                ('Shazam', 'Campeão Mágico', 44, 'https://terraverso.com.br/wp-content/uploads/2023/03/Shazam_DC.jpg', 'Força divina, eletricidade', 45, 38, 34),
                ('Lanterna Verde', 'Guardiào Cósmico', 42, 'https://www.boletimnerd.com.br/wp-content/uploads/2025/07/guy-gardner-lanterna-verde-quadrinhos.jpg', 'Construtos de energia, voo, força de vontade', 30, 32, 28),
                ('Homem-Formiga', 'Herói Tecnológico', 25, 'https://lh6.googleusercontent.com/proxy/d3kxfAVGf-ajb-ctj5Jn8WjFBaCXNW49IAU-VfFVEW7t57e704N-bGYE0mXv1r2XNpA2SWiP-f3-Cb40FXngqbITR8lEtVhHBL982jc1mlrJiLBZ3xqxNJgPMx6fSow7XQ', 'Alteração de tamanho, força ampliada, comunicação com formigas', 20, 18, 24),
                ('Feiticeira Escarlate', 'Usuária de Magia do Caos', 50, 'https://lumiere-a.akamaihd.net/v1/images/feiticeira_escarlate_ucm_4_c584f237.jpeg?region=280,0,720,720', 'Manipulação da realidade, magia do caos, telecinesia', 32, 28, 26),
                ('Supergirl', 'Kryptoniana', 48, 'https://upload.wikimedia.org/wikipedia/pt/5/58/Supergirl_por_Adam_Hughes_e_Jeremy_Roberts.jpg', 'Voo, superforça, visão de calor, audição aprimorada', 48, 40, 45),
                ('Link', 'Herói da Lenda', 33, 'https://i.pinimg.com/736x/22/57/d8/2257d873dc8d3242096bd455ef93a8f6.jpg', 'Espada mestra, arco, habilidades mágicas', 22, 25, 24),
                ('Kratos', 'Deus da Guerra', 60, 'https://upload.wikimedia.org/wikipedia/pt/a/ae/Kratos_GoW_Ragnarok.jpg', 'Lâminas do Caos, força divina, fúria espartana', 70, 55, 30),
                ('Lara Croft', 'Aventureira', 26, 'https://i.pinimg.com/736x/b8/46/33/b84633e6d037a388ceeff3669b28e4df.jpg', 'Tiro, acrobacia, arqueologia', 16, 14, 26),
                ('Geralt de Rívia', 'Bruxo', 40, 'https://store.ign.com/cdn/shop/files/The-Witcher-3-Wild-Hunt-Geralt-of-Rivia-1-6-Scale-Action-Figure-16.jpg?v=1734720271&width=1946', 'Sinais, alquimia, espada prata', 28, 29, 24)
                ;
                """
            )
            conn.commit()
            print('Inserted sample heroes.')
        else:
            print('Herois table already has data; skipping sample inserts.')

    except Error as e:
        print('MySQL Error:', e)
        print('If the error is a foreign key constraint (1452), check that you are not inserting into `equipes` with a `user_id` that does not exist in `usuarios`.')
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()