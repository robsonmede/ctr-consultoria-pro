from pathlib import Path
import shutil
import sys


CAMINHO_APP = Path("app-completo.py")
CAMINHO_BACKUP = Path("app-completo.py.bak")


def aplicar_correcao():
    if not CAMINHO_APP.exists():
        print(
            "ERRO: o arquivo app-completo.py não foi encontrado.\n"
            "Coloque corrigir_app.py na mesma pasta do app-completo.py."
        )
        sys.exit(1)

    codigo = CAMINHO_APP.read_text(encoding="utf-8")

    # Cria backup antes de modificar.
    shutil.copy2(CAMINHO_APP, CAMINHO_BACKUP)

    alteracoes = 0

    # ========================================================
    # CORREÇÃO DO ASSESSMENT NIST CSF
    # ========================================================

    bloco_assessment_antigo = '''elif menu == "Assessment NIST CSF":
    dados = obter_dados_ativos()
    assessment = dados["assessment"]'''

    bloco_assessment_novo = '''elif menu == "Assessment NIST CSF":
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        st.stop()

    assessment = dados["assessment"]'''

    if bloco_assessment_antigo in codigo:
        codigo = codigo.replace(
            bloco_assessment_antigo,
            bloco_assessment_novo,
            1,
        )
        alteracoes += 1
        print("OK: módulo Assessment NIST CSF corrigido.")
    elif bloco_assessment_novo in codigo:
        print("AVISO: o módulo Assessment já estava corrigido.")
    else:
        print(
            "AVISO: não foi possível localizar automaticamente "
            "o início do módulo Assessment."
        )

    # ========================================================
    # CORREÇÃO DO COMPLIANCE
    # ========================================================

    bloco_compliance_antigo = '''elif menu == "Compliance":
    dados = obter_dados_ativos()'''

    bloco_compliance_novo = '''elif menu == "Compliance":
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.error("Nenhuma organização ativa foi encontrada.")
        st.stop()'''

    if bloco_compliance_antigo in codigo:
        codigo = codigo.replace(
            bloco_compliance_antigo,
            bloco_compliance_novo,
            1,
        )
        alteracoes += 1
        print("OK: módulo Compliance corrigido.")
    elif bloco_compliance_novo in codigo:
        print("AVISO: o módulo Compliance já estava corrigido.")
    else:
        print(
            "AVISO: não foi possível localizar automaticamente "
            "o início do módulo Compliance."
        )

    # ========================================================
    # VALIDAÇÃO DAS REFERÊNCIAS
    # ========================================================

    if 'key=f"assessment_{organizacao[\'id\']}_{chave}"' in codigo:
        print("OK: chave multi-organização do Assessment localizada.")

    if 'key=f"compliance_{organizacao[\'id\']}_{chave}"' in codigo:
        print("OK: chave multi-organização do Compliance localizada.")

    if alteracoes == 0:
        print(
            "\nNenhuma alteração nova foi aplicada. "
            "O arquivo pode já estar corrigido."
        )
        print(f"Backup disponível em: {CAMINHO_BACKUP}")
        return

    CAMINHO_APP.write_text(codigo, encoding="utf-8")

    # Valida a sintaxe do código depois das substituições.
    try:
        compile(
            codigo,
            str(CAMINHO_APP),
            "exec",
        )
    except SyntaxError as erro:
        shutil.copy2(CAMINHO_BACKUP, CAMINHO_APP)

        print("\nERRO: a validação de sintaxe falhou.")
        print(f"Linha: {erro.lineno}")
        print(f"Detalhes: {erro.msg}")
        print("O arquivo original foi restaurado automaticamente.")
        sys.exit(1)

    print("\nCorreção aplicada com sucesso.")
    print(f"Arquivo corrigido: {CAMINHO_APP.resolve()}")
    print(f"Backup do original: {CAMINHO_BACKUP.resolve()}")


if __name__ == "__main__":
    aplicar_correcao()
