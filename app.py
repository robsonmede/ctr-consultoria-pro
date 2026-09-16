import hashlib
import hmac
import io
import time
import uuid
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="CTR DEFENSE | Consultoria Profissional",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTES
# ============================================================

MAX_TENTATIVAS_LOGIN = 5
TEMPO_BLOQUEIO_SEGUNDOS = 60

DIMENSOES_NIST = [
    "Governar",
    "Identificar",
    "Proteger",
    "Detectar",
    "Responder",
    "Recuperar",
]

PERGUNTAS_ASSESSMENT = {
    "Governar": [
        "Existe uma política formal de segurança da informação?",
        "Papéis e responsabilidades de segurança estão definidos?",
        "Os riscos cibernéticos são reportados à alta administração?",
        "Fornecedores são avaliados quanto aos riscos de segurança?",
    ],
    "Identificar": [
        "A organização possui inventário atualizado de ativos?",
        "Os dados críticos estão identificados e classificados?",
        "Existe processo formal de avaliação de riscos?",
        "Dependências críticas de negócio estão documentadas?",
    ],
    "Proteger": [
        "A organização utiliza autenticação multifator?",
        "Os acessos seguem o princípio do menor privilégio?",
        "Existe programa contínuo de conscientização?",
        "Backups são protegidos e testados periodicamente?",
    ],
    "Detectar": [
        "Logs de segurança são coletados e monitorados?",
        "Existe monitoramento de eventos suspeitos?",
        "Alertas possuem critérios definidos de priorização?",
        "A organização realiza análise de vulnerabilidades?",
    ],
    "Responder": [
        "Existe plano formal de resposta a incidentes?",
        "Os responsáveis por incidentes estão definidos?",
        "São realizados exercícios de resposta a incidentes?",
        "Existe procedimento para comunicação de incidentes?",
    ],
    "Recuperar": [
        "Existe plano de recuperação de desastres?",
        "Os objetivos de recuperação estão definidos?",
        "Os planos de recuperação são testados?",
        "Lições aprendidas são incorporadas aos processos?",
    ],
}

CONTROLES_COMPLIANCE = {
    "NIST CSF 2.0": [
        "Estratégia de gestão de riscos cibernéticos definida",
        "Inventário de ativos atualizado",
        "Gestão de identidade e controle de acesso",
        "Monitoramento contínuo de segurança",
        "Plano de resposta a incidentes",
        "Plano de recuperação e continuidade",
    ],
    "ISO 27001": [
        "Contexto e escopo do SGSI definidos",
        "Política de segurança aprovada",
        "Avaliação e tratamento de riscos",
        "Gestão de acessos",
        "Gestão de fornecedores",
        "Auditoria interna do SGSI",
    ],
    "LGPD": [
        "Inventário de dados pessoais",
        "Bases legais documentadas",
        "Canal para titulares de dados",
        "Encarregado de dados definido",
        "Plano de resposta a incidentes de privacidade",
        "Avaliação de operadores e fornecedores",
    ],
}

NIVEIS_MATURIDADE = {
    "Não implementado": 0,
    "Inicial": 1,
    "Repetível": 2,
    "Definido": 3,
    "Gerenciado": 4,
    "Otimizado": 5,
}

