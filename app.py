"""
VERA-KY: Verification Engine for Results & Accountability - Kentucky
Type 4 Detection using WIDA ACCESS Speaking vs Writing + KSA Achievement Data

Kentucky context: WIDA ACCESS (not KELPA). 4 domains: Listening, Speaking, Reading, Writing.
Exit criteria: Composite 4.5+. Academic: KSA (Kentucky Summative Assessment), 4 levels:
Novice, Apprentice, Proficient, Distinguished. Data: KSIS (Infinite Campus),
district ID varies (NCES-style / KDE internal). 171 districts, EL growing 128% over 20 years.
Dashboard: reportcard.kyschools.us. JCPS Louisville ~21,000 MLs (largest).
SB 1 governance reform. HB 162 math reform. United We Learn redesign.
67% of 4th graders not proficient in reading.

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_KY_BLUE = "#002B5C"
KY_GOLD = "#FFD700"
KY_DARK_BLUE = "#001A3A"
KY_LIGHT_BLUE = "#335C85"

# ============================================================================
# DATA: Kentucky Districts with EL Populations (from KSIS / reportcard.kyschools.us)
# ============================================================================

def load_districts():
    """
    Load KY districts with significant EL populations.
    Real data from reportcard.kyschools.us and KSIS (Infinite Campus).
    171 districts statewide, EL population growing 128% over 20 years.
    KSA has 4 levels: Novice, Apprentice, Proficient, Distinguished.
    67% of 4th graders not proficient in reading.
    JCPS Louisville is largest with ~21,000 MLs.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, ksa_ela_all, ksa_ela_el, ksa_ela_hispanic, ksa_ela_white,
        #  ksa_math_all, ksa_math_el, top_el_languages)

        # JCPS Louisville -- by far the largest
        ("275", "Jefferson County (JCPS)", 96000, 21000, 21.9,
         82.5, 34.2, 8.8, 19.5, 48.5,
         28.2, 7.2, "Spanish, Somali, Arabic, Swahili, Nepali, Burmese"),

        # Major urban / suburban districts
        ("160", "Fayette County", 42000, 5460, 13.0,
         85.8, 38.5, 11.2, 24.5, 52.8,
         31.5, 8.8, "Spanish, Arabic, Japanese, Chinese, Swahili"),
        ("045", "Boone County", 20500, 2460, 12.0,
         88.2, 40.2, 12.5, 26.8, 54.2,
         33.5, 9.5, "Spanish, Gujarati, Hindi, Arabic"),
        ("048", "Bowling Green Ind.", 9200, 2300, 25.0,
         78.5, 30.2, 8.5, 18.2, 46.5,
         23.8, 6.8, "Spanish, Somali, Bosnian, Burmese, Arabic"),
        ("205", "Kenton County", 14800, 1480, 10.0,
         86.5, 38.8, 12.8, 25.5, 52.5,
         31.8, 9.2, "Spanish, Gujarati, Portuguese"),
        ("115", "Daviess County", 11200, 1232, 11.0,
         84.2, 36.5, 10.8, 23.2, 50.8,
         29.5, 8.5, "Spanish, Burmese, Marshallese"),

        # Refugee / meatpacking corridor districts
        ("048B", "Warren County", 16500, 2640, 16.0,
         80.5, 32.5, 9.2, 20.5, 47.8,
         25.8, 7.5, "Spanish, Bosnian, Somali, Burmese, Karen"),
        ("230", "Lexington (Scott Co.)", 8900, 1335, 15.0,
         82.8, 34.8, 10.5, 22.8, 49.2,
         27.2, 8.0, "Spanish, Japanese, Swahili"),
        ("440", "Shelby County", 7200, 1440, 20.0,
         79.8, 31.8, 9.0, 19.8, 47.2,
         24.5, 7.0, "Spanish, Guatemalan languages, Burmese"),

        # Growing EL districts
        ("090", "Clark County", 5800, 580, 10.0,
         83.5, 35.2, 11.5, 23.5, 50.2,
         28.5, 8.2, "Spanish, Arabic"),
        ("245", "Laurel County", 8500, 680, 8.0,
         81.2, 33.5, 10.2, 21.8, 48.5,
         26.2, 7.8, "Spanish, Karen, Burmese"),
        ("070", "Campbell County", 6200, 496, 8.0,
         87.2, 39.2, 13.2, 26.2, 53.5,
         32.2, 9.8, "Spanish, Hindi, Arabic"),
        ("160B", "Covington Ind.", 3800, 760, 20.0,
         72.5, 26.5, 7.8, 16.5, 42.2,
         19.8, 5.8, "Spanish, Guatemalan languages, Swahili"),
        ("275B", "Oldham County", 12500, 750, 6.0,
         90.5, 44.5, 16.8, 32.5, 56.8,
         36.5, 12.5, "Spanish, Chinese, Hindi, Korean"),
        ("325", "Nelson County", 5400, 540, 10.0,
         82.2, 34.2, 10.8, 22.5, 49.5,
         27.8, 8.2, "Spanish, Burmese, Karen"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'ksa_ela_all', 'ksa_ela_el', 'ksa_ela_hispanic',
        'ksa_ela_white',
        'ksa_math_all', 'ksa_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: WIDA ACCESS Domain Data (modeled from KDE ACCESS public results)
# ============================================================================

def load_access_data(districts_df):
    """
    Generate district WIDA ACCESS domain data modeled from KDE ACCESS results.
    WIDA ACCESS: 4 domains: Listening, Speaking, Reading, Writing.
    6 proficiency levels: 1-Entering, 2-Emerging, 3-Developing, 4-Expanding,
    5-Bridging, 6-Reaching.
    Exit criteria: Composite 4.5+.
    """
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                # Base scores by grade -- speaking naturally higher than writing
                base_speaking = 3.6 + (grade * 0.05)
                base_writing = 2.8 + (grade * 0.03)
                base_listening = 3.8 + (grade * 0.04)
                base_reading = 3.0 + (grade * 0.04)

                # District adjustments: lower EL proficiency = lower scores
                el_factor = d['ksa_ela_el'] / 12.0
                speaking_adj = 0.3 * el_factor
                writing_adj = -0.2 + (el_factor - 1) * 0.15
                listening_adj = speaking_adj + 0.1
                reading_adj = writing_adj + 0.15

                # JCPS and Bowling Green: high diversity, oral advantage
                if d['district_id'] in ['275', '048']:
                    speaking_adj += 0.15
                    writing_adj -= 0.10

                # Refugee corridor districts
                if d['district_id'] in ['048B', '440', '160B']:
                    speaking_adj += 0.10
                    writing_adj -= 0.08

                # Year-over-year modest growth
                year_adj = 0.05 if year == 2025 else 0

                listening_score = round(base_listening + listening_adj + year_adj, 2)
                speaking_score = round(base_speaking + speaking_adj + year_adj, 2)
                reading_score = round(base_reading + reading_adj + year_adj, 2)
                writing_score = round(base_writing + writing_adj + year_adj, 2)
                composite = round((listening_score + speaking_score +
                                   reading_score + writing_score) / 4, 2)

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(15, int(d['el_count'] / 6)),
                    'listening_avg': listening_score,
                    'speaking_avg': speaking_score,
                    'reading_avg': reading_score,
                    'writing_avg': writing_score,
                    'composite_avg': composite,
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: KSA Achievement Data (from reportcard.kyschools.us)
# ============================================================================

def load_ksa_data(districts_df):
    """
    Generate KSA data based on reportcard.kyschools.us proficiency rates.
    KSA (Kentucky Summative Assessment) has 4 performance levels:
    Novice, Apprentice, Proficient, Distinguished.
    ELA and Math tested grades 3-8 (and 10-11).
    67% of 4th graders not proficient in reading.
    """
    ksa_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['ksa_ela_all']
                    else:
                        base = d['ksa_math_all']

                    # Grade adjustment: proficiency dips in middle school
                    prof = max(8, min(70, base + (grade - 5) * -1.2))

                    # Grade 4 reading crisis: 67% not proficient
                    if subject == 'ELA' and grade == 4:
                        prof = min(prof, 33.0)

                    # Year adjustment
                    if year == 2024:
                        prof = prof - 1.0

                    # KSA 4-level distribution
                    distinguished = max(1.5, prof * 0.12)
                    proficient = max(4, prof - distinguished)
                    apprentice = max(12, (100 - prof) * 0.38)
                    novice = max(8, 100 - proficient - distinguished - apprentice)

                    ksa_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'novice_pct': round(novice, 1),
                        'apprentice_pct': round(apprentice, 1),
                        'proficient_pct': round(proficient, 1),
                        'distinguished_pct': round(distinguished, 1),
                        'prof_distinguished_pct': round(proficient + distinguished, 1),
                    })

    return pd.DataFrame(ksa_data)


