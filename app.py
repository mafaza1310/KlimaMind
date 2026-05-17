"""KlimaMind Dashboard v3 — Kararlı & Tam"""
import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os, warnings
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "data")

# ── RENKLER ──────────────────────────────────────────────────────────
RED   = "#8B0000"
TEAL  = "#1A7A6E"
DGRAY = "#2C3E50"
MGRAY = "#95A5A6"
WHITE = "#FFFFFF"
LGRAY = "#F0F2F5"
BLUE  = "#2980B9"
ORANGE= "#E67E22"
PURPLE= "#8E44AD"

# ── VERİ YÜKLE ───────────────────────────────────────────────────────
df_suicide = pd.read_csv(os.path.join(DATA_DIR, "suicide_panel.csv"))
df_suicide["suicide_rate"]  = pd.to_numeric(df_suicide["suicide_rate"], errors="coerce")
df_suicide["suicide_count"] = pd.to_numeric(df_suicide["suicide_count"], errors="coerce")
df_suicide["year"] = df_suicide["year"].astype(int)
df_suicide["province"] = df_suicide["province"].astype(str).str.strip()

df_csri = pd.read_csv(os.path.join(DATA_DIR, "province_csri.csv"))
df_csri["province"] = df_csri["province"].astype(str).str.strip()

# ERA5 ayrı yükle (merge YOK)
ERA5_OK = False
df_era5 = pd.DataFrame()
clim_path = os.path.join(DATA_DIR, "climate_panel.csv")
if os.path.exists(clim_path):
    df_era5 = pd.read_csv(clim_path)
    df_era5["avg_temp"] = pd.to_numeric(df_era5["avg_temp"], errors="coerce")
    df_era5["province"] = df_era5["province"].astype(str).str.strip()
    df_era5["year"] = df_era5["year"].astype(int)
    ERA5_OK = df_era5["avg_temp"].notna().sum() > 0

PROVINCES = sorted(df_suicide["province"].unique().tolist())
YEARS     = sorted(df_suicide["year"].unique().tolist())
Y_MIN, Y_MAX = YEARS[0], YEARS[-1]
DEFAULT   = "Antalya" if "Antalya" in PROVINCES else PROVINCES[0]
TOTAL     = int(df_suicide["suicide_count"].sum())
N_SIG     = int(df_csri["significant"].sum())

print(f"✅ {TOTAL:,} intihar | {len(PROVINCES)} il | ERA5: {ERA5_OK}")
print(f"   İller örnek: {PROVINCES[:5]}")