CORES_RISCO = {
    "Baixo": "#2ca02c",
    "Médio": "#ffbf00",
    "Alto": "#ff7f0e",
    "Crítico": "#d62728",
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --ctr-primary: #047f9e;
            --ctr-secondary: #0b3040;
            --ctr-text: #102f3b;
            --ctr-muted: #647b85;
            --ctr-border: #c8dce4;
            --ctr-background: #f4f8fa;
            --ctr-card: #ffffff;
        }

        .stApp {
            background:
                linear-gradient(135deg, #f7fafb 0%, #eaf2f5 100%);
            color: var(--ctr-text);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, p, label,
        [data-testid="stMarkdownContainer"] {
            color: var(--ctr-text);
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #0b3040 0%, #075c75 100%);
        }

        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] input {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid var(--ctr-border);
            border-left: 5px solid var(--ctr-primary);
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(11, 48, 64, 0.07);
        }

        div[data-testid="stForm"],
        div[data-testid="stExpander"] {
            background-color: #ffffff;
            border: 1px solid var(--ctr-border);
            border-radius: 14px;
            padding: 12px;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {
            color: #102f3b !important;
            background-color: #ffffff !important;
            border-color: #b8ced7 !important;
        }

        div[data-baseweb="select"] > div {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        div[role="listbox"],
        li[role="option"] {
            color: #102f3b !important;
            background-color: #ffffff !important;
        }

        .ctr-hero {
            padding: 24px;
            margin-bottom: 22px;
            border-radius: 18px;
            color: #ffffff;
            background:
                linear-gradient(120deg, #0b3040 0%, #047f9e 100%);
            box-shadow: 0 12px 30px rgba(11, 48, 64, 0.18);
        }

        .ctr-hero h1,
        .ctr-hero p {
            color: #ffffff !important;
            margin: 0;
        }

        .ctr-hero p {
            margin-top: 6px;
            opacity: 0.9;
        }

        .ctr-card {
            height: 100%;
            padding: 18px;
            border: 1px solid var(--ctr-border);
            border-radius: 14px;
            background-color: #ffffff;
            box-shadow: 0 8px 24px rgba(11, 48, 64, 0.07);
        }

        .ctr-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            color: #ffffff;
            background-color: #047f9e;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .login-logo {
            width: 86px;
            height: 86px;
            margin: 0 auto 1rem auto;
            border-radius: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            background:
                linear-gradient(135deg, #047f9e 0%, #0b3040 100%);
            font-size: 42px;
            box-shadow: 0 14px 32px rgba(11, 48, 64, 0.22);
        }

        .login-header {
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .login-footer {
            margin-top: 1.5rem;
            color: #647b85;
            text-align: center;
            font-size: 0.82rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 9px;
            font-weight: 700;
        }

        .stButton > button[kind="primary"],
        .stDownloadButton > button {
            color: #ffffff !important;
            background-color: #047f9e !important;
            border-color: #047f9e !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÕES GERAIS
# ============================================================

def gerar_id(prefixo):
    return f"{prefixo}_{uuid.uuid4().hex[:10]}"


def dataframe_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def classificar_risco(probabilidade, impacto):
    pontuacao = int(probabilidade) * int(impacto)

    if pontuacao >= 20:
        return "Crítico"
    if pontuacao >= 12:
        return "Alto"
    if pontuacao >= 6:
        return "Médio"
    return "Baixo"


def classificar_maturidade(score):
    if score < 20:
        return "Inicial"
    if score < 40:
        return "Repetível"
    if score < 60:
        return "Definido"
    if score < 80:
        return "Gerenciado"
    return "Otimizado"


def normalizar_dataframe(registros, colunas):
    if not registros:
        return pd.DataFrame(columns=colunas)

    df = pd.DataFrame(registros)

    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = ""

    return df[colunas]


def exibir_cabecalho(titulo, subtitulo):
    st.markdown(
        f"""
        <div class="ctr-hero">
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AUTENTICAÇÃO
# ============================================================

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def inicializar_autenticacao():
    padroes = {
        "autenticado": False,
        "usuario_logado": None,
        "nome_usuario_logado": None,
        "perfil_usuario": None,
        "tentativas_login": 0,
        "bloqueado_ate": 0.0,
        "exibir_senha_login": False,
    }

    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def carregar_usuarios():
    try:
        usuarios_configurados = st.secrets["usuarios"]
    except (KeyError, FileNotFoundError):
        return {}

    usuarios = {}

    for login, configuracao in usuarios_configurados.items():
        try:
            usuarios[str(login).strip().lower()] = {
                "nome": str(configuracao.get("nome", login)).strip(),
                "senha_hash": str(
                    configuracao.get("senha_hash", "")
                ).strip().lower(),
                "perfil": str(
                    configuracao.get("perfil", "Consultor")
                ).strip(),
                "ativo": bool(configuracao.get("ativo", True)),
            }
        except (AttributeError, TypeError):
            continue

    return usuarios


def autenticar_usuario(login, senha):
    usuarios = carregar_usuarios()
    login_normalizado = login.strip().lower()
    usuario = usuarios.get(login_normalizado)

    if not usuario or not usuario.get("ativo"):
        return False

    hash_esperado = usuario.get("senha_hash", "")
    hash_informado = gerar_hash_senha(senha)

    if not hash_esperado:
        return False

    if not hmac.compare_digest(hash_informado, hash_esperado):
        return False

    st.session_state.autenticado = True
    st.session_state.usuario_logado = login_normalizado
    st.session_state.nome_usuario_logado = usuario["nome"]
    st.session_state.perfil_usuario = usuario["perfil"]
    st.session_state.tentativas_login = 0
    st.session_state.bloqueado_ate = 0.0

    return True


def efetuar_logout():
    for chave in [
        "autenticado",
        "usuario_logado",
        "nome_usuario_logado",
        "perfil_usuario",
        "campo_login",
        "campo_senha",
    ]:
        st.session_state.pop(chave, None)

    inicializar_autenticacao()


def exibir_tela_login():
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                display: none;
            }

            div[data-testid="collapsedControl"] {
                display: none;
            }

            .block-container {
                max-width: 540px;
                padding-top: 7vh;
            }
        </style>

        <div class="login-logo">🛡️</div>
        <div class="login-header">
            <h1>CTR DEFENSE</h1>
            <p>Plataforma Profissional de Consultoria em Cibersegurança</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    usuarios = carregar_usuarios()

    if not usuarios:
        st.error(
            "Nenhum usuário está configurado. Crie o arquivo "
            "`.streamlit/secrets.toml` conforme o modelo apresentado "
            "após o código."
        )
        st.stop()

    segundos_restantes = max(
        0,
        int(
            float(st.session_state.get("bloqueado_ate", 0))
            - time.time()
        ),
    )

    if segundos_restantes > 0:
        st.error(
            "Acesso temporariamente bloqueado. "
            f"Aguarde {segundos_restantes} segundos."
        )

        if st.button("Atualizar", use_container_width=True):
            st.rerun()

        st.stop()

    tipo_senha = (
        "default"
        if st.session_state.exibir_senha_login
        else "password"
    )

    with st.form("formulario_login"):
        login = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            key="campo_login",
        )

        senha = st.text_input(
            "Senha",
            type=tipo_senha,
            placeholder="Digite sua senha",
            key="campo_senha",
        )

        entrar = st.form_submit_button(
            "Entrar na plataforma",
            type="primary",
            use_container_width=True,
        )

    texto_exibicao = (
        "Ocultar senha"
        if st.session_state.exibir_senha_login
        else "Mostrar senha"
    )

    if st.button(
        texto_exibicao,
        use_container_width=True,
        key="alternar_exibicao_senha",
    ):
        st.session_state.exibir_senha_login = (
            not st.session_state.exibir_senha_login
        )
        st.rerun()

    if entrar:
        if not login.strip() or not senha:
            st.warning("Informe o usuário e a senha.")

        elif autenticar_usuario(login, senha):
            st.success("Autenticação realizada com sucesso.")
            st.rerun()

        else:
            st.session_state.tentativas_login += 1
            tentativas = st.session_state.tentativas_login
            restantes = MAX_TENTATIVAS_LOGIN - tentativas

            if tentativas >= MAX_TENTATIVAS_LOGIN:
                st.session_state.bloqueado_ate = (
                    time.time() + TEMPO_BLOQUEIO_SEGUNDOS
                )
                st.session_state.tentativas_login = 0
                st.error(
                    "Número máximo de tentativas atingido. "
                    f"Acesso bloqueado por "
                    f"{TEMPO_BLOQUEIO_SEGUNDOS} segundos."
                )
            else:
                st.error(
                    "Usuário ou senha inválidos. "
                    f"Tentativas restantes: {restantes}."
                )

    st.markdown(
        f"""
        <div class="login-footer">
            CTR DEFENSE © {datetime.now().year}<br>
            Acesso restrito a usuários autorizados.
        </div>
        """,
        unsafe_allow_html=True,
    )


def exigir_autenticacao():
    inicializar_autenticacao()

    if not st.session_state.get("autenticado", False):
        exibir_tela_login()
        st.stop()


# ============================================================
# ESTADO E ORGANIZAÇÕES
# ============================================================

def criar_dados_organizacao():
    return {
        "assessment": {},
        "riscos": [],
        "acoes": [],
        "roadmap": [],
        "gap_analysis": {},
        "compliance": {},
        "reunioes": [],
    }


def inicializar_estado():
    if "organizacoes" not in st.session_state:
        st.session_state.organizacoes = {}

    if "organizacao_ativa_id" not in st.session_state:
        st.session_state.organizacao_ativa_id = None


def obter_organizacao_ativa():
    organizacao_id = st.session_state.get("organizacao_ativa_id")

    if not organizacao_id:
        return None

    return st.session_state.organizacoes.get(organizacao_id)


def obter_dados_ativos():
    organizacao = obter_organizacao_ativa()

    if organizacao is None:
        return None

    if "dados" not in organizacao:
        organizacao["dados"] = criar_dados_organizacao()

    return organizacao["dados"]


def exigir_organizacao():
    organizacao = obter_organizacao_ativa()
    dados = obter_dados_ativos()

    if organizacao is None or dados is None:
        st.warning(
            "Cadastre ou selecione uma organização na barra lateral "
            "antes de utilizar este módulo."
        )
        st.stop()

    return organizacao, dados


def remover_chaves_widgets_organizacao(organizacao_id):
    prefixos = [
        f"assessment_{organizacao_id}_",
        f"compliance_{organizacao_id}_",
        f"gap_{organizacao_id}_",
    ]

    for chave in list(st.session_state.keys()):
        if any(str(chave).startswith(prefixo) for prefixo in prefixos):
            del st.session_state[chave]


# ============================================================
# CÁLCULOS
# ============================================================

def calcular_scores_assessment(dados):
    respostas = dados.get("assessment", {})
    scores = {}

    for dimensao, perguntas in PERGUNTAS_ASSESSMENT.items():
        valores = [
            int(respostas.get(f"{dimensao}_{indice}", 0))
            for indice in range(len(perguntas))
        ]

        scores[dimensao] = (
            round(sum(valores) / (len(valores) * 5) * 100, 1)
            if valores
            else 0
        )

    geral = (
        round(sum(scores.values()) / len(scores), 1)
        if scores
        else 0
    )

    return scores, geral


def estatisticas_riscos(dados):
    riscos = dados.get("riscos", [])

    contagem = {
        nivel: sum(
            1 for risco in riscos
            if risco.get("Nível") == nivel
        )
        for nivel in CORES_RISCO
    }

    return contagem


# ============================================================
# SIDEBAR
# ============================================================

def construir_sidebar():
    st.sidebar.title("🛡️ CTR DEFENSE")
    st.sidebar.caption("Gestão de Consultoria")

    organizacoes = st.session_state.organizacoes

    if organizacoes:
        ids = list(organizacoes.keys())

        indice_atual = 0
        atual = st.session_state.get("organizacao_ativa_id")

        if atual in ids:
            indice_atual = ids.index(atual)

        selecionado = st.sidebar.selectbox(
            "Organização ativa",
            options=ids,
            index=indice_atual,
            format_func=lambda org_id: organizacoes[org_id]["nome"],
        )

        st.session_state.organizacao_ativa_id = selecionado
    else:
        st.sidebar.info("Nenhuma organização cadastrada.")

    modulos = [
        "Dashboard Executivo",
        "Organizações",
        "Assessment NIST CSF",
        "Matriz de Riscos",
        "Plano de Ação",
        "Roadmap de Segurança",
        "Gap Analysis",
        "Adequação LGPD/NIST/ISO",
        "Reuniões",
        "Relatórios",
    ]

    menu = st.sidebar.radio(
        "Módulos da consultoria",
        modulos,
    )

    st.sidebar.markdown("---")

    nome = st.session_state.get(
        "nome_usuario_logado",
        "Usuário",
    )
    perfil = st.session_state.get(
        "perfil_usuario",
        "Consultor",
    )

    st.sidebar.markdown(f"**👤 {nome}**")
    st.sidebar.caption(f"Perfil: {perfil}")

    if st.sidebar.button(
        "🚪 Sair",
        use_container_width=True,
    ):
        efetuar_logout()
        st.rerun()

    st.sidebar.caption(
        f"CTR DEFENSE © {datetime.now().year}"
    )

    return menu


# ============================================================
# DASHBOARD
# ============================================================

def modulo_dashboard():
    exibir_cabecalho(
        "Dashboard Executivo",
        "Visão consolidada da postura de cibersegurança.",
    )

    organizacao, dados = exigir_organizacao()
    scores, score_geral = calcular_scores_assessment(dados)
    riscos = dados.get("riscos", [])
    acoes = dados.get("acoes", [])

    riscos_criticos = sum(
        1 for risco in riscos
        if risco.get("Nível") == "Crítico"
    )

    acoes_concluidas = sum(
        1 for acao in acoes
        if acao.get("Status") == "Concluída"
    )

    percentual_acoes = (
        round(acoes_concluidas / len(acoes) * 100, 1)
        if acoes
        else 0
    )

    coluna1, coluna2, coluna3, coluna4 = st.columns(4)

    coluna1.metric(
        "Maturidade",
        f"{score_geral:.1f}%",
        classificar_maturidade(score_geral),
    )
    coluna2.metric("Riscos cadastrados", len(riscos))
    coluna3.metric("Riscos críticos", riscos_criticos)
    coluna4.metric(
        "Ações concluídas",
        f"{percentual_acoes:.1f}%",
    )

    st.subheader(f"Organização: {organizacao['nome']}")

    coluna_radar, coluna_riscos = st.columns(2)

    with coluna_radar:
        fig_radar = go.Figure()

        valores = [scores[d] for d in DIMENSOES_NIST]
        valores_fechados = valores + [valores[0]]
        categorias = DIMENSOES_NIST + [DIMENSOES_NIST[0]]

        fig_radar.add_trace(
            go.Scatterpolar(
                r=valores_fechados,
                theta=categorias,
                fill="toself",
                name="Maturidade",
                line_color="#047f9e",
            )
        )

        fig_radar.update_layout(
            title="Maturidade por função NIST CSF",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                )
            ),
            showlegend=False,
            height=450,
        )

        st.plotly_chart(
            fig_radar,
            use_container_width=True,
        )

    with coluna_riscos:
        contagem = estatisticas_riscos(dados)

        df_riscos = pd.DataFrame(
            {
                "Nível": list(contagem.keys()),
                "Quantidade": list(contagem.values()),
            }
        )

        fig_riscos = px.pie(
            df_riscos,
            names="Nível",
            values="Quantidade",
            title="Distribuição dos riscos",
            color="Nível",
            color_discrete_map=CORES_RISCO,
            hole=0.45,
        )

        fig_riscos.update_layout(height=450)

        st.plotly_chart(
            fig_riscos,
            use_container_width=True,
        )

    df_maturidade = pd.DataFrame(
        {
            "Dimensão": list(scores.keys()),
            "Maturidade": list(scores.values()),
        }
    )

    fig_barras = px.bar(
        df_maturidade,
        x="Dimensão",
        y="Maturidade",
        text="Maturidade",
        color="Maturidade",
        color_continuous_scale="Blues",
        range_y=[0, 100],
        title="Cobertura por dimensão",
    )

    st.plotly_chart(
        fig_barras,
        use_container_width=True,
    )


# ============================================================
# ORGANIZAÇÕES
# ============================================================

def modulo_organizacoes():
    exibir_cabecalho(
        "Organizações",
        "Cadastro e gerenciamento dos clientes da consultoria.",
    )

    with st.form("form_organizacao", clear_on_submit=True):
        st.subheader("Cadastrar organização")

        coluna1, coluna2 = st.columns(2)

        nome = coluna1.text_input("Nome da organização")
        documento = coluna2.text_input("CNPJ ou documento")
        setor = coluna1.text_input("Setor")
        responsavel = coluna2.text_input("Responsável")
        email = coluna1.text_input("E-mail")
        telefone = coluna2.text_input("Telefone")

        cadastrar = st.form_submit_button(
            "Cadastrar organização",
            type="primary",
        )

        if cadastrar:
            if not nome.strip():
                st.error("Informe o nome da organização.")
            else:
                organizacao_id = gerar_id("org")

                st.session_state.organizacoes[organizacao_id] = {
                    "id": organizacao_id,
                    "nome": nome.strip(),
                    "documento": documento.strip(),
                    "setor": setor.strip(),
                    "responsavel": responsavel.strip(),
                    "email": email.strip(),
                    "telefone": telefone.strip(),
                    "criada_em": datetime.now().strftime(
                        "%d/%m/%Y %H:%M"
                    ),
                    "dados": criar_dados_organizacao(),
                }

                st.session_state.organizacao_ativa_id = organizacao_id
                st.success("Organização cadastrada com sucesso.")
                st.rerun()

    st.subheader("Organizações cadastradas")

    if not st.session_state.organizacoes:
        st.info("Nenhuma organização cadastrada.")
        return

    registros = []

    for organizacao in st.session_state.organizacoes.values():
        registros.append(
            {
                "ID": organizacao["id"],
                "Organização": organizacao["nome"],
                "Documento": organizacao["documento"],
                "Setor": organizacao["setor"],
                "Responsável": organizacao["responsavel"],
                "E-mail": organizacao["email"],
                "Criada em": organizacao["criada_em"],
            }
        )

    st.dataframe(
        pd.DataFrame(registros),
        use_container_width=True,
        hide_index=True,
    )

    organizacao_id_remover = st.selectbox(
        "Organização para exclusão",
        options=list(st.session_state.organizacoes.keys()),
        format_func=lambda org_id: (
            st.session_state.organizacoes[org_id]["nome"]
        ),
    )

    confirmar = st.checkbox(
        "Confirmo a exclusão definitiva dos dados da organização."
    )

    if st.button("Excluir organização", type="secondary"):
        if not confirmar:
            st.warning("Marque a confirmação antes de excluir.")
        else:
            remover_chaves_widgets_organizacao(
                organizacao_id_remover
            )

            del st.session_state.organizacoes[
                organizacao_id_remover
            ]

            ids_restantes = list(
                st.session_state.organizacoes.keys()
            )

            st.session_state.organizacao_ativa_id = (
                ids_restantes[0]
                if ids_restantes
                else None
            )

            st.success("Organização excluída.")
            st.rerun()


# ============================================================
# ASSESSMENT NIST
# ============================================================

def modulo_assessment():
    exibir_cabecalho(
        "Assessment NIST CSF 2.0",
        "Avaliação de maturidade nas seis funções do framework.",
    )

    organizacao, dados = exigir_organizacao()
    organizacao_id = organizacao["id"]

    opcoes = list(NIVEIS_MATURIDADE.keys())

    total_perguntas = sum(
        len(perguntas)
        for perguntas in PERGUNTAS_ASSESSMENT.values()
    )

    respondidas = sum(
        1
        for valor in dados["assessment"].values()
        if int(valor) > 0
    )

    st.progress(
        respondidas / total_perguntas
        if total_perguntas
        else 0
    )
    st.caption(
        f"{respondidas} de {total_perguntas} controles avaliados."
    )

    for dimensao, perguntas in PERGUNTAS_ASSESSMENT.items():
        with st.expander(
            f"{dimensao} — {len(perguntas)} controles",
            expanded=True,
        ):
            colunas = st.columns(2)

            for indice, pergunta in enumerate(perguntas):
                chave_dado = f"{dimensao}_{indice}"
                valor_atual = int(
                    dados["assessment"].get(chave_dado, 0)
                )

                valor_widget = colunas[indice % 2].selectbox(
                    pergunta,
                    options=opcoes,
                    index=valor_atual,
                    key=(
                        f"assessment_{organizacao_id}_"
                        f"{dimensao}_{indice}"
                    ),
                )

                dados["assessment"][chave_dado] = (
                    NIVEIS_MATURIDADE[valor_widget]
                )

    scores, score_geral = calcular_scores_assessment(dados)

    st.subheader("Resultado")

    coluna1, coluna2 = st.columns(2)
    coluna1.metric("Maturidade geral", f"{score_geral:.1f}%")
    coluna2.metric(
        "Classificação",
        classificar_maturidade(score_geral),
    )

    df_scores = pd.DataFrame(
        {
            "Dimensão": list(scores.keys()),
            "Score": list(scores.values()),
        }
    )

    fig = px.bar(
        df_scores,
        x="Dimensão",
        y="Score",
        color="Score",
        text="Score",
        range_y=[0, 100],
        color_continuous_scale="Teal",
    )

    st.plotly_chart(fig, use_container_width=True)

    if st.button("Limpar avaliação"):
        remover_chaves_widgets_organizacao(organizacao_id)
        dados["assessment"] = {}
        st.success("Assessment reiniciado.")
        st.rerun()


# ============================================================
# RISCOS
# ============================================================

def modulo_riscos():
    exibir_cabecalho(
        "Matriz de Riscos",
        "Registro, priorização e tratamento de riscos.",
    )

    _, dados = exigir_organizacao()

    with st.form("form_risco", clear_on_submit=True):
        st.subheader("Cadastrar risco")

        risco = st.text_input("Descrição do risco")
        categoria = st.selectbox(
            "Categoria",
            [
                "Governança",
                "Tecnologia",
                "Pessoas",
                "Processos",
                "Terceiros",
                "Privacidade",
            ],
        )

        coluna1, coluna2, coluna3 = st.columns(3)

        probabilidade = coluna1.slider(
            "Probabilidade",
            1,
            5,
            3,
        )
        impacto = coluna2.slider(
            "Impacto",
            1,
            5,
            3,
        )
        status = coluna3.selectbox(
            "Status",
            ["Ativo", "Em tratamento", "Aceito", "Encerrado"],
        )

        tratamento = st.text_area("Tratamento recomendado")
        responsavel = st.text_input("Responsável")

        adicionar = st.form_submit_button(
            "Adicionar risco",
            type="primary",
        )

        if adicionar:
            if not risco.strip():
                st.error("Informe a descrição do risco.")
            else:
                nivel = classificar_risco(
                    probabilidade,
                    impacto,
                )

                dados["riscos"].append(
                    {
                        "ID": gerar_id("risco"),
                        "Risco": risco.strip(),
                        "Categoria": categoria,
                        "Probabilidade": probabilidade,
                        "Impacto": impacto,
                        "Pontuação": probabilidade * impacto,
                        "Nível": nivel,
                        "Status": status,
                        "Tratamento": tratamento.strip(),
                        "Responsável": responsavel.strip(),
                        "Data": date.today().strftime("%d/%m/%Y"),
                    }
                )

                st.success("Risco cadastrado com sucesso.")
                st.rerun()

    colunas_riscos = [
        "ID",
        "Risco",
        "Categoria",
        "Probabilidade",
        "Impacto",
        "Pontuação",
        "Nível",
        "Status",
        "Tratamento",
        "Responsável",
        "Data",
    ]

    df = normalizar_dataframe(
        dados["riscos"],
        colunas_riscos,
    )

    st.subheader("Registro de riscos")

    if df.empty:
        st.info("Nenhum risco cadastrado.")
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        fig = px.scatter(
            df,
            x="Probabilidade",
            y="Impacto",
            size="Pontuação",
            color="Nível",
            hover_name="Risco",
            color_discrete_map=CORES_RISCO,
            range_x=[0.5, 5.5],
            range_y=[0.5, 5.5],
            title="Heatmap de probabilidade e impacto",
        )

        fig.update_xaxes(dtick=1)
        fig.update_yaxes(dtick=1)

        st.plotly_chart(fig, use_container_width=True)

        id_remover = st.selectbox(
            "Selecione um risco para excluir",
            options=df["ID"].tolist(),
            format_func=lambda risco_id: next(
                (
                    item["Risco"]
                    for item in dados["riscos"]
                    if item["ID"] == risco_id
                ),
                risco_id,
            ),
        )

        if st.button("Excluir risco"):
            dados["riscos"] = [
                item
                for item in dados["riscos"]
                if item["ID"] != id_remover
            ]
            st.success("Risco excluído.")
            st.rerun()


# ============================================================
# PLANO DE AÇÃO
# ============================================================

def modulo_plano_acao():
    exibir_cabecalho(
        "Plano de Ação",
        "Gestão das iniciativas de tratamento e melhoria.",
    )

    _, dados = exigir_organizacao()

    with st.form("form_acao", clear_on_submit=True):
        acao = st.text_input("Ação")
        descricao = st.text_area("Descrição")

        coluna1, coluna2, coluna3 = st.columns(3)

        responsavel = coluna1.text_input("Responsável")
        prioridade = coluna2.selectbox(
            "Prioridade",
            ["Baixa", "Média", "Alta", "Crítica"],
        )
        status = coluna3.selectbox(
            "Status",
            [
                "Não iniciada",
                "Em andamento",
                "Bloqueada",
                "Concluída",
            ],
        )

        coluna4, coluna5 = st.columns(2)
        inicio = coluna4.date_input("Data de início")
        prazo = coluna5.date_input("Prazo")

        adicionar = st.form_submit_button(
            "Adicionar ação",
            type="primary",
        )

        if adicionar:
            if not acao.strip():
                st.error("Informe a ação.")
            elif prazo < inicio:
                st.error(
                    "O prazo não pode ser anterior à data de início."
                )
            else:
                dados["acoes"].append(
                    {
                        "ID": gerar_id("acao"),
                        "Ação": acao.strip(),
                        "Descrição": descricao.strip(),
                        "Responsável": responsavel.strip(),
                        "Prioridade": prioridade,
                        "Status": status,
                        "Início": inicio.isoformat(),
                        "Prazo": prazo.isoformat(),
                    }
                )
                st.success("Ação cadastrada.")
                st.rerun()

    colunas = [
        "ID",
        "Ação",
        "Descrição",
        "Responsável",
        "Prioridade",
        "Status",
        "Início",
        "Prazo",
    ]

    df = normalizar_dataframe(dados["acoes"], colunas)

    if df.empty:
        st.info("Nenhuma ação cadastrada.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    status_contagem = (
        df.groupby("Status")
        .size()
        .reset_index(name="Quantidade")
    )

    fig = px.bar(
        status_contagem,
        x="Status",
        y="Quantidade",
        color="Status",
        title="Ações por status",
    )

    st.plotly_chart(fig, use_container_width=True)

    id_remover = st.selectbox(
        "Ação para exclusão",
        options=df["ID"].tolist(),
        format_func=lambda acao_id: next(
            (
                item["Ação"]
                for item in dados["acoes"]
                if item["ID"] == acao_id
            ),
            acao_id,
        ),
    )

    if st.button("Excluir ação"):
        dados["acoes"] = [
            item
            for item in dados["acoes"]
            if item["ID"] != id_remover
        ]
        st.rerun()


# ============================================================
# ROADMAP
# ============================================================

def modulo_roadmap():
    exibir_cabecalho(
        "Roadmap de Segurança",
        "Cronograma estratégico das iniciativas de segurança.",
    )

    _, dados = exigir_organizacao()

    with st.form("form_roadmap", clear_on_submit=True):
        iniciativa = st.text_input("Iniciativa")
        categoria = st.selectbox(
            "Categoria",
            DIMENSOES_NIST,
        )

        coluna1, coluna2 = st.columns(2)
        inicio = coluna1.date_input("Início")
        fim = coluna2.date_input("Fim")

        coluna3, coluna4 = st.columns(2)
        responsavel = coluna3.text_input("Responsável")
        progresso = coluna4.slider("Progresso", 0, 100, 0)

        adicionar = st.form_submit_button(
            "Adicionar ao roadmap",
            type="primary",
        )

        if adicionar:
            if not iniciativa.strip():
                st.error("Informe a iniciativa.")
            elif fim < inicio:
                st.error("A data final deve ser posterior ao início.")
            else:
                dados["roadmap"].append(
                    {
                        "ID": gerar_id("roadmap"),
                        "Iniciativa": iniciativa.strip(),
                        "Categoria": categoria,
                        "Início": inicio.isoformat(),
                        "Fim": fim.isoformat(),
                        "Responsável": responsavel.strip(),
                        "Progresso": progresso,
                    }
                )
                st.success("Iniciativa adicionada.")
                st.rerun()

    colunas = [
        "ID",
        "Iniciativa",
        "Categoria",
        "Início",
        "Fim",
        "Responsável",
        "Progresso",
    ]

    df = normalizar_dataframe(dados["roadmap"], colunas)

    if df.empty:
        st.info("Nenhuma iniciativa cadastrada.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)

    df_gantt = df.copy()
    df_gantt["Início"] = pd.to_datetime(df_gantt["Início"])
    df_gantt["Fim"] = pd.to_datetime(df_gantt["Fim"])

    fig = px.timeline(
        df_gantt,
        x_start="Início",
        x_end="Fim",
        y="Iniciativa",
        color="Categoria",
        hover_data=["Responsável", "Progresso"],
        title="Cronograma das iniciativas",
    )

    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# GAP ANALYSIS
# ============================================================

def modulo_gap_analysis():
    exibir_cabecalho(
        "Gap Analysis",
        "Comparativo entre a maturidade atual e a desejada.",
    )

    organizacao, dados = exigir_organizacao()
    organizacao_id = organizacao["id"]
    scores, _ = calcular_scores_assessment(dados)

    resultados = []

    for dimensao in DIMENSOES_NIST:
        atual = scores.get(dimensao, 0)
        desejado_salvo = int(
            dados["gap_analysis"].get(dimensao, 80)
        )

        desejado = st.slider(
            f"Meta de maturidade — {dimensao}",
            min_value=0,
            max_value=100,
            value=desejado_salvo,
            step=5,
            key=f"gap_{organizacao_id}_{dimensao}",
        )

        dados["gap_analysis"][dimensao] = desejado

        resultados.append(
            {
                "Dimensão": dimensao,
                "Atual": atual,
                "Desejado": desejado,
                "Gap": round(max(0, desejado - atual), 1),
            }
        )

    df = pd.DataFrame(resultados)

    st.dataframe(df, use_container_width=True, hide_index=True)

    df_grafico = df.melt(
        id_vars="Dimensão",
        value_vars=["Atual", "Desejado"],
        var_name="Cenário",
        value_name="Maturidade",
    )

    fig = px.bar(
        df_grafico,
        x="Dimensão",
        y="Maturidade",
        color="Cenário",
        barmode="group",
        range_y=[0, 100],
        title="Maturidade atual versus desejada",
    )

    st.plotly_chart(fig, use_container_width=True)

    maior_gap = df.sort_values(
        "Gap",
        ascending=False,
    ).iloc[0]

    st.info(
        f"Prioridade recomendada: **{maior_gap['Dimensão']}**, "
        f"com gap de **{maior_gap['Gap']:.1f} pontos**."
    )


# ============================================================
# COMPLIANCE
# ============================================================

def modulo_adequacao():
    exibir_cabecalho(
        "Adequação LGPD, NIST e ISO 27001",
        "Acompanhamento dos controles de conformidade.",
    )

    organizacao, dados = exigir_organizacao()
    organizacao_id = organizacao["id"]

    framework = st.selectbox(
        "Framework",
        options=list(CONTROLES_COMPLIANCE.keys()),
    )

    if framework not in dados["compliance"]:
        dados["compliance"][framework] = {}

    controles_framework = dados["compliance"][framework]
    controles = CONTROLES_COMPLIANCE[framework]

    status_opcoes = [
        "Não avaliado",
        "Não conforme",
        "Parcialmente conforme",
        "Conforme",
    ]

    pontuacao_status = {
        "Não avaliado": 0,
        "Não conforme": 0,
        "Parcialmente conforme": 50,
        "Conforme": 100,
    }

    for indice, controle in enumerate(controles):
        chave = f"controle_{indice}"

        if chave not in controles_framework:
            controles_framework[chave] = {
                "status": "Não avaliado",
                "evidencia": "",
            }

        registro = controles_framework[chave]
        chave_base = (
            f"compliance_{organizacao_id}_"
            f"{framework}_{indice}"
        )

        with st.expander(controle, expanded=True):
            status_atual = registro.get(
                "status",
                "Não avaliado",
            )

            status = st.selectbox(
                "Status",
                options=status_opcoes,
                index=status_opcoes.index(status_atual),
                key=f"{chave_base}_status",
            )

            evidencia = st.text_area(
                "Evidência ou observação",
                value=registro.get("evidencia", ""),
                key=f"{chave_base}_evidencia",
            )

            controles_framework[chave] = {
                "controle": controle,
                "status": status,
                "evidencia": evidencia,
            }

    valores = [
        pontuacao_status[
            controles_framework[f"controle_{indice}"]["status"]
        ]
        for indice in range(len(controles))
    ]

    percentual = (
        round(sum(valores) / len(valores), 1)
        if valores
        else 0
    )

    st.metric(
        f"Conformidade — {framework}",
        f"{percentual:.1f}%",
    )
    st.progress(percentual / 100)

    df = pd.DataFrame(
        [
            {
                "Controle": controles_framework[
                    f"controle_{indice}"
                ].get("controle", controle),
                "Status": controles_framework[
                    f"controle_{indice}"
                ]["status"],
                "Evidência": controles_framework[
                    f"controle_{indice}"
                ]["evidencia"],
            }
            for indice, controle in enumerate(controles)
        ]
    )

    st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================
# REUNIÕES
# ============================================================

def modulo_reunioes():
    exibir_cabecalho(
        "Reuniões",
        "Registro de atas, decisões e próximos passos.",
    )

    _, dados = exigir_organizacao()

    with st.form("form_reuniao", clear_on_submit=True):
        titulo = st.text_input("Título da reunião")
        data_reuniao = st.date_input("Data")
        participantes = st.text_input("Participantes")
        pauta = st.text_area("Pauta")
        ata = st.text_area("Ata e decisões", height=180)
        proximos_passos = st.text_area("Próximos passos")

        salvar = st.form_submit_button(
            "Salvar reunião",
            type="primary",
        )

        if salvar:
            if not titulo.strip():
                st.error("Informe o título da reunião.")
            else:
                dados["reunioes"].append(
                    {
                        "ID": gerar_id("reuniao"),
                        "Título": titulo.strip(),
                        "Data": data_reuniao.isoformat(),
                        "Participantes": participantes.strip(),
                        "Pauta": pauta.strip(),
                        "Ata": ata.strip(),
                        "Próximos passos": proximos_passos.strip(),
                    }
                )
                st.success("Reunião registrada.")
                st.rerun()

    colunas = [
        "ID",
        "Título",
        "Data",
        "Participantes",
        "Pauta",
        "Ata",
        "Próximos passos",
    ]

    df = normalizar_dataframe(
        dados["reunioes"],
        colunas,
    )

    if df.empty:
        st.info("Nenhuma reunião registrada.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)

    for reuniao in dados["reunioes"]:
        with st.expander(
            f"{reuniao['Data']} — {reuniao['Título']}"
        ):
            st.write(
                f"**Participantes:** "
                f"{reuniao['Participantes'] or 'Não informado'}"
            )
            st.write(f"**Pauta:** {reuniao['Pauta']}")
            st.write(f"**Ata:** {reuniao['Ata']}")
            st.write(
                f"**Próximos passos:** "
                f"{reuniao['Próximos passos']}"
            )


# ============================================================
# RELATÓRIOS E EXPORTAÇÕES
# ============================================================

def gerar_resumo_executivo(organizacao, dados):
    scores, score_geral = calcular_scores_assessment(dados)
    contagem_riscos = estatisticas_riscos(dados)

    resumo = [
        {
            "Indicador": "Organização",
            "Valor": organizacao["nome"],
        },
        {
            "Indicador": "Data do relatório",
            "Valor": datetime.now().strftime("%d/%m/%Y %H:%M"),
        },
        {
            "Indicador": "Maturidade geral",
            "Valor": f"{score_geral:.1f}%",
        },
        {
            "Indicador": "Classificação",
            "Valor": classificar_maturidade(score_geral),
        },
        {
            "Indicador": "Total de riscos",
            "Valor": len(dados["riscos"]),
        },
        {
            "Indicador": "Riscos críticos",
            "Valor": contagem_riscos["Crítico"],
        },
        {
            "Indicador": "Total de ações",
            "Valor": len(dados["acoes"]),
        },
    ]

    for dimensao, score in scores.items():
        resumo.append(
            {
                "Indicador": f"Maturidade — {dimensao}",
                "Valor": f"{score:.1f}%",
            }
        )

    return pd.DataFrame(resumo)


def gerar_csv_consolidado(organizacao, dados):
    buffer = io.StringIO()

    buffer.write("CTR DEFENSE - RELATÓRIO CONSOLIDADO\n")
    buffer.write(f"Organização;{organizacao['nome']}\n")
    buffer.write(
        f"Data;{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    )

    scores, geral = calcular_scores_assessment(dados)

    buffer.write("RESUMO DE MATURIDADE\n")
    buffer.write("Dimensão;Score\n")

    for dimensao, score in scores.items():
        buffer.write(f"{dimensao};{score:.1f}%\n")

    buffer.write(f"Maturidade geral;{geral:.1f}%\n\n")

    secoes = [
        ("RISCOS", dados["riscos"]),
        ("PLANO DE AÇÃO", dados["acoes"]),
        ("ROADMAP", dados["roadmap"]),
        ("REUNIÕES", dados["reunioes"]),
    ]

    for titulo, registros in secoes:
        buffer.write(f"{titulo}\n")

        if registros:
            df = pd.DataFrame(registros)
            buffer.write(
                df.to_csv(
                    index=False,
                    sep=";",
                    lineterminator="\n",
                )
            )
        else:
            buffer.write("Nenhum registro\n")

        buffer.write("\n")

    buffer.write("COMPLIANCE\n")

    registros_compliance = []

    for framework, controles in dados["compliance"].items():
        for controle in controles.values():
            registros_compliance.append(
                {
                    "Framework": framework,
                    "Controle": controle.get("controle", ""),
                    "Status": controle.get("status", ""),
                    "Evidência": controle.get("evidencia", ""),
                }
            )

    if registros_compliance:
        buffer.write(
            pd.DataFrame(registros_compliance).to_csv(
                index=False,
                sep=";",
                lineterminator="\n",
            )
        )
    else:
        buffer.write("Nenhum registro\n")

    return buffer.getvalue().encode("utf-8-sig")


def modulo_relatorios():
    exibir_cabecalho(
        "Relatórios",
        "Exportação dos dados e resultados da consultoria.",
    )

    organizacao, dados = exigir_organizacao()

    nome_arquivo = (
        organizacao["nome"]
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )

    resumo = gerar_resumo_executivo(
        organizacao,
        dados,
    )

    st.subheader("Resumo executivo")
    st.dataframe(
        resumo,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Baixar resumo executivo em CSV",
        data=dataframe_csv(resumo),
        file_name=f"{nome_arquivo}_resumo.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Baixar relatório consolidado em CSV",
        data=gerar_csv_consolidado(
            organizacao,
            dados,
        ),
        file_name=f"{nome_arquivo}_relatorio_consolidado.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Exportações por módulo")

    exportacoes = [
        (
            "Riscos",
            dados["riscos"],
            f"{nome_arquivo}_riscos.csv",
        ),
        (
            "Plano de ação",
            dados["acoes"],
            f"{nome_arquivo}_acoes.csv",
        ),
        (
            "Roadmap",
            dados["roadmap"],
            f"{nome_arquivo}_roadmap.csv",
        ),
        (
            "Reuniões",
            dados["reunioes"],
            f"{nome_arquivo}_reunioes.csv",
        ),
    ]

    colunas = st.columns(2)

    for indice, (titulo, registros, arquivo) in enumerate(exportacoes):
        df = pd.DataFrame(registros)

        if df.empty:
            df = pd.DataFrame(
                [{"Informação": "Nenhum registro cadastrado"}]
            )

        colunas[indice % 2].download_button(
            f"Baixar {titulo}",
            data=dataframe_csv(df),
            file_name=arquivo,
            mime="text/csv",
            use_container_width=True,
            key=f"download_{titulo}",
        )

    st.info(
        "Os dados estão armazenados em `st.session_state`. "
        "Eles serão perdidos se o servidor reiniciar. Para produção, "
        "utilize SQLite, PostgreSQL ou outro banco persistente."
    )


# ============================================================
# EXECUÇÃO
# ============================================================

exigir_autenticacao()
inicializar_estado()

menu = construir_sidebar()

if menu == "Dashboard Executivo":
    modulo_dashboard()

elif menu == "Organizações":
    modulo_organizacoes()

elif menu == "Assessment NIST CSF":
    modulo_assessment()

elif menu == "Matriz de Riscos":
    modulo_riscos()

elif menu == "Plano de Ação":
    modulo_plano_acao()

elif menu == "Roadmap de Segurança":
    modulo_roadmap()

elif menu == "Gap Analysis":
    modulo_gap_analysis()

elif menu == "Adequação LGPD/NIST/ISO":
    modulo_adequacao()

elif menu == "Reuniões":
    modulo_reunioes()

elif menu == "Relatórios":
    modulo_relatorios()
