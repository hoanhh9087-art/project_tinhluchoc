import streamlit as st
from google import genai
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AI 靜力學形心終極求解器", layout="wide")

st.title("🏛️ AI 輔助靜力學形心終極求解系統 (完整第九章支援)")
st.write("本系統已全面升級，支援第九章「質心與形心」所有複合幾何、曲線定積分及複雜工程應用題型。")

# --- Thanh điều khiển bên trái ---
st.sidebar.header("⚙️ 系統參數與模式設定")
api_key = st.sidebar.text_input("請輸入 Google Gemini API Key:", type="password")

# Cho người dùng chọn 3 chế độ vạn năng
mode = st.sidebar.radio(
    "選擇章節分析模式:", 
    [
        "1. 複合面積模式 (Composite Areas)", 
        "2. 高階曲線積分模式 (Integration Mode)",
        "3. 任意題目自由輸入模式 (Free Text Input)"
    ]
)

prompt = ""
fig, ax = plt.subplots(figsize=(5, 5))

# --- CHẾ ĐỘ 1: HÌNH HỌC PHỨC HỢP ---
if mode == "1. 複合面積模式 (Composite Areas)":
    st.sidebar.subheader("📐 幾何參數設定")
    shape_type = st.sidebar.selectbox("圖形種類:", ["矩形 (Rectangle)", "三角形 (Triangle)"])
    w = st.sidebar.number_input("寬度 / 底邊 (b):", value=10.0)
    h = st.sidebar.number_input("高度 (h):", value=5.0)
    x_base = st.sidebar.number_input("基準點 X 坐標:", value=0.0)
    y_base = st.sidebar.number_input("基準點 Y 坐標:", value=0.0)
    is_hole = st.sidebar.checkbox("這是一個挖空區域 (Hole)?")

    # Vẽ hình học cơ bản
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    if shape_type == "矩形 (Rectangle)":
        color = 'red' if is_hole else 'dodgerblue'
        hatch = '///' if is_hole else None
        rect = plt.Rectangle((x_base, y_base), w, h, fill=True, facecolor=color, alpha=0.6, hatch=hatch, edgecolor='black')
        ax.add_patch(rect)
        cx, cy = x_base + w/2, y_base + h/2
    else:
        color = 'red' if is_hole else 'dodgerblue'
        hatch = '///' if is_hole else None
        pts = np.array([[x_base, y_base], [x_base + w, y_base], [x_base, y_base + h]])
        tri = plt.Polygon(pts, fill=True, facecolor=color, alpha=0.6, hatch=hatch, edgecolor='black')
        ax.add_patch(tri)
        cx, cy = x_base + w/3, y_base + h/3
        
    ax.plot(cx, cy, 'ro', label=f"Centroid")
    ax.set_xlim(min(0, x_base) - 2, max(10, x_base + w) + 2)
    ax.set_ylim(min(0, y_base) - 2, max(10, y_base + h) + 2)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()

    prompt = f"""你現在是國立勤益科技大學智慧自動化工程系的靜力學助教。
請協助求解以下「複合面積形心」的題目，並嚴格以繁體中文、步驟清晰、表格化呈現計算過程。
【題目已知條件】：
- 圖形幾何種類: {shape_type}
- 尺寸參數: 寬/底={w}, 高度={h}
- 基準點坐標位置: ({x_base}, {y_base})
- 區域屬性: {"此區域為挖空孔洞 (面積算負值)" if is_hole else "此區域為實體結構 (面積算正值)"}
【必須包含的輸出內容】：
1. 說明形心公式的核心原理：\\bar{{X}} = \\frac{{\\sum A_i x_i}}{{\\sum A_i}} 與 \\bar{{Y}} = \\frac{{\\sum A_i y_i}}{{\\sum A_i}}。
2. 建立 Markdown 計算表格，欄位包含：項目、面積 A_i、單一形心 x_i、單一形心 y_i、乘積 A_i x_i、乘積 A_i y_i。
3. 導出最終的整體幾何結構確切形心坐標解答 (\\bar{{X}}, \\bar{{Y}})。"""

