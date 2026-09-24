import math
import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Pipe Flow Calculator",
    page_icon="🚰",
    layout="wide"
)

G = 9.81  # Gravitational acceleration (m/s²)


# =========================================================
# CORE CALCULATION FUNCTIONS
# =========================================================

def reynolds_number(rho, velocity, diameter, viscosity):
    """Calculate Reynolds number using dynamic viscosity."""
    if viscosity <= 0 or diameter <= 0:
        return 0.0

    return (rho * velocity * diameter) / viscosity


def kinematic_viscosity(viscosity, rho):
    """Calculate kinematic viscosity."""
    if rho <= 0:
        return 0.0

    return viscosity / rho


def relative_roughness(roughness, diameter):
    """Calculate relative pipe roughness."""
    if diameter <= 0:
        return 0.0

    return roughness / diameter


def laminar_friction_factor(Re):
    """Darcy friction factor for laminar flow."""
    if Re <= 0:
        return 0.0

    return 64.0 / Re


def turbulent_friction_factor(Re, roughness, diameter):
    """
    Calculate Darcy friction factor using the
    Colebrook-White equation with fixed-point iteration.
    """
    if Re <= 0 or diameter <= 0:
        return 0.0

    f = 0.02

    for _ in range(100):
        old_f = f

        try:
            term = (
                roughness / (3.7 * diameter)
                + 2.51 / (Re * math.sqrt(f))
            )

            if term <= 0:
                break

            f = 1.0 / (-2.0 * math.log10(term)) ** 2

        except (ValueError, ZeroDivisionError):
            break

        if abs(f - old_f) < 1e-8:
            break

    return f


def friction_factor(Re, roughness, diameter):
    """Determine Darcy friction factor based on flow regime."""
    if Re <= 0:
        return 0.0

    if Re < 2300:
        return laminar_friction_factor(Re)

    return turbulent_friction_factor(Re, roughness, diameter)


def flow_regime(Re):
    """Determine flow regime from Reynolds number."""
    if Re <= 0:
        return "Invalid / No Flow"
    elif Re < 2300:
        return "Laminar"
    elif Re <= 4000:
        return "Transitional"
    else:
        return "Turbulent"


def head_loss(f, length, diameter, velocity):
    """Calculate Darcy-Weisbach head loss."""
    if diameter <= 0:
        return 0.0

    return (
        f
        * (length / diameter)
        * (velocity ** 2 / (2 * G))
    )


def pressure_drop(rho, head_loss_value):
    """Convert head loss to pressure drop."""
    return rho * G * head_loss_value


def pascal_to_kpa(pressure_pa):
    """Convert Pa to kPa."""
    return pressure_pa / 1000.0


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🚰 Pipe Flow & Fluid Mechanics Calculator")

st.markdown(
    """
    Calculate **Reynolds number, flow regime, friction factor,
    Darcy-Weisbach head loss, and pressure drop** for flow through
    circular pipes.
    """
)

st.divider()


# =========================================================
# TABS
# =========================================================

tab_all, tab_re, tab_f, tab_hf, tab_dp = st.tabs(
    [
        "⚡ Comprehensive Analysis",
        "📊 Reynolds Number",
        "🌀 Friction Factor",
        "📏 Head Loss",
        "💥 Pressure Drop",
    ]
)


# =========================================================
# TAB 1: COMPREHENSIVE ANALYSIS
# =========================================================

with tab_all:

    st.header("Full System Calculation")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fluid Properties")

        rho = st.number_input(
            "Density, ρ (kg/m³)",
            min_value=0.0001,
            value=1000.0,
            step=10.0,
            key="all_rho"
        )

        viscosity = st.number_input(
            "Dynamic Viscosity, μ (Pa·s)",
            min_value=0.000001,
            value=0.001002,
            format="%.6f",
            key="all_visc"
        )

    with col2:
        st.subheader("Pipe & Flow Parameters")

        diameter = st.number_input(
            "Pipe Diameter, D (m)",
            min_value=0.0001,
            value=0.05,
            format="%.4f",
            key="all_d"
        )

        length = st.number_input(
            "Pipe Length, L (m)",
            min_value=0.0,
            value=10.0,
            step=1.0,
            key="all_l"
        )

        velocity = st.number_input(
            "Fluid Velocity, V (m/s)",
            min_value=0.0,
            value=2.0,
            step=0.1,
            key="all_v"
        )

        roughness = st.number_input(
            "Pipe Roughness, ε (m)",
            min_value=0.0,
            value=0.000045,
            format="%.6f",
            key="all_e"
        )

    if st.button(
        "🚀 Run Full Calculation",
        type="primary",
        use_container_width=True
    ):

        Re = reynolds_number(
            rho,
            velocity,
            diameter,
            viscosity
        )

        nu = kinematic_viscosity(
            viscosity,
            rho
        )

        regime = flow_regime(Re)

        rr = relative_roughness(
            roughness,
            diameter
        )

        f = friction_factor(
            Re,
            roughness,
            diameter
        )

        hf = head_loss(
            f,
            length,
            diameter,
            velocity
        )

        delta_p = pressure_drop(
            rho,
            hf
        )

        delta_p_kpa = pascal_to_kpa(delta_p)

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        st.divider()
        st.subheader("📊 Results")

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Reynolds Number",
            f"{Re:,.2f}"
        )

        m2.metric(
            "Flow Regime",
            regime
        )

        m3.metric(
            "Darcy Friction Factor",
            f"{f:.6f}"
        )

        m4, m5, m6 = st.columns(3)

        m4.metric(
            "Kinematic Viscosity",
            f"{nu:.8f} m²/s"
        )

        m5.metric(
            "Relative Roughness",
            f"{rr:.6f}"
        )

        m6.metric(
            "Head Loss",
            f"{hf:.4f} m"
        )

        st.divider()

        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.metric(
                "Pressure Drop",
                f"{delta_p:,.2f} Pa",
                f"{delta_p_kpa:.4f} kPa"
            )

        with res_col2:
            st.metric(
                "Pressure Drop in kPa",
                f"{delta_p_kpa:.4f} kPa"
            )