COORDS = {
    "Adana":(37.00,35.32),"Adıyaman":(37.76,38.27),"Afyonkarahisar":(38.75,30.54),
    "Ağrı":(39.72,43.05),"Amasya":(40.65,35.83),"Ankara":(39.92,32.85),
    "Antalya":(36.90,30.69),"Artvin":(41.18,41.82),"Aydın":(37.85,27.84),
    "Balıkesir":(39.65,27.88),"Bilecik":(40.14,29.98),"Bingöl":(38.88,40.50),
    "Bitlis":(38.40,42.11),"Bolu":(40.73,31.61),"Burdur":(37.72,30.29),
    "Bursa":(40.18,29.06),"Çanakkale":(40.15,26.41),"Çankırı":(40.60,33.61),
    "Çorum":(40.55,34.95),"Denizli":(37.77,29.09),"Diyarbakır":(37.91,40.23),
    "Edirne":(41.68,26.56),"Elazığ":(38.67,39.22),"Erzincan":(39.75,39.50),
    "Erzurum":(39.90,41.27),"Eskişehir":(39.78,30.52),"Gaziantep":(37.06,37.38),
    "Giresun":(40.91,38.39),"Gümüşhane":(40.46,39.48),"Hakkari":(37.57,43.74),
    "Hatay":(36.40,36.34),"Isparta":(37.76,30.55),"Mersin":(36.80,34.63),
    "İstanbul":(41.01,28.95),"İzmir":(38.42,27.14),"Kars":(40.61,43.09),
    "Kastamonu":(41.38,33.78),"Kayseri":(38.73,35.48),"Kırklareli":(41.73,27.22),
    "Kırşehir":(39.15,34.17),"Kocaeli":(40.85,29.88),"Konya":(37.87,32.49),
    "Kütahya":(39.42,29.98),"Malatya":(38.35,38.31),"Manisa":(38.62,27.43),
    "Kahramanmaraş":(37.57,36.92),"Mardin":(37.31,40.73),"Muğla":(37.21,28.36),
    "Muş":(38.73,41.49),"Nevşehir":(38.62,34.72),"Niğde":(37.97,34.68),
    "Ordu":(40.98,37.88),"Rize":(41.02,40.52),"Sakarya":(40.77,30.39),
    "Samsun":(41.29,36.33),"Siirt":(37.93,41.95),"Sinop":(42.02,35.15),
    "Sivas":(39.75,37.02),"Tekirdağ":(41.45,27.51),"Tokat":(40.31,36.55),
    "Trabzon":(41.00,39.72),"Tunceli":(39.10,39.55),"Şanlıurfa":(37.16,38.79),
    "Uşak":(38.67,29.41),"Van":(38.49,43.38),"Yozgat":(39.82,34.81),
    "Zonguldak":(41.45,31.80),"Aksaray":(38.37,34.04),"Bayburt":(40.26,40.23),
    "Karaman":(37.18,33.22),"Kırıkkale":(39.85,33.51),"Batman":(37.88,41.13),
    "Şırnak":(37.52,42.46),"Bartın":(41.63,32.34),"Ardahan":(41.11,42.70),
    "Iğdır":(39.92,44.04),"Yalova":(40.65,29.27),"Karabük":(41.20,32.63),
    "Kilis":(36.72,37.12),"Osmaniye":(37.07,36.25),"Düzce":(40.84,31.16)
}

# ── APP ──────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="KlimaMind")

