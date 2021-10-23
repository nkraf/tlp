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
    motoboy_name = ''

    # Captura o nome do motoboy atráves da linha de comando
    if len(sys.argv) > 1:
        motoboy_name = sys.argv[1]

    # Pedidos ordernados por loja
    pedidos = cursor.execute("""
        SELECT LOJA.*, PEDIDO.PRECO FROM LOJA INNER JOIN PEDIDO ON PEDIDO.CODIGO_LOJA = LOJA.CODIGO
        ORDER BY LOJA.CODIGO ASC
    """).fetchall()

    # Motoboys ordenados por exclusividade da loja
    motoboys_com_exclusividade = cursor.execute("""
        SELECT MOTOBOY.*, MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA AS LOJA_PRIORITARIA FROM MOTOBOY
        JOIN MOTOBOY_EXCLUSIVIDADE ON MOTOBOY_EXCLUSIVIDADE.CODIGO_MOTOBOY = MOTOBOY.CODIGO
        ORDER BY MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA ASC NULLS LAST
    """).fetchall()

    # Demais motoboys
    motoboys = cursor.execute("""
        SELECT MOTOBOY.*, MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA AS LOJA_PRIORITARIA FROM MOTOBOY
        LEFT JOIN MOTOBOY_EXCLUSIVIDADE ON MOTOBOY_EXCLUSIVIDADE.CODIGO_MOTOBOY = MOTOBOY.CODIGO
        WHERE MOTOBOY_EXCLUSIVIDADE.CODIGO_LOJA IS NULL
    """).fetchall()

    # Lista de indices dos exclusivos
    motoboys_index_queue_e = [motoboys_com_exclusividade[x] for x in range(0, len(motoboys_com_exclusividade))]

    # Lista de indices dos demais motoboys
    motoboys_index_queue = [motoboys[x] for x in range(0, len(motoboys))]

    lojas_computadas = []
    loja_atual = None

    pedidos_entregues = {}
    for mb in motoboys_index_queue_e:
        pedidos_entregues[mb[1]] = []

    for mb in motoboys_index_queue:
        pedidos_entregues[mb[1]] = []

    # Itera todos os pedidos
    for pedido in pedidos:

        # Move os motoboys exclusivos já que a loja não tem mais nenhum pedido
        if pedido[0] != loja_atual:
            swp = []
            for mb in motoboys_index_queue_e:
                if mb[3] in lojas_computadas:
                    swp.append(mb)

            for mb in swp:
                motoboys_index_queue_e.remove(mb)
                motoboys_index_queue.append(mb)

        loja_atual = pedido[0]
        lojas_computadas.append(loja_atual)
        motoboy = None

        while motoboy is None:

            # Seleciona o motoboy exclusivo
            for mb in motoboys_index_queue_e:
                if mb[3] == loja_atual:
                    motoboy = mb
                    motoboys_index_queue_e.remove(mb)
                    break

            # Seleciona qualquer motoboy
            if motoboy is None:
                for mb in motoboys_index_queue:
                    motoboy = mb
                    motoboys_index_queue.remove(mb)
                    break

            # Reinicia a rolagem
            if motoboy is None:
                motoboys_index_queue_e = [motoboys_com_exclusividade[x] for x in
                                          range(0, len(motoboys_com_exclusividade))]
                motoboys_index_queue = [motoboys[x] for x in range(0, len(motoboys))]

        preco_fixo_mb = float(motoboy[2])
        pedidos_entregues[motoboy[1]].append(
            {
                'loja':pedido[1],
                'valor_total_frete': preco_fixo_mb + float(pedido[2]) / 100 * pedido[3],
                'taxa': pedido[2],
                'preco_fixo_mb': motoboy[2],
                'preco': pedido[3],
                'nome': motoboy[1]
            }
        )

    print_table_header()
    for mb in pedidos_entregues.values():
        for pedido in mb:
            print_table_row(pedido)
    print_separator()


    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