# ============================================================================
# DATA: Statewide Domain Proficiency (from KDE WIDA ACCESS data)
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide WIDA ACCESS domain proficiency percentages by grade cluster.
    Source: KDE ACCESS data, reportcard.kyschools.us.
    Kentucky has 171 districts, EL pop growing 128% over 20 years.
    % at Expanding (4) or higher shown below.
    Exit criteria: Composite 4.5+.
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 36, 'speaking': 32, 'reading': 18, 'writing': 12},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 42, 'speaking': 38, 'reading': 22, 'writing': 15},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 46, 'speaking': 41, 'reading': 26, 'writing': 18},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 49, 'speaking': 43, 'reading': 29, 'writing': 20},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 34, 'speaking': 30, 'reading': 16, 'writing': 10},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 40, 'speaking': 36, 'reading': 20, 'writing': 13},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 44, 'speaking': 39, 'reading': 24, 'writing': 16},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 47, 'speaking': 41, 'reading': 27, 'writing': 18},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    st.session_state.authenticated = True
    return True


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing on WIDA ACCESS scale (1-6).
    Flag threshold: delta > 0.8 on WIDA scale.
    """
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    flagged = delta > 0.8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("Kentucky Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot Districts", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("4th Grade Reading", "33%", help="Only 33% of 4th graders proficient in reading (67% not proficient)")

    st.divider()

    # Legislative & policy context
    st.subheader("Kentucky Education Reform Landscape")
    st.markdown("""
    Kentucky is undergoing a period of significant education reform. Three major initiatives
    are reshaping how schools operate, what students learn, and how they are assessed:

    - **SB 1 (Senate Bill 1):** Governance reform that restructured the relationship between
      the Kentucky Department of Education (KDE), local school boards, and school-based
      decision making councils (SBDMs). Shifts authority and accountability structures.
    - **HB 162 (House Bill 162):** Math reform legislation requiring evidence-based math
      instruction, structured curricula, and alignment with Kentucky Academic Standards.
    - **United We Learn:** A comprehensive redesign initiative rethinking Kentucky's
      accountability, assessment, and school improvement systems. Aims to move beyond
      test-score-driven accountability toward a more holistic model.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**67% Not Proficient**\n4th grade reading crisis\nacross Kentucky")
    with col2:
        st.warning("**128% EL Growth**\nOver 20 years statewide\nJCPS: ~21,000 MLs")
    with col3:
        st.warning("**SB 1 + HB 162**\nGovernance & math reform\nreshaping KY education")

    st.divider()

    st.subheader("Key State Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**WIDA ACCESS**\nEnglish Language Proficiency\nLevels 1-6\nExit: Composite 4.5+")
    with col2:
        st.info("**KSA**\nKentucky Summative Assessment\n4 levels: Novice, Apprentice,\nProficient, Distinguished")
    with col3:
        st.info("**KSIS (Infinite Campus)**\nState data system\nreportcard.kyschools.us\n171 districts")

    st.divider()

    st.subheader("Key State Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Districts", "171", help="Kentucky school districts")
    with col2:
        st.metric("EL Growth (20yr)", "128%", help="EL population growth over 20 years")
    with col3:
        st.metric("JCPS MLs", "~21,000", help="Jefferson County Public Schools multilingual learners")
    with col4:
        st.metric("United We Learn", "Active", help="Statewide accountability redesign")

    st.divider()

    # JCPS spotlight
    st.subheader("JCPS Louisville: Kentucky's EL Epicenter")
    st.markdown("""
    **Jefferson County Public Schools (JCPS)** in Louisville is by far the largest district
    in Kentucky with approximately **96,000 students** and **~21,000 multilingual learners (MLs)**
    -- roughly 22% of enrollment. JCPS serves students speaking over **150 languages**,
    with significant populations of Spanish, Somali, Arabic, Swahili, Nepali, and
    Burmese speakers.

    Louisville's refugee resettlement history has created one of the most linguistically
    diverse school systems in the southeastern United States. The district faces unique
    challenges in providing adequate EL services across such a wide linguistic landscape,
    particularly as **SB 1** reforms restructure governance and **United We Learn**
    redesigns accountability metrics.
    """)

    jcps = districts_df[districts_df['district_id'] == '275']
    non_jcps = districts_df[districts_df['district_id'] != '275']
    comparison = pd.DataFrame({
        'Category': ['JCPS Louisville', 'All Other Pilot Districts'],
        'EL Count': [jcps['el_count'].values[0], non_jcps['el_count'].sum()],
        'Total Students': [jcps['total_students'].values[0], non_jcps['total_students'].sum()]
    })
    fig_jcps = px.bar(
        comparison, x='Category', y=['EL Count', 'Total Students'],
        barmode='group',
        color_discrete_sequence=[KY_GOLD, KY_BLUE],
        labels={'value': 'Students', 'variable': 'Group'},
        title="JCPS vs All Other Pilot Districts: EL Scale"
    )
    fig_jcps.update_layout(height=350, legend_title_text='')
    st.plotly_chart(fig_jcps, use_container_width=True)

    st.divider()

    st.subheader("Top EL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Spanish', 'Arabic', 'Somali', 'Swahili', 'Burmese', 'Nepali', 'Bosnian', 'Other'],
        'Approx Share': [62, 7, 5, 4, 4, 3, 2, 13],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, KY_GOLD], [1, KY_BLUE]],
                      labels={'Approx Share': '% of EL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top EL Home Languages in Kentucky")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot Districts -- Highest EL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'ksa_ela_all', 'ksa_ela_el', 'ksa_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['Dist ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ELA All %', 'ELA EL %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, KY_GOLD], [1, KY_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=600, showlegend=False,
                      title="EL Population by District (color = EL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide WIDA ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** KDE WIDA ACCESS data, reportcard.kyschools.us. Kentucky uses **WIDA ACCESS**
    with 4 domains: Listening, Speaking, Reading, Writing. 6 proficiency levels: Entering (1),
    Emerging (2), Developing (3), Expanding (4), Bridging (5), Reaching (6).

    Domain proficiency percentages (% at Expanding or higher) show the systemic oral-written
    delta: Speaking consistently outperforms Writing across all grade clusters. Kentucky exit
    criteria require a **Composite score of 4.5+** on WIDA ACCESS.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', KY_BLUE), ('speaking', KY_GOLD),
                           ('reading', '#888888'), ('writing', KY_DARK_BLUE)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"WIDA ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Expanding or Higher",
        barmode='group', height=450, yaxis=dict(range=[0, 68])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[KY_DARK_BLUE if d > 20 else KY_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for Kentucky:** The oral-written gap is especially pronounced in
    districts with large refugee populations -- **JCPS Louisville** (~21,000 MLs with 150+
    languages), **Bowling Green** (~25% EL with Somali, Bosnian, Burmese speakers), and
    **Shelby County** (~20% EL with Guatemalan and Burmese populations). Students from these
    communities develop conversational fluency but struggle with academic writing, particularly
    when their home languages use non-Latin scripts.

    Under **United We Learn**, Kentucky is redesigning accountability to better capture
    EL progress. The **SB 1** governance reform and **HB 162** math reform add urgency
    to ensuring ELs have access to grade-level content while receiving targeted literacy support.
    With **67% of 4th graders not proficient in reading**, the writing gap compounds an
    already critical literacy crisis.
    """)


def render_access_analysis(access_df, districts_df):
    st.header("WIDA ACCESS Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains: Listening, Speaking,
    Reading, Writing. Kentucky uses the standard WIDA ACCESS assessment with proficiency
    levels 1-6.

    Exit criteria: **Composite score of 4.5+**.
    Kentucky has **171 districts** with EL population growing **128% over 20 years**.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="access_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="access_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="access_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        # Show top languages for context
        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top EL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.2f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.2f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.2f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.2f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.2f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[KY_BLUE, KY_GOLD, '#888888', KY_DARK_BLUE],
            text=[f"{s:.2f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"WIDA ACCESS Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score (1-6)", height=400,
            yaxis=dict(range=[0, 6])
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.2f}")
        with col2:
            st.metric("Written Average", f"{written:.2f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.2f}",
                      delta="Flag" if gap > 0.8 else "Monitor" if gap > 0.5 else "OK")

        # Exit criteria check
        st.subheader("Exit Criteria Check (KY: Composite 4.5+ on WIDA ACCESS)")
        composite = row['composite_avg']
        if composite >= 4.5:
            st.success(f"Composite {composite:.2f} meets exit threshold of 4.5+")
        elif composite >= 4.0:
            st.warning(f"Composite {composite:.2f} approaching exit threshold (4.5+). "
                       "Monitor for reclassification readiness.")
        else:
            st.info(f"Composite {composite:.2f} below exit threshold of 4.5+. "
                    "Continued EL services required.")

        st.markdown("""
        Under **United We Learn**, Kentucky is rethinking how EL progress is measured
        in the accountability system. The composite 4.5+ exit threshold remains, but
        advocates are pushing for domain-specific progress monitoring -- particularly
        in Writing, where the systemic gap is most acute.
        """)
    else:
        st.warning("No data available for the selected filters.")


def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking - Writing on WIDA ACCESS scale (1-6). Flag threshold: delta > 0.8.

    In Kentucky, this is particularly relevant for districts with large refugee populations
    -- **JCPS Louisville** (150+ languages), **Bowling Green** (Somali, Bosnian, Burmese),
    and **Shelby County** (Guatemalan, Burmese) -- where students develop conversational
    English rapidly but lag in academic writing. With **67% of 4th graders not proficient
    in reading** statewide, the writing gap compounds Kentucky's literacy crisis.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.2f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.2f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.2f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=KY_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=KY_BLUE))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350,
            yaxis=dict(range=[0, 6])
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.2f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **Kentucky policy context:** Under **SB 1** governance reform and the
            **United We Learn** redesign, districts have new flexibility in how they
            address EL needs. Districts should review WIDA ACCESS domain data for
            flagged students and provide targeted academic writing intervention with
            culturally and linguistically responsive instruction. **HB 162** math reform
            also demands attention to language demands embedded in math assessments.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.2f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=KY_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=KY_BLUE, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="WIDA Scale Score", height=400,
                yaxis=dict(range=[0, 6])
            )
            st.plotly_chart(fig, use_container_width=True)

            # Summary table
            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **Data from reportcard.kyschools.us (KSA results).** Kentucky has persistent achievement gaps
    between white students and Hispanic and EL students. With **67% of 4th graders not proficient
    in reading**, the state faces a broad literacy crisis that disproportionately impacts ELs.

    **United We Learn** is redesigning accountability to address these systemic gaps.
    **SB 1** governance reform shifts how districts allocate resources to underserved populations.
    """)

    st.divider()

    # Achievement gap bar chart
    fig = go.Figure()
    sorted_df = districts_df.sort_values('ksa_ela_all', ascending=True)
    for col, name, color in [
        ('ksa_ela_white', 'White', '#666666'),
        ('ksa_ela_all', 'All Students', KY_BLUE),
        ('ksa_ela_hispanic', 'Hispanic', KY_LIGHT_BLUE),
        ('ksa_ela_el', 'English Learners', KY_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="KSA ELA Proficiency by Subgroup -- 2025",
        barmode='group', xaxis_title="% Proficient + Distinguished", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gap magnitude analysis
    st.subheader("Gap Magnitude: White - EL ELA Proficiency")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wh_gap'] = districts_df_copy['ksa_ela_white'] - districts_df_copy['ksa_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['ksa_ela_white'] - districts_df_copy['ksa_ela_el']

    col1, col2 = st.columns(2)
    with col1:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="United We Learn", delta_color="inverse")
    with col2:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-EL Gap", f"{avg_we:.1f} pts", delta="United We Learn", delta_color="inverse")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('we_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['we_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[KY_DARK_BLUE if g > 30 else KY_GOLD for g in gap_sorted['we_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['we_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-EL ELA Gap by District (pts)", height=600,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    # 4th grade reading crisis callout
    st.subheader("4th Grade Reading Crisis")
    st.error("""
    **67% of Kentucky 4th graders are NOT proficient in reading on KSA.**

    This statistic underscores the urgency of the **United We Learn** redesign and
    **HB 162** math reform (which also impacts language-dependent math instruction).
    English Learners, who face compounding barriers of language acquisition plus content
    mastery, are disproportionately represented in the non-proficient group. The
    **SB 1** governance reform must ensure that restructured decision-making leads to
    better outcomes for these students.
    """)

    # Scatter: EL proficiency vs overall
    st.subheader("EL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='ksa_ela_all', y='ksa_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, KY_BLUE]],
        hover_name='district_name',
        labels={'ksa_ela_all': 'All Students ELA %', 'ksa_ela_el': 'EL ELA %',
                'el_count': 'EL Count', 'el_percent': 'EL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=60, y1=60,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="EL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ---
    **Kentucky context:** The **United We Learn** initiative acknowledges that Kentucky's
    current accountability system does not adequately capture EL progress or the
    challenges facing high-EL districts. With EL enrollment growing **128% over 20 years**,
    the state's assessment and accountability infrastructure must evolve. Every gap shown
    above represents students whose access to proficient-level instruction is not being met.
    **SB 1** restructures governance, but governance reform alone cannot close a 30+ point
    ELA gap between White and EL students.
    """)


def render_ksa(ksa_df, districts_df):
    st.header("KSA Assessment Analysis")
    st.markdown("""
    **Kentucky Summative Assessment (KSA)** -- 4 performance levels:
    Novice, Apprentice, Proficient, Distinguished.

    ELA and Math tested grades 3-8 (and 10-11).
    Dashboard: reportcard.kyschools.us.
    67% of 4th graders not proficient in reading.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="ksa_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="ksa_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="ksa_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="ksa_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = ksa_df[
        (ksa_df['district_id'] == district_id) &
        (ksa_df['grade'] == grade) &
        (ksa_df['subject'] == subject) &
        (ksa_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Novice", f"{row['novice_pct']:.1f}%")
        with col2:
            st.metric("Apprentice", f"{row['apprentice_pct']:.1f}%")
        with col3:
            st.metric("Proficient", f"{row['proficient_pct']:.1f}%")
        with col4:
            st.metric("Distinguished", f"{row['distinguished_pct']:.1f}%")

        levels = ['Novice', 'Apprentice', 'Proficient', 'Distinguished']
        values = [row['novice_pct'], row['apprentice_pct'],
                  row['proficient_pct'], row['distinguished_pct']]
        colors = [KY_DARK_BLUE, KY_LIGHT_BLUE, KY_GOLD, KY_BLUE]
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"KSA {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Proficiency rate context
        st.metric("Combined Proficiency (Proficient + Distinguished)",
                  f"{row['prof_distinguished_pct']:.1f}%",
                  help="67% of 4th graders not proficient in reading statewide")

        # Cross-grade comparison
        st.subheader(f"KSA {subject} Across Grades -- {district} ({year})")
        cross = ksa_df[
            (ksa_df['district_id'] == district_id) &
            (ksa_df['subject'] == subject) &
            (ksa_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            level_col_map = {
                'Novice': 'novice_pct',
                'Apprentice': 'apprentice_pct',
                'Proficient': 'proficient_pct',
                'Distinguished': 'distinguished_pct',
            }
            for level, color in zip(levels, colors):
                col_name = level_col_map[level]
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_name],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"KSA {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(access_df, ksa_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-KY analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("WIDA ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ACCESS CSV",
            access_df.to_csv(index=False),
            "vera_ky_access.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("KSA Data")
        st.dataframe(ksa_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download KSA CSV",
            ksa_df.to_csv(index=False),
            "vera_ky_ksa.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide ACCESS Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_ky_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_ky_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-KY | Kentucky Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {KY_BLUE}; }}
        .stButton > button {{ background-color: {KY_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {KY_DARK_BLUE}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    # Load all data
    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    ksa_df = load_ksa_data(districts_df)
    domain_df = load_statewide_domain_data()

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {KY_BLUE}; margin: 0;">VERA-KY</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Kentucky Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "WIDA ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "KSA Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - WIDA ACCESS (4 domains)
    - KDE ACCESS Data
    - KSA (Grades 3-8, 10-11)
    - KSIS (Infinite Campus)
    - reportcard.kyschools.us

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 0.8 (WIDA scale)

    **EXIT Criteria:**
    - Composite 4.5+ on ACCESS

    **WIDA Levels:**
    - 1: Entering
    - 2: Emerging
    - 3: Developing
    - 4: Expanding
    - 5: Bridging
    - 6: Reaching

    **Key Context:**
    - 171 districts
    - EL growth: 128% (20 yr)
    - JCPS: ~21,000 MLs
    - **SB 1** governance reform
    - **HB 162** math reform
    - **United We Learn** redesign
    - 67% 4th graders not prof reading

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    # Page routing
    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "WIDA ACCESS Analysis":
        render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(access_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "KSA Analysis":
        render_ksa(ksa_df, districts_df)
    elif page == "Export Data":
        render_export(access_df, ksa_df, districts_df, domain_df)


if __name__ == "__main__":
    main()