app.layout = html.Div(style={"fontFamily":"'Segoe UI',Arial,sans-serif","backgroundColor":LGRAY,"minHeight":"100vh"}, children=[

    # HEADER
    html.Div(style={"background":f"linear-gradient(135deg, {RED} 0%, #5C0000 100%)",
                    "padding":"14px 28px","display":"flex","justifyContent":"space-between","alignItems":"center",
                    "boxShadow":"0 2px 8px rgba(0,0,0,0.3)"}, children=[
        html.Div([
            html.Span("🧠 KlimaMind", style={"color":WHITE,"fontSize":"24px","fontWeight":"bold","letterSpacing":"1px"}),
            html.Span("  İklim × İntihar Mortalitesi  |  Türkiye 2009–2023",
                      style={"color":"rgba(255,255,255,0.75)","fontSize":"13px","marginLeft":"12px"}),
        ]),
        html.Div([
            html.Span("TÜİK", style={"backgroundColor":"rgba(255,255,255,0.2)","color":WHITE,
                "padding":"3px 8px","borderRadius":"10px","fontSize":"11px","marginRight":"6px"}),
            html.Span("EM-DAT", style={"backgroundColor":"rgba(255,255,255,0.2)","color":WHITE,
                "padding":"3px 8px","borderRadius":"10px","fontSize":"11px","marginRight":"6px"}),
            html.Span("ERA5" if ERA5_OK else "ERA5 ⚠",
                      style={"backgroundColor":"rgba(26,122,110,0.6)" if ERA5_OK else "rgba(255,100,0,0.4)",
                             "color":WHITE,"padding":"3px 8px","borderRadius":"10px","fontSize":"11px"}),
        ])
    ]),

    # KPI BAR
    html.Div(style={"backgroundColor":WHITE,"padding":"10px 28px","display":"flex","gap":"0",
                    "borderBottom":f"3px solid {TEAL}","boxShadow":"0 1px 4px rgba(0,0,0,0.06)"}, children=[
        html.Div(style={"flex":1,"textAlign":"center","borderRight":f"1px solid {LGRAY}"}, children=[
            html.Div(f"{TOTAL:,}", style={"fontSize":"22px","fontWeight":"bold","color":RED}),
            html.Div("Toplam İntihar (2009–2023)", style={"fontSize":"11px","color":MGRAY}),
        ]),
        html.Div(style={"flex":1,"textAlign":"center","borderRight":f"1px solid {LGRAY}"}, children=[
            html.Div(str(len(PROVINCES)), style={"fontSize":"22px","fontWeight":"bold","color":TEAL}),
            html.Div("Türkiye İli", style={"fontSize":"11px","color":MGRAY}),
        ]),
        html.Div(style={"flex":1,"textAlign":"center","borderRight":f"1px solid {LGRAY}"}, children=[
            html.Div(f"{N_SIG}/81", style={"fontSize":"22px","fontWeight":"bold","color":BLUE}),
            html.Div("Anlamlı Korelasyon (p<0.05)", style={"fontSize":"11px","color":MGRAY}),
        ]),
        html.Div(style={"flex":1,"textAlign":"center"}, children=[
            html.Div(f"{df_suicide['suicide_count'].mean():.0f}", style={"fontSize":"22px","fontWeight":"bold","color":ORANGE}),
            html.Div("Ort. İl Yıllık İntihar", style={"fontSize":"11px","color":MGRAY}),
        ]),
    ]),

    # MAIN
    html.Div(style={"display":"grid","gridTemplateColumns":"270px 1fr","gap":"12px","padding":"12px 16px"}, children=[

        # SOL PANEL
        html.Div(style={"display":"flex","flexDirection":"column","gap":"10px"}, children=[

            # Filtreler
            html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"16px",
                            "boxShadow":"0 2px 8px rgba(0,0,0,0.07)"}, children=[
                html.H3("⚙️ Filtreler", style={"margin":"0 0 14px","color":DGRAY,"fontSize":"14px","fontWeight":"bold"}),

                html.Label("📍 İl Seç", style={"fontSize":"11px","fontWeight":"bold","color":MGRAY,"letterSpacing":"1px"}),
                dcc.Dropdown(id="dd-prov",
                    options=[{"label":p,"value":p} for p in PROVINCES],
                    value=DEFAULT, clearable=False,
                    style={"fontSize":"12px","marginTop":"4px","marginBottom":"12px"}),

                html.Label("📅 Yıl Aralığı", style={"fontSize":"11px","fontWeight":"bold","color":MGRAY,"letterSpacing":"1px"}),
                dcc.RangeSlider(id="sl-yr", min=Y_MIN, max=Y_MAX, step=1,
                    value=[Y_MIN, Y_MAX],
                    marks={y:{"label":str(y),"style":{"fontSize":"10px"}} for y in YEARS if y%3==0},
                    tooltip={"placement":"bottom","always_visible":False}),

                html.Div(style={"marginTop":"14px"}),
                html.Label("🗺️ Harita Metriği", style={"fontSize":"11px","fontWeight":"bold","color":MGRAY,"letterSpacing":"1px"}),
                dcc.RadioItems(id="rd-metric",
                    options=[{"label":"  CSRI Risk Skoru","value":"csri"},
                             {"label":"  İntihar Oranı /100k","value":"rate"}],
                    value="csri",
                    labelStyle={"display":"block","marginTop":"7px","fontSize":"12px","color":DGRAY}),
            ]),

            # Top 10
            html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"14px",
                            "boxShadow":"0 2px 8px rgba(0,0,0,0.07)","flex":1}, children=[
                html.H3("🏆 En Riskli 10 İl", style={"margin":"0 0 10px","color":DGRAY,"fontSize":"14px","fontWeight":"bold"}),
                html.Div(id="top10"),
            ]),
        ]),

        # SAĞ PANEL
        html.Div(style={"display":"flex","flexDirection":"column","gap":"10px"}, children=[

            # Satır 1: Harita + Ulusal Trend
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"10px"}, children=[
                html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"12px",
                                "boxShadow":"0 2px 8px rgba(0,0,0,0.07)"}, children=[
                    html.H3("🗺️ Türkiye Risk Haritası", style={"margin":"0 0 6px","color":DGRAY,"fontSize":"13px"}),
                    html.P("İle tıkla → sol dropdown güncellenir", style={"margin":"0 0 4px","color":MGRAY,"fontSize":"10px"}),
                    dcc.Graph(id="fig-map", style={"height":"310px"}, config={"displayModeBar":False}),
                ]),
                html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"12px",
                                "boxShadow":"0 2px 8px rgba(0,0,0,0.07)"}, children=[
                    html.H3("📈 Türkiye Yıllık İntihar Trendi", style={"margin":"0 0 6px","color":DGRAY,"fontSize":"13px"}),
                    dcc.Graph(id="fig-nat", style={"height":"310px"}, config={"displayModeBar":False}),
                ]),
            ]),

            # Satır 2: İl Detay + CSRI Bar
            html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"10px"}, children=[
                html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"12px",
                                "boxShadow":"0 2px 8px rgba(0,0,0,0.07)"}, children=[
                    html.H3(id="det-title", style={"margin":"0 0 6px","color":DGRAY,"fontSize":"13px"}),
                    dcc.Graph(id="fig-det", style={"height":"270px"}, config={"displayModeBar":False}),
                ]),
                html.Div(style={"backgroundColor":WHITE,"borderRadius":"12px","padding":"12px",
                                "boxShadow":"0 2px 8px rgba(0,0,0,0.07)"}, children=[
                    html.H3("📊 CSRI Sıralaması — Top 20", style={"margin":"0 0 6px","color":DGRAY,"fontSize":"13px"}),
                    dcc.Graph(id="fig-csri", style={"height":"270px"}, config={"displayModeBar":False}),
                ]),
            ]),
        ]),
    ]),

    html.Div(style={"backgroundColor":DGRAY,"padding":"8px","textAlign":"center","marginTop":"4px"}, children=[
        html.P("KlimaMind © 2025  |  MAFAZA Mohamed Bahialdein  |  Gümüşhane Üniversitesi  |  Kaynak: TÜİK + EM-DAT + ERA5 Copernicus  |  Tüm veriler açık erişim",
               style={"color":"rgba(255,255,255,0.6)","margin":0,"fontSize":"10px"})
    ]),
])