# =========================================================
# TAB 2: REYNOLDS NUMBER
# =========================================================

with tab_re:

    st.header("📊 Reynolds Number & Flow Regime")

    c1, c2 = st.columns(2)

    with c1:
        rho_re = st.number_input(
            "Density (kg/m³)",
            min_value=0.0001,
            value=1000.0,
            key="re_rho"
        )

        d_re = st.number_input(
            "Diameter (m)",
            min_value=0.0001,
            value=0.05,
            format="%.4f",
            key="re_d"
        )

    with c2:
        v_re = st.number_input(
            "Velocity (m/s)",
            min_value=0.0,
            value=2.0,
            key="re_v"
        )

        mu_re = st.number_input(
            "Dynamic Viscosity (Pa·s)",
            min_value=0.000001,
            value=0.001002,
            format="%.6f",
            key="re_mu"
        )

    if st.button(
        "Calculate Reynolds Number",
        use_container_width=True,
        key="calculate_re"
    ):

        Re_val = reynolds_number(
            rho_re,
            v_re,
            d_re,
            mu_re
        )

        reg_val = flow_regime(Re_val)

        col1, col2 = st.columns(2)

        col1.metric(
            "Reynolds Number",
            f"{Re_val:,.2f}"
        )

        col2.metric(
            "Flow Regime",
            reg_val
        )


# =========================================================
# TAB 3: FRICTION FACTOR
# =========================================================

with tab_f:

    st.header("🌀 Darcy Friction Factor")

    Re_f = st.number_input(
        "Reynolds Number",
        min_value=0.0,
        value=100000.0,
        step=1000.0,
        key="f_re"
    )

    d_f = st.number_input(
        "Pipe Diameter (m)",
        min_value=0.0001,
        value=0.05,
        format="%.4f",
        key="f_d"
    )

    e_f = st.number_input(
        "Pipe Roughness (m)",
        min_value=0.0,
        value=0.000045,
        format="%.6f",
        key="f_e"
    )

    if st.button(
        "Calculate Friction Factor",
        use_container_width=True,
        key="calculate_f"
    ):

        f_val = friction_factor(
            Re_f,
            e_f,
            d_f
        )

        st.success(
            f"**Darcy Friction Factor:** {f_val:.6f}"
        )


# =========================================================
# TAB 4: HEAD LOSS
# =========================================================

with tab_hf:

    st.header("📏 Darcy-Weisbach Head Loss")

    c1, c2 = st.columns(2)

    with c1:

        f_hf = st.number_input(
            "Darcy Friction Factor",
            min_value=0.0,
            value=0.02,
            format="%.4f",
            key="hf_f"
        )

        d_hf = st.number_input(
            "Pipe Diameter (m)",
            min_value=0.0001,
            value=0.05,
            format="%.4f",
            key="hf_d"
        )

    with c2:

        l_hf = st.number_input(
            "Pipe Length (m)",
            min_value=0.0,
            value=10.0,
            key="hf_l"
        )

        v_hf = st.number_input(
            "Velocity (m/s)",
            min_value=0.0,
            value=2.0,
            key="hf_v"
        )

    if st.button(
        "Calculate Head Loss",
        use_container_width=True,
        key="calculate_hf"
    ):

        hf_val = head_loss(
            f_hf,
            l_hf,
            d_hf,
            v_hf
        )

        st.success(
            f"**Head Loss:** {hf_val:.4f} m"
        )


# =========================================================
# TAB 5: PRESSURE DROP
# =========================================================

with tab_dp:

    st.header("💥 Pressure Drop")

    c1, c2 = st.columns(2)

    with c1:

        rho_dp = st.number_input(
            "Density (kg/m³)",
            min_value=0.0001,
            value=1000.0,
            key="dp_rho"
        )

        l_dp = st.number_input(
            "Pipe Length (m)",
            min_value=0.0,
            value=10.0,
            key="dp_l"
        )

    with c2:

        f_dp = st.number_input(
            "Darcy Friction Factor",
            min_value=0.0,
            value=0.02,
            format="%.4f",
            key="dp_f"
        )

        d_dp = st.number_input(
            "Pipe Diameter (m)",
            min_value=0.0001,
            value=0.05,
            key="dp_d"
        )

    v_dp = st.number_input(
        "Velocity (m/s)",
        min_value=0.0,
        value=2.0,
        key="dp_v"
    )

    if st.button(
        "Calculate Pressure Drop",
        use_container_width=True,
        key="calculate_dp"
    ):

        hf_calc = head_loss(
            f_dp,
            l_dp,
            d_dp,
            v_dp
        )

        dp_pa = pressure_drop(
            rho_dp,
            hf_calc
        )

        dp_kpa = pascal_to_kpa(dp_pa)

        col_a, col_b, col_c = st.columns(3)

        col_a.metric(
            "Head Loss",
            f"{hf_calc:.4f} m"
        )

        col_b.metric(
            "Pressure Drop",
            f"{dp_pa:,.2f} Pa"
        )

        col_c.metric(
            "Pressure Drop",
            f"{dp_kpa:.4f} kPa"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Pipe Flow & Fluid Mechanics Calculator | "
    "Darcy-Weisbach equation and Colebrook-White friction factor"
)
