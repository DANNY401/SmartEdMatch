"""
SmartEdMatch — Interactive Nigeria Map Service
Renders a live interactive map of Nigeria showing recommended institutions.

INSTALL:
pip install folium streamlit-folium

No API key needed — uses OpenStreetMap tiles (completely free).
"""

# ── Institution coordinates ───────────────────────────────────────────────────
# GPS coordinates for each institution in the dataset
INSTITUTION_COORDS = {
    # Federal Universities
    "University of Lagos":               (6.5158, 3.3898),
    "University of Ibadan":              (7.3775, 3.9470),
    "Obafemi Awolowo University":        (7.5189, 4.5234),
    "University of Nigeria Nsukka":      (6.8636, 7.3961),
    "Ahmadu Bello University":           (11.1581, 7.6494),
    "University of Benin":               (6.3612, 5.6218),
    "University of Port Harcourt":       (4.8979, 6.9065),
    "University of Ilorin":              (8.4799, 4.6418),
    "Nnamdi Azikiwe University":         (6.2103, 7.0675),
    "Federal University of Technology Akure": (7.2526, 5.2034),
    "Federal University of Technology Minna": (9.6139, 6.5569),
    "Federal University of Technology Owerri": (5.4920, 7.0331),
    "Bayero University Kano":            (12.0022, 8.5920),
    "University of Calabar":             (4.9516, 8.3225),
    "University of Abuja":               (8.8833, 7.1675),
    "University of Maiduguri":           (11.8333, 13.1517),
    "Usman Dan Fodio University":        (13.0622, 5.2339),
    "Federal University Lokoja":         (7.7973, 6.7377),
    "Federal University Lafia":          (8.4945, 8.5038),
    "Federal University Dutse":          (11.6666, 9.3431),

    # Private Universities
    "Covenant University":               (6.6731, 3.1578),
    "Babcock University":                (6.8917, 3.7203),
    "American University of Nigeria":    (10.1729, 13.3044),
    "Pan-Atlantic University":           (6.5087, 3.3624),
    "Redeemer's University":             (7.4706, 4.2458),
    "Landmark University":               (8.5333, 4.5333),
    "Afe Babalola University":           (7.7167, 5.2167),
    "Bowen University":                  (7.4500, 4.6500),
    "Baze University":                   (9.0574, 7.4898),
    "Nile University of Nigeria":        (9.0500, 7.5167),
    "Madonna University":                (6.0667, 6.8500),
    "Igbinedion University":             (6.3067, 5.6142),
    "Veritas University Abuja":          (8.9167, 7.2333),

    # State Universities
    "Lagos State University":            (6.5156, 3.3720),
    "Rivers State University":           (4.8156, 7.0498),
    "Kogi State University":             (7.8028, 6.7394),
    "Delta State University":            (5.5372, 5.9748),
    "Imo State University":              (5.4895, 7.0395),
    "Enugu State University":            (6.4415, 7.5071),
    "Ekiti State University":            (7.7333, 5.2167),
    "Osun State University":             (7.5500, 4.5667),
    "Kaduna State University":           (10.5239, 7.4381),
    "Kano State University of Science and Technology": (12.0022, 8.5920),

    # Polytechnics
    "Yaba College of Technology":        (6.5167, 3.3667),
    "Federal Polytechnic Nekede":        (5.4795, 7.0218),
    "Federal Polytechnic Ilaro":         (6.8878, 3.0202),
    "Federal Polytechnic Bida":          (9.0833, 6.0167),
    "Federal Polytechnic Bauchi":        (10.3167, 9.8333),
    "Kaduna Polytechnic":                (10.5239, 7.4381),
    "The Polytechnic Ibadan":            (7.3775, 3.9470),
    "Lagos State Polytechnic":           (6.5156, 3.3720),

    # Colleges of Education
    "Federal College of Education Zaria":    (11.0667, 7.7167),
    "Federal College of Education Abeokuta": (7.1475, 3.3619),
    "Federal College of Education Kano":     (12.0022, 8.5920),
    "Adeyemi College of Education":          (7.1667, 4.8333),
    "Alvan Ikoku Federal College of Education": (5.4895, 7.0395),
}

# ── Pin colours by institution type ──────────────────────────────────────────
TYPE_COLOURS = {
    "Federal University":         "#2563EB",   # blue
    "State University":           "#06B6D4",   # cyan
    "Private University":         "#8B5CF6",   # purple
    "Federal Polytechnic":        "#F59E0B",   # gold
    "State Polytechnic":          "#F97316",   # orange
    "Federal College of Education": "#10B981", # green
    "State College of Education":   "#34D399", # light green
}

TYPE_ICONS = {
    "Federal University":           "university",
    "State University":             "university",
    "Private University":           "graduation-cap",
    "Federal Polytechnic":          "wrench",
    "State Polytechnic":            "wrench",
    "Federal College of Education": "book",
    "State College of Education":   "book",
}