# ── CALLBACKS ────────────────────────────────────────────────────────

# Haritaya tıklayınca dropdown güncelle
@app.callback(Output("dd-prov","value"), Input("fig-map","clickData"), prevent_initial_call=True)
def map_click(click):
    if click and "points" in click:
        return click["points"][0]["text"]
    return dash.no_update

# Harita
@app.callback(Output("fig-map","figure"), Input("rd-metric","value"), Input("sl-yr","value"))
def cb_map(metric, yr):
    y0, y1 = int(yr[0]), int(yr[1])
    if metric == "csri":
        vals = dict(zip(df_csri["province"], df_csri["csri"]))
        cs = [[0,"#FFE0E0"],[0.4,"#CC2222"],[1,"#4B0000"]]
        bt = "CSRI"
    else:
        avg = df_suicide[(df_suicide.year>=y0)&(df_suicide.year<=y1)].groupby("province")["suicide_rate"].mean()
        vals = avg.to_dict()
        cs = [[0,"#FEF9E7"],[0.5,"#E67E22"],[1,"#922B21"]]
        bt = "/100k"

    lats,lons,texts,colors,szs = [],[],[],[],[]
    for p,(lat,lon) in COORDS.items():
        lats.append(lat); lons.append(lon); texts.append(p)
        v = float(vals.get(p, 0))
        colors.append(v if v==v else 0)
        szs.append(max(9, min(18, v*1.5+8)) if metric=="rate" else 12)

    fig = go.Figure(go.Scattermapbox(
        lat=lats, lon=lons, mode="markers", text=texts,
        marker=dict(size=szs, color=colors, colorscale=cs, showscale=True,
                    colorbar=dict(title=dict(text=bt,side="right"),thickness=12,len=0.65,
                                  tickfont=dict(size=10)),opacity=0.88),
        hovertemplate="<b>%{text}</b><br>"+bt+": %{marker.color:.2f}<extra></extra>"
    ))
    fig.update_layout(mapbox=dict(style="carto-positron",center=dict(lat=39.0,lon=35.0),zoom=4.3),
        margin=dict(l=0,r=0,t=0,b=0),height=310,paper_bgcolor=WHITE)
    return fig

