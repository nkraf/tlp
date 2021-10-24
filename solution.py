import sys
import sqlite3
import dbinit
from os.path import exists


def print_table_header():
    print_separator()
    print('| MOTOBOY | TAXA FIXA |   LOJA   | TAXA LOJA | VALOR PEDIDO | TOTAL RECEBIDO PELO MOTOBOY |')
    print_separator()


def print_table_row(motoboy):
    print('| %7s | %9s | %8s | %9s | %12s | %27s |'%(motoboy['nome'], motoboy['preco_fixo_mb'],
          motoboy['loja'], motoboy['taxa'], motoboy['preco'], motoboy['valor_total_frete']))


def print_separator():
    print('+-----------------------------------------------------------------------------------------+')


def main():
    # Inicia o banco de dados
    if not exists('zax.db'):
        dbinit.init_zax_db()
        dbinit.db_test_data()

    db = sqlite3.connect('zax.db')
    cursor = db.cursor()

    # Motoboy a ser consultado
    motoboy_name = None

    # Captura o nome do motoboy atráves da linha de comando
    if len(sys.argv) > 1:
        motoboy_name = sys.argv[1]

    # Lojas
    lojas = cursor.execute("""
        SELECT LOJA.* from LOJA INNER JOIN PEDIDO ON PEDIDO.CODIGO_LOJA = LOJA.CODIGO GROUP BY LOJA.CODIGO ORDER by count(PEDIDO.CODIGO);
    """).fetchall()

    quantidade_pedidos = int(cursor.execute("""
        SELECT count(*) from PEDIDO;
    """).fetchone()[0])

    # Pedidos por loja
    entregas = []
    pedidos_entregues = {}
    for mb in cursor.execute("SELECT MOTOBOY.NOME FROM MOTOBOY").fetchall():
        pedidos_entregues[mb[0]] = []

    for loja in lojas:
        pedidos_loja = cursor.execute("""
            SELECT * FROM PEDIDO WHERE CODIGO_LOJA = ?;
        """, str(loja[0])).fetchall()

        motoboys_da_loja = cursor.execute("""
            select * from MOTOBOY
            JOIN MOTOBOY_EXCLUSIVIDADE ON MOTOBOY_EXCLUSIVIDADE.CODIGO_MOTOBOY = MOTOBOY.CODIGO
            WHERE MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA = ?;
        """, str(loja[0])).fetchall()

        entregas.append({
            'loja': loja,
            'pedidos': pedidos_loja,
            'motoboys': motoboys_da_loja,
            'fila_motoboys': [x for x in range(0, len(motoboys_da_loja))],
            'ciclo': 0
        })

    # Demais motoboys
    motoboys = cursor.execute("""
        SELECT MOTOBOY.* FROM MOTOBOY
        LEFT JOIN MOTOBOY_EXCLUSIVIDADE ON MOTOBOY_EXCLUSIVIDADE.CODIGO_MOTOBOY = MOTOBOY.CODIGO
        WHERE MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA IS NULL
    """).fetchall()

    fila_motoboys = [x for x in range(0, len(motoboys))]

    lojas_processadas = 0
    loja = 0
    quantidade_lojas = len(entregas)
    i = 0
    ciclo = 0
    while i < quantidade_pedidos:
        if not entregas[loja]['pedidos']:
            lojas_processadas += 1
            loja = lojas_processadas
            continue

        pedido = entregas[loja]['pedidos'].pop(0)
        motoboy = None

        while motoboy is None:
            if not entregas[loja]['fila_motoboys']:
                if entregas[loja]['ciclo'] < ciclo:
                    entregas[loja]['fila_motoboys'] = [x for x in range(0, len(entregas[loja]['motoboys']))]
                    entregas[loja]['ciclo'] += 1

            if entregas[loja]['fila_motoboys']:
                motoboy = entregas[loja]['motoboys'][entregas[loja]['fila_motoboys'].pop(0)]
                break

            if motoboy is None and fila_motoboys:
                motoboy = motoboys[fila_motoboys.pop(0)]
                break

            if motoboy is None:
                fila_motoboys = [x for x in range(0, len(motoboys))]
                ciclo += 1

        preco_fixo_mb = float(motoboy[2])
        pedidos_entregues[motoboy[1]].append(
            {
                'loja': entregas[loja]['loja'][1],
                'valor_total_frete': preco_fixo_mb + float(pedido[2]) / 100 * float(entregas[loja]['loja'][2]),
                'taxa': pedido[2],
                'preco_fixo_mb': motoboy[2],
                'preco': entregas[loja]['loja'][2],
                'nome': motoboy[1]
            }
        )

        loja += 1
        if loja >= quantidade_lojas:
            loja = lojas_processadas
        i += 1



    print_table_header()
    for mb in pedidos_entregues:

        if motoboy_name is not None:
            if mb == motoboy_name:
                for pedido in pedidos_entregues[mb]:
                    print_table_row(pedido)
                break
        else:
            for pedido in pedidos_entregues[mb]:
                print_table_row(pedido)
    print_separator()

    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