def build_institution_map(results_df, student_zone: str = None):
    """
    Build an interactive Folium map showing recommended institutions.

    Args:
        results_df: DataFrame of recommended institutions (from engine.recommend())
        student_zone: The student's preferred geopolitical zone (optional)

    Returns:
        A Folium map object ready for st_folium()
    """
    try:
        import folium
    except ImportError:
        return None

    # Nigeria centre coordinates
    NIGERIA_CENTER = (9.0820, 8.6753)

    # Create map
    m = folium.Map(
        location=NIGERIA_CENTER,
        zoom_start=6,
        tiles="CartoDB dark_matter",
        prefer_canvas=True
    )

    # Add Nigeria boundary outline
    folium.GeoJson(
        "https://raw.githubusercontent.com/deldersveld/topojson/master/countries/nigeria/nigeria-regions.json",
        name="Nigeria Regions",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#334155",
            "weight": 1,
            "opacity": 0.5
        }
    ).add_to(m)

    if results_df is None or results_df.empty:
        return m

    # Add institution pins
    for rank, row in results_df.iterrows():
        inst_name  = str(row["university_name"])
        inst_type  = str(row["type"])
        score      = float(row["similarity_pct"])
        cutoff     = int(row["jamb_cutoff"])
        state      = str(row["state"])
        course     = str(row["course"])
        tuition_min = int(row["tuition_min"])
        tuition_max = int(row["tuition_max"])

        coords = INSTITUTION_COORDS.get(inst_name)
        if not coords:
            continue

        colour = TYPE_COLOURS.get(inst_type, "#64748B")
        medal  = {1: "🥇", 2: "🥈", 3: "🥉"}.get(int(rank), f"#{rank}")

        # Score colour
        if score >= 70:
            score_colour = "#10B981"
        elif score >= 45:
            score_colour = "#3B82F6"
        else:
            score_colour = "#F59E0B"

        # Popup HTML
        popup_html = f"""
        <div style="
            background:#0B1A2E;
            border:1px solid rgba(255,255,255,0.1);
            border-radius:12px;
            padding:14px 16px;
            min-width:240px;
            font-family:Arial,sans-serif;
            color:#E2E8F0;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:16px;">{medal}</span>
                <span style="font-weight:700;font-size:13px;">{inst_name}</span>
            </div>
            <div style="font-size:11px;color:#64748B;margin-bottom:10px;">📍 {state}</div>

            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">
                <span style="background:rgba(37,99,235,0.2);color:#93C5FD;border-radius:20px;
                padding:2px 8px;font-size:10px;font-weight:600;">{course}</span>
                <span style="background:rgba(139,92,246,0.2);color:#C4B5FD;border-radius:20px;
                padding:2px 8px;font-size:10px;font-weight:600;">{inst_type}</span>
            </div>

            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:10px;color:#64748B;">Match Score</span>
                <span style="font-size:13px;font-weight:800;color:{score_colour};">{score:.1f}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:10px;color:#64748B;">JAMB Cut-off</span>
                <span style="font-size:12px;font-weight:700;color:#FCD34D;">{cutoff}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:10px;color:#64748B;">Tuition</span>
                <span style="font-size:11px;color:#6EE7B7;">₦{tuition_min:,} – ₦{tuition_max:,}</span>
            </div>
        </div>
        """

        # Score bar (draw a circle with the score baked in)
        circle_radius = 8 + (score / 100) * 8   # 8–16px radius based on match score

        # Add circle marker
        folium.CircleMarker(
            location=coords,
            radius=circle_radius,
            color=colour,
            fill=True,
            fill_color=colour,
            fill_opacity=0.7,
            weight=2,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{medal} {inst_name} — {score:.0f}% match"
        ).add_to(m)

        # Add rank label
        folium.Marker(
            location=coords,
            icon=folium.DivIcon(
                html=f"""<div style="
                    background:{colour};
                    color:white;
                    border-radius:50%;
                    width:20px;height:20px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:9px;font-weight:800;
                    border:2px solid white;
                    margin-top:-10px;margin-left:-10px;
                ">{rank}</div>""",
                icon_size=(20, 20),
                icon_anchor=(10, 10)
            ),
            tooltip=inst_name
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="
        position:fixed;bottom:30px;right:10px;z-index:1000;
        background:#0B1A2E;border:1px solid rgba(255,255,255,0.1);
        border-radius:12px;padding:12px 16px;font-family:Arial,sans-serif;
    ">
        <div style="font-size:11px;font-weight:700;color:#E2E8F0;margin-bottom:8px;">Institution Type</div>
        <div style="display:flex;flex-direction:column;gap:5px;">
    """
    for itype, colour in TYPE_COLOURS.items():
        legend_html += f"""
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:10px;height:10px;border-radius:50%;background:{colour};"></div>
                <span style="font-size:10px;color:#94A3B8;">{itype}</span>
            </div>
        """
    legend_html += "</div></div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def render_map_in_streamlit(results_df, student_zone: str = None):
    """
    Render the interactive map in a Streamlit app.

    Usage in app.py:
        from map_service import render_map_in_streamlit
        render_map_in_streamlit(results, zone)
    """
    import streamlit as st

    try:
        from streamlit_folium import st_folium
    except ImportError:
        st.warning("📦 Install map libraries to enable the interactive map: `pip install folium streamlit-folium`")
        return

    m = build_institution_map(results_df, student_zone)
    if m is None:
        st.warning("Map could not be built.")
        return

    st.markdown("### 🗺️ Institutions on the Map")
    st.caption("Click any pin to see institution details. Pin size indicates match score.")

    st_folium(
        m,
        width=None,
        height=480,
        returned_objects=[]
    )
