import streamlit as st
from google import genai
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Thiết lập giao diện Web theo chuẩn các trường đại học Đài Loan
st.set_page_config(page_title="AI 輔助靜力學形心求解器", layout="wide")
st.title("🤖 AI 輔助靜力學求解系統 - Ch.9 複合面積形心")
st.markdown("### 國立勤益科技大學 智慧自動化工程系 - 靜力學期末加分專題")

# Thanh điều hướng bên trái (Sidebar)
st.sidebar.header("🔑 系統憑證設定")
api_key = st.sidebar.text_input("請輸入 Google Gemini API Key:", type="password")

st.sidebar.header("📋 1. 輸入複合圖形資料")
shape_type = st.sidebar.selectbox("選擇子圖形種類:", ["矩形 (Rectangle)", "三角形 (Triangle)"])

# Khởi tạo các biến tọa độ mặc định để tránh lỗi logic
w, h, x_base, y_base, cx, cy = 10.0, 5.0, 0.0, 0.0, 5.0, 2.5
is_hole = False

if shape_type == "矩形 (Rectangle)":
    w = st.sidebar.number_input("寬度 (width, b):", value=10.0, step=1.0)
    h = st.sidebar.number_input("高度 (height, h):", value=5.0, step=1.0)
    x_base = st.sidebar.number_input("左下角 X 座標:", value=0.0, step=1.0)
    y_base = st.sidebar.number_input("左下角 Y 座標:", value=0.0, step=1.0)
    is_hole = st.sidebar.checkbox("這是一個挖空區域 (Hole)?")
    cx = x_base + w / 2
    cy = y_base + h / 2

elif shape_type == "三角形 (Triangle)":
    w = st.sidebar.number_input("底邊寬度 (base, b):", value=6.0, step=1.0)
    h = st.sidebar.number_input("直角高度 (height, h):", value=9.0, step=1.0)
    x_base = st.sidebar.number_input("直角頂點 X 座標:", value=0.0, step=1.0)
    y_base = st.sidebar.number_input("直角頂點 Y 座標:", value=0.0, step=1.0)
    is_hole = st.sidebar.checkbox("這是一個挖空區域 (Hole)?")
    cx = x_base + w / 3
    cy = y_base + h / 3

# 2. Xây dựng cấu trúc Prompt kỹ sư (Prompt Engineering) gửi cho AI
prompt_statics = f"""
你現在是一個大一 國立勤益科技大學 智慧自動化工程系 的靜力學助教。
請協助求解以下「複合面積形心」的題目，並嚴格以繁體中文、步驟清晰、表格化呈現計算過程，方便學生逐段驗算與對照課本答案。

【題目已知條件】：
結構包含以下子圖形資訊：
- 圖形幾何種類: {shape_type}
- 尺寸參數: 寬/底={w}, 高度={h}
- 基準點座標位置: ({x_base}, {y_base})
- 區域屬性: {"此區域為挖空孔 active (面積算負值)" if is_hole else "此區域為實體面 (面積算正值)"}

【必須包含的輸出內容】：
1. 說明形心公式的核心原理：$\\bar{{X}} = \\frac{{\\sum A_i x_i}}{{\\sum A_i}}$ 與 $\\bar{{Y}} = \\frac{{\\sum A_i y_i}}{{\\sum A_i}}$。
2. 建立一個 Markdown 計算表格，欄位包含：子圖形項目、面積 $A_i$、單一形心 $x_i$、單一形心 $y_i$、動態乘積 $A_i x_i$、動態乘積 $A_i y_i$。
3. 導出最終的整體複合圖形重心/形心座標確切解答 (\\bar{{X}}, \\bar{{Y}})，並給出清晰的加總數值。
"""

# 3. Chia giao diện chính thành 2 cột (Cột 1: Đồ họa trực quan, Cột 2: Lời giải AI)
col1, col2 = st.columns([4, 5])

with col1:
    st.subheader("🖼️ 幾何圖形即時畫布")
    fig, ax = plt.subplots(figsize=(5, 5))
    
    edge_color = 'red' if is_hole else '#1f77b4'
    fill_color = 'none' if is_hole else '#aec7e8'
    hatch_style = '///' if is_hole else None
    
    if shape_type == "矩形 (Rectangle)":
        rect = patches.Rectangle((x_base, y_base), w, h, linewidth=2, edgecolor=edge_color, facecolor=fill_color, hatch=hatch_style)
        ax.add_patch(rect)
    elif shape_type == "三角形 (Triangle)":
        # Giả định vẽ tam giác vuông chuẩn tại góc tọa độ nhập vào
        triangle_pts = [[x_base, y_base], [x_base + w, y_base], [x_base, y_base + h]]
        poly = patches.Polygon(triangle_pts, linewidth=2, edgecolor=edge_color, facecolor=fill_color, hatch=hatch_style)
        ax.add_patch(poly)
        
    # Vẽ điểm định vị hình tâm của phần tử
    ax.plot(cx, cy, 'ro', label="Sub-Centroid")
    ax.text(cx, cy, f"  C({cx:.1f}, {cy:.1f})", color='red', fontweight='bold')
    
    # Thiết lập khung hệ tọa độ Oxy
    ax.set_xlim(min(0, x_base) - 3, max(10, x_base + w) + 3)
    ax.set_ylim(min(0, y_base) - 3, max(10, y_base + h) + 3)
    ax.grid(True, linestyle='--')
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    st.pyplot(fig)

with col2:
    st.subheader("📝 AI 智慧型逐步解題精靈")
    if st.button("🚀 啟動 AI 求解系統"):
        if not api_key:
            st.error("❌ 請先在左側輸入您的 Gemini API Key 才能連線至運算核心！")
        else:
            with st.spinner("⏳ AI 正在剖析題意並產生繁體中文計算步驟..."):
                try:
                    # Gọi mô hình thế hệ mới với thư viện genai mới nhất
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_statics,
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ 連線失敗，請檢查 API Key 是否正確。錯誤訊息: {e}")
