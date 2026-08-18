import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Rosa 3D", page_icon="🌹", layout="wide")

# =========================================================
# Título y nota editables
# =========================================================
TITULO = "Para ti, la dueña de mi corazón 🌹"
NOTA = "Hice esta rosa en una superficie 3D con funciones parametricas, no olvides lo mucho que te amo ❤️"
 
st.markdown(
    f"""
    <div style="text-align:center; margin-top:0.5rem;">
        <h1 style="
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 3rem;
            font-style: italic;
            color: #b3134c;
            margin-bottom: 0.2rem;
        ">{TITULO}</h1>
        <p style="
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 1.2rem;
            color: #555;
            max-width: 600px;
            margin: 0 auto;
        ">{NOTA}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

animate = st.checkbox("Animar (florecer)", value=False)

st.divider()

# =========================================================
COLS, ROWS = 300, 40          # resolución (theta, r)
TOTAL_DEG = 180 * 15          # 7.5 vueltas
T_D = TOTAL_DEG / COLS
R_D = 1.0 / ROWS

OPENING = 2
V_DENSITY = 8
P_ALIGN = 3.6
CURVE1 = 2
CURVE2 = 1.3
SCALE = 260

theta_full = np.arange(0, COLS + 1) * T_D          # grados
r_idx = np.arange(0, ROWS + 1) * R_D               # 0..1


def surface_arrays(theta_slice):
    THETA, R = np.meshgrid(theta_slice, r_idx)
    phi_deg = (180 / OPENING) * np.exp(-THETA / (V_DENSITY * 180))
    phi = np.radians(phi_deg)
    petal_cut = 1 - 0.5 * (1.25 * (1 - np.mod(P_ALIGN * THETA, 360) / 180) ** 2 - 0.25) ** 2
    hang_down = CURVE1 * (R ** 2) * (CURVE2 * R - 1) ** 2 * np.sin(phi)

    r2 = R * np.sin(phi) + hang_down * np.cos(phi)
    theta_rad = np.radians(THETA)

    px = SCALE * petal_cut * r2 * np.sin(theta_rad)
    pz = SCALE * petal_cut * r2 * np.cos(theta_rad)
    py = SCALE * petal_cut * (R * np.cos(phi) - hang_down * np.sin(phi))  # altura (hacia arriba)

    return px, pz, py, THETA


base_layout = dict(
    scene=dict(
        xaxis_visible=False,
        yaxis_visible=False,
        zaxis_visible=False,
        aspectmode="data",
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=0, b=0),
    height=700,
    showlegend=False,
)


def make_surface(theta_slice):
    x, y, z, THETA = surface_arrays(theta_slice)
    return go.Surface(
        x=x, y=y, z=z,
        surfacecolor=THETA,
        colorscale=[[0, "#9d0707"], [0.5, "#800d0d"], [1, "#5c0033"]],
        showscale=False,
        lighting=dict(ambient=0.55, diffuse=0.9, specular=0.4, roughness=0.4),
    )


if animate:
    n_frames = 30
    counts = np.linspace(max(8, (COLS + 1) // n_frames), COLS + 1, n_frames).astype(int)
    fig = go.Figure(data=[make_surface(theta_full[: counts[0]])])
    fig.frames = [
        go.Frame(data=[make_surface(theta_full[:c])], name=str(k))
        for k, c in enumerate(counts)
    ]
    fig.update_layout(
        **base_layout,
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0, y=0, xanchor="left", yanchor="top",
                buttons=[
                    dict(
                        label="▶ Reproducir",
                        method="animate",
                        args=[None, dict(
                            frame=dict(duration=90, redraw=True),
                            fromcurrent=True, transition=dict(duration=0),
                        )],
                    ),
                    dict(
                        label="⏸ Pausa",
                        method="animate",
                        args=[[None], dict(
                            frame=dict(duration=0, redraw=False), mode="immediate",
                        )],
                    ),
                ],
            )
        ],
    )
else:
    fig = go.Figure(data=[make_surface(theta_full)])
    fig.update_layout(**base_layout)

st.plotly_chart(fig, use_container_width=True)
