import sqlite3


def init_zax_db():
    db = sqlite3.connect('zax.db')
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE MOTOBOY (
                CODIGO INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                NOME TEXT NOT NULL,
                PRECO_FIXO REAL CHECK (PRECO_FIXO >= 0)
        );
    """)

    cursor.execute("""
        CREATE TABLE LOJA (
                CODIGO INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                NOME TEXT NOT NULL,
                TAXA_EXTRA REAL CHECK (TAXA_EXTRA >= 0)
        );
    """)

    cursor.execute("""
        CREATE TABLE MOTOBOY_EXCLUSIVIDADE (
                CODIGO_MOTOBOY INTEGER,
                CODIGO_LOJA INTEGER,
                FOREIGN KEY(CODIGO_MOTOBOY) references MOTOBOY(CODIGO),
                FOREIGN KEY(CODIGO_LOJA) references LOJA(CODIGO),
                PRIMARY KEY(CODIGO_MOTOBOY, CODIGO_LOJA)
        );
    """)

    cursor.execute("""
        CREATE TABLE PEDIDO (
                CODIGO INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                CODIGO_LOJA INTEGER,
                PRECO REAL CHECK (PRECO >= 0),
                FOREIGN KEY(CODIGO_LOJA) references LOJA(CODIGO)
        );
    """)

    cursor.close()
    db.close()


def db_test_data():
    """
    Motoboys
    Moto 1 - cobra R$2 reais por entrega e atende todas as lojas
    Moto 2 - cobra R$2 reais por entrega e atende todas as lojas
    Moto 3 - cobra R$2 reais por entrega e atende todas as lojas
    Moto 4 - cobra R$2 reais por entrega e atende apenas a loja 1
    Moto 5 - cobra R$3 reais por entrega e atende todas as lojas

    Lojas
    Loja 1 - 3 pedidos (PEDIDO 1 R$50, PEDIDO 2 R$50, PEDIDO 3 R$50) e paga 5% do valor pedido por entrega fora o valor fixo.
    Loja 2 - 4 pedidos (PEDIDO 1 R$50, PEDIDO 2 R$50, PEDIDO 3 R$50, PEDIDO 4 R$50) e paga 5% do valor pedido por entrega fora o valor fixo.
    Loja 3 - 3 pedidos (PEDIDO 1 R$50, PEDIDO 2 R$50, PEDIDO 3 R$100) e paga 15% do valor pedido por entrega fora o valor fixo.

    O Moto 1 atende todas as lojas
    O Moto 2 atende todas as lojas
    O Moto 3 atende todas as lojas
    O Moto 4 atende apenas a loja 1
    O Moto 5 atende todas as lojas
    """

    db = sqlite3.connect('zax.db')
    cursor = db.cursor()

    motoboys = [
        ('Moto 1', 2),
        ('Moto 2', 2),
        ('Moto 3', 2),
        ('Moto 4', 2),
        ('Moto 5', 3)
    ]

    lojas = [
        ['Loja 1', 5],
        ['Loja 2', 5],
        ['Loja 3', 15]
    ]

    cursor.executemany("""
        INSERT INTO MOTOBOY (NOME, PRECO_FIXO) VALUES (?,?)
    """, motoboys)

    cursor.executemany("""
        INSERT INTO LOJA (NOME, TAXA_EXTRA) VALUES (?,?)
    """, lojas)

    cursor.execute("""
        INSERT INTO MOTOBOY_EXCLUSIVIDADE VALUES (?,?)
    """, cursor.execute("""
        SELECT MOTOBOY.CODIGO, LOJA.CODIGO FROM MOTOBOY, LOJA WHERE MOTOBOY.NOME = 'Moto 4' and LOJA.NOME = 'Loja 1';
    """).fetchone())

    cod_loja_1 = cursor.execute("""
        SELECT CODIGO FROM LOJA WHERE NOME = 'Loja 1';
    """).fetchone()[0]

    cod_loja_2 = cursor.execute("""
        SELECT CODIGO FROM LOJA WHERE NOME = 'Loja 2';
    """).fetchone()[0]

    cod_loja_3 = cursor.execute("""
        SELECT CODIGO FROM LOJA WHERE NOME = 'Loja 3';
    """).fetchone()[0]

    pedidos = [
        (50, cod_loja_1),
        (50, cod_loja_1),
        (50, cod_loja_1),
        (50, cod_loja_2),
        (50, cod_loja_2),
        (50, cod_loja_2),
        (50, cod_loja_2),
        (50, cod_loja_3),
        (50, cod_loja_3),
        (100, cod_loja_3)
    ]

    cursor.executemany("""
        INSERT INTO PEDIDO (PRECO, CODIGO_LOJA) VALUES (?,?)
    """, pedidos)

    cursor.close()
    db.commit()
    db.close()


def test():
    init_zax_db()
    db_test_data()


if __name__ == '__main__':
    test()