# --- CHẾ ĐỘ 2: TÍCH PHÂN ĐƯỜNG CONG NÂNG CAO ---
elif mode == "2. 高階曲線積分模式 (Integration Mode)":
    st.sidebar.subheader("📉 曲線積分參數設定")
    equation = st.sidebar.selectbox("選擇曲線方程類型:", ["y = x^2 (拋物線)", "y^2 = x (拋物線)", "y = x^3 (三次曲線)", "y = sin(x) (正弦曲線)"])
    x_max = st.sidebar.number_input("X 軸積分上限 (m):", value=1.0)
    y_max = st.sidebar.number_input("Y 軸幾何上限 (m):", value=1.0)
    strip_type = st.sidebar.radio("選擇微分條類型:", ["垂直微分條 (Vertical Strip / dx)", "水平微分條 (Horizontal Strip / dy)"])

    # Vẽ đồ thị đường cong
    x = np.linspace(0, x_max, 200)
    if equation == "y = x^2 (拋物線)":
        y = x**2
        eq_text = "y = x^2"
    elif equation == "y^2 = x (拋物線)":
        y = np.sqrt(x)
        eq_text = "y = \\sqrt{{x}}"
    elif equation == "y = x^3 (三次曲線)":
        y = x**3
        eq_text = "y = x^3"
    else:
        y = np.sin(x)
        eq_text = "y = sin(x)"

    ax.plot(x, y, color='blue', linewidth=2, label=f"Curve: {eq_text}")
    ax.fill_between(x, y, color='dodgerblue', alpha=0.4, label="Area (A)")
    
    if strip_type == "垂直微分條 (Vertical Strip / dx)":
        ax.axvspan(x_max*0.5, x_max*0.55, color='orange', alpha=0.7, label="Element dA (dx)")
    else:
        ax.axhspan(y_max*0.5, y_max*0.55, color='orange', alpha=0.7, label="Element dA (dy)")

    ax.set_xlim(-0.2, x_max + 0.5)
    ax.set_ylim(-0.2, y_max + 0.5)
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()

    prompt = f"""你現在是國立勤益科技大學智慧自動化工程系的靜力學助教。
請協助利用「微元法與定積分（Integration）」求解以下靜力學形心題目。請嚴格以繁體中文、公式推導步驟清晰呈現。
【題目已知條件】：
- 邊界曲線方程: {equation}
- 積分範圍邊界: X 從 0 到 {x_max}m，Y 上限為 {y_max}m。
- 採用的分析微元: {strip_type}
【必須包含的輸出內容】：
1. 寫出形心的定積分定義公式：\\bar{{X}} = \\frac{{\\int \\tilde{{x}} dA}}{{\\int dA}} 與 \\bar{{Y}} = \\frac{{\\int \\tilde{{y}} dA}}{{\\int dA}}。
2. 詳細說明並推導出該微元條的：(a) 微分面積 dA 表達式；(b) 微元形心坐標 (\\tilde{{x}}, \\tilde{{y}}) 的表達式。
3. 進行定積分的代數代入與積分運算過程（秀出積分原函數與上下限代入）。
4. 精確導出最終答案 (\\bar{{X}}, \\bar{{Y}})。"""

# --- CHẾ ĐỘ 3: TỰ DO NHẬP ĐỀ BÀI (VẠN NĂNG) ---
else:
    st.sidebar.subheader("📝 任意題目文本輸入")
    custom_question = st.sidebar.text_area(
        "請直接複製或輸入課本題目敘述 (支援任何複雜題型):",
        value="一個由半圓形（半徑 R=3m）與矩形（寬 6m, 高 4m）組成的複合面積，其中矩形中心被挖空了一個直徑 2m 的圓形孔洞，求整體結構的幾何形心坐標。"
    )
    
    # Hiển thị ảnh minh họa sơ đồ tư duy AI cho chế độ tự do
    ax.text(0.5, 0.5, "AI Solver Mode\nReady to analyze\nany Chapter 9 problem", 
            fontsize=12, ha='center', va='center', weight='bold', color='purple')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    prompt = f"""你現在是國立勤益科技大學智慧自動化工程系的靜力學助教。
請協助求解以下進階或任意型態的靜力學第九章（質心與形心）題目。
請嚴格以繁體中文進行步驟化、邏輯清晰的解題推導。如果有複合圖形，請盡量用 Markdown 表格輔助呈現計算。

【使用者輸入的題目內容】：
{custom_question}

【輸出規範】：
1. 分析題意，列出解題所需的基礎靜力學公式與幾何原理。
2. 詳列每一步計算過程（包含面積、分部形心、乘積項等）。
3. 給出最終的形心坐標確切答案，並加上簡短的工程物理意義總結。"""


# --- Hiển thị giao diện chính ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 幾何圖形與分析視覺化")
    st.pyplot(fig)

with col2:
    st.subheader("🤖 Gemini AI 智慧求解核心")
    if st.button("🚀 啟動 AI 求解系統"):
        if not api_key:
            st.error("請先在左側輸入您的 Google Gemini API Key!")
        else:
            with st.spinner("AI 正在進行靜力學深度邏輯推理中...請稍候..."):
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"系統發送請求失敗，錯誤訊息: {e}")