# Ulusal trend
@app.callback(Output("fig-nat","figure"), Input("sl-yr","value"))
def cb_nat(yr):
    y0, y1 = int(yr[0]), int(yr[1])
    sub = df_suicide[(df_suicide.year>=y0)&(df_suicide.year<=y1)]
    nat = sub.groupby("year")["suicide_count"].sum().reset_index()
    nat.columns = ["year","total"]
    nat = nat[nat.total > 0]

    years = nat["year"].tolist()
    totals = nat["total"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=totals, name="İntihar Sayısı",
        marker_color=RED, opacity=0.82,
        hovertemplate="%{x}: <b>%{y:,}</b> vaka<extra></extra>"))

    if len(years) > 2:
        z = np.polyfit(years, totals, 1)
        trend_y = [round(np.poly1d(z)(y)) for y in years]
        fig.add_trace(go.Scatter(x=years, y=trend_y,
            name=f"Trend ({'+' if z[0]>0 else ''}{z[0]:.0f}/yıl)",
            line=dict(color=PURPLE, width=2, dash="dot"), mode="lines"))

    fig.update_layout(height=310, margin=dict(l=50,r=15,t=10,b=35),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(title=None, gridcolor="#EEE", tickmode="linear", dtick=2,
                   tickfont=dict(size=10)),
        yaxis=dict(title="Vaka Sayısı", gridcolor="#EEE", tickfont=dict(size=10)),
        legend=dict(orientation="h",y=1.05,x=0,font=dict(size=10)),
        hovermode="x unified", bargap=0.25)
    return fig

# İl detayı — ana callback
@app.callback(
    Output("det-title","children"),
    Output("fig-det","figure"),
    Input("dd-prov","value"),
    Input("sl-yr","value")
)
def cb_det(prov, yr):
    print(f"[DET CALLED] prov={prov!r}, yr={yr}")

    # Güvenli varsayılan
    if not prov or prov not in PROVINCES:
        prov = DEFAULT

    y0, y1 = int(yr[0]), int(yr[1])

    # İl verisi
    mask = (df_suicide["province"] == prov) & (df_suicide["year"] >= y0) & (df_suicide["year"] <= y1)
    sub = df_suicide[mask].copy().sort_values("year")
    sub["suicide_rate"] = pd.to_numeric(sub["suicide_rate"], errors="coerce")
    sub = sub.dropna(subset=["suicide_rate"])

    print(f"[DET] {prov}: {len(sub)} satır, min_rate={sub['suicide_rate'].min():.2f}, max_rate={sub['suicide_rate'].max():.2f}")

    # Ulusal ortalama
    nat_mask = (df_suicide["year"] >= y0) & (df_suicide["year"] <= y1)
    nat = df_suicide[nat_mask].groupby("year")["suicide_rate"].mean().reset_index()

    # İki eksenli grafik: intihar oranı (sol) + sıcaklık (sağ, ERA5)
    fig = go.Figure()

    # 1. Türkiye ortalaması
    fig.add_trace(go.Scatter(
        x=nat["year"].tolist(), y=nat["suicide_rate"].round(2).tolist(),
        name="TR Ort.", mode="lines",
        line=dict(color="#BDC3C7", width=1.5, dash="dash"),
        hovertemplate="%{x}: %{y:.2f} TR ort.<extra></extra>"
    ))

    # 2. İl intihar oranı
    fig.add_trace(go.Scatter(
        x=sub["year"].tolist(), y=sub["suicide_rate"].round(2).tolist(),
        name=prov, mode="lines+markers",
        line=dict(color=RED, width=2.5),
        marker=dict(size=8, color=RED, line=dict(color=WHITE, width=1.5)),
        hovertemplate="%{x}: <b>%{y:.2f}</b>/100k<extra></extra>"
    ))

    # CSRI badge
    csri_row = df_csri[df_csri["province"] == prov]
    title_suffix = ""
    if not csri_row.empty:
        cv = float(csri_row["csri"].iloc[0])
        sig = bool(csri_row["significant"].iloc[0])
        title_suffix = f"  |  CSRI: {cv:.0f}{' ✓ p<0.05' if sig else ''}"

    fig.update_layout(
        height=270, margin=dict(l=50,r=55,t=10,b=35),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(gridcolor="#F0F0F0", dtick=2, tickfont=dict(size=10),
                   range=[y0-0.3, y1+0.3]),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10)),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Oran /100k", gridcolor="#F0F0F0", tickfont=dict(size=10))

    return f"📍 {prov} — İntihar Oranı Trendi{title_suffix}", fig

# CSRI bar
@app.callback(Output("fig-csri","figure"), Input("sl-yr","value"))
def cb_csri(_):
    top = df_csri.nlargest(20, "csri").copy()
    colors = [RED if bool(s) else "#BDC3C7" for s in top["significant"]]
    fig = go.Figure(go.Bar(
        x=top["csri"].tolist(), y=top["province"].tolist(),
        orientation="h", marker_color=colors, opacity=0.85,
        hovertemplate="<b>%{y}</b><br>CSRI: %{x:.1f}<extra></extra>"
    ))
    fig.update_layout(height=270, margin=dict(l=10,r=20,t=5,b=30),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        xaxis=dict(title="CSRI Skoru (kırmızı = p<0.05 anlamlı)", gridcolor="#EEE", tickfont=dict(size=10)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)))
    return fig

# Top 10 tablo
@app.callback(Output("top10","children"), Input("sl-yr","value"))
def cb_top10(_):
    rows = []
    for i, (_, r) in enumerate(df_csri.head(10).iterrows()):
        bg = "#FFF8F8" if i%2==0 else WHITE
        sig_el = (html.Span("✓", style={"backgroundColor":"#D5F5E3","color":"#1E8449",
                  "padding":"1px 5px","borderRadius":"4px","fontSize":"9px","fontWeight":"bold"})
                  if bool(r.get("significant")) else
                  html.Span("–", style={"color":"#CCC","fontSize":"11px"}))
        # Satıra tıklayınca dropdown güncelle
        rows.append(html.Tr(
            style={"backgroundColor":bg,"cursor":"pointer"},
            children=[
                html.Td(str(i+1), style={"padding":"5px 6px","fontWeight":"bold","color":RED,"fontSize":"11px","width":"22px"}),
                html.Td(r["province"], style={"padding":"5px 4px","fontSize":"11px","fontWeight":"600"}),
                html.Td(f"{r['csri']:.0f}", style={"padding":"5px 4px","fontSize":"11px","textAlign":"center","width":"36px"}),
                html.Td(f"{r.get('avg_suicide_rate',0):.2f}", style={"padding":"5px 4px","fontSize":"10px","textAlign":"center","color":MGRAY,"width":"48px"}),
                html.Td(sig_el, style={"padding":"5px 4px","textAlign":"center","width":"24px"}),
            ]
        ))
    return html.Table(style={"width":"100%","borderCollapse":"collapse"}, children=[
        html.Thead(html.Tr([
            html.Th("#",    style={"padding":"5px 6px","backgroundColor":RED,"color":WHITE,"fontSize":"9px","width":"22px"}),
            html.Th("İl",   style={"padding":"5px 4px","backgroundColor":RED,"color":WHITE,"fontSize":"9px"}),
            html.Th("CSRI", style={"padding":"5px 4px","backgroundColor":RED,"color":WHITE,"fontSize":"9px","textAlign":"center"}),
            html.Th("/100k",style={"padding":"5px 4px","backgroundColor":RED,"color":WHITE,"fontSize":"9px","textAlign":"center"}),
            html.Th("p",    style={"padding":"5px 4px","backgroundColor":RED,"color":WHITE,"fontSize":"9px","textAlign":"center"}),
        ])),
        html.Tbody(rows)
    ])

if __name__ == "__main__":
    print(f"\n{'='*45}")
    print(f"  KlimaMind v3  →  http://127.0.0.1:8050")
    print(f"{'='*45}\n")
    app.run(debug=False, port=8050)
