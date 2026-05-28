import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64

# ==========================================
# 1. 页面与全局美化配置 (Liquid Glass 学习风)
# ==========================================
st.set_page_config(page_title="纯净听写记录仪 Pro", page_icon="🎙️", layout="centered")

# 注入自定义 CSS
st.markdown("""
    <style>
    /* 全局字体和背景 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 50%, #f0e9ff 100%);
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    /* 主标题 */
    h1 {
        text-align: center;
        font-weight: 700;
        font-size: 2.2rem;
        background: linear-gradient(90deg, #2563eb, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* 毛玻璃卡片基础 */
    .glass-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.07);
        animation: slideUp 0.5s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* 音频播放器区域 */
    .audio-area {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        text-align: center;
    }
    
    .audio-label {
        color: #475569;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    audio {
        width: 100%;
        border-radius: 10px;
        margin-top: 8px;
    }
    
    audio::-webkit-media-controls-panel {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
    }
    
    /* 单词信息卡片 */
    .word-info {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        text-align: center;
    }
    
    .word-display {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    
    .meaning-display {
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 400;
    }
    
    /* 按钮组 */
    .button-group {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    /* 表单区域 */
    .form-area {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.07);
    }
    
    /* 输入框美化 */
    [data-testid="stTextInput"] input {
        border-radius: 12px !important;
        border: 1.5px solid rgba(203, 213, 225, 0.6) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stTextInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
        outline: none !important;
    }
    
    /* 按钮美化 */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }
    
    /* 主要按钮 */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }
    
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* 警告/回退按钮 */
    .btn-back > button {
        background: linear-gradient(135deg, #f59e0b, #d97706) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3);
    }
    
    .btn-back > button:hover {
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
    }
    
    /* 重播按钮 */
    .btn-replay > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
    }
    
    .btn-replay > button:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6, #10b981, #3b82f6);
        background-size: 200% 100%;
        animation: shimmer 2s infinite;
        border-radius: 10px;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* 状态提示条 */
    .review-banner {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 16px;
        color: #92400e;
        font-weight: 500;
        font-size: 14px;
        text-align: center;
        animation: fadeIn 0.4s ease-out;
    }
    
    /* Tab 美化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.8) !important;
        color: #2563eb !important;
        font-weight: 600 !important;
    }
    
    /* 表格美化 */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    
    /* Metric 卡片 */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 全局容器 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 700px !important;
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.4), transparent);
        margin: 24px 0;
    }
    
    /* 成功消息 */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(12px);
    }
    
    /* 信息提示 */
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px);
    }
    
    /* 警告提示 */
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px);
    }
    
    /* 错误提示 */
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 状态初始化
# ==========================================
if 'vocab_list' not in st.session_state:
    st.session_state.vocab_list = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'records' not in st.session_state:
    st.session_state.records = []
if 'setup_done' not in st.session_state:
    st.session_state.setup_done = False
if 'is_reviewing' not in st.session_state:
    st.session_state.is_reviewing = False
if 'replay_counter' not in st.session_state:
    st.session_state.replay_counter = 0

# ==========================================
# 3. 核心功能函数
# ==========================================
def parse_markdown_table(md_text):
    """解析 Markdown 表格为字典列表"""
    parsed_data = []
    lines = md_text.strip().split('\n')
    for line in lines:
        if not line.strip() or '---' in line or '单词' in line:
            continue
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            parsed_data.append({"word": parts[0], "meaning": parts[1]})
    return parsed_data

def get_autoplay_audio_html(text):
    """生成带 autoplay 属性的 base64 音频 HTML"""
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    
    audio_html = f'''
        <audio controls autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            您的浏览器不支持音频播放。
        </audio>
    '''
    return audio_html

def generate_markdown_report():
    """生成 Markdown 报告"""
    md_content = "# 📅 每日单词听写记录\n\n"
    md_content += "| 标准拼写 | 标准释义 | 我的拼写 | 我的释义 |\n"
    md_content += "|---|---|---|---|\n"
    for record in st.session_state.records:
        md_content += f"| **{record['std_word']}** | {record['std_meaning']} | {record['user_word']} | {record['user_meaning']} |\n"
    return md_content

def reset_session():
    st.session_state.vocab_list = []
    st.session_state.current_index = 0
    st.session_state.records = []
    st.session_state.setup_done = False
    st.session_state.is_reviewing = False
    st.session_state.replay_counter = 0
    st.rerun()

def go_to_previous():
    """回退到上一个单词"""
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.is_reviewing = True
        st.session_state.replay_counter += 1
        st.rerun()

def replay_current():
    """重播当前单词"""
    st.session_state.replay_counter += 1
    st.rerun()

# ==========================================
# 4. 页面 UI 构建
# ==========================================
st.markdown("<h1>🎙️ 纯净听写记录仪</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>专注输入 • 自动播放 • 随时回听</div>", unsafe_allow_html=True)

# ----------------- 视图 1：数据导入 -----------------
if not st.session_state.setup_done:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📥 导入听写词库")
    
    tab1, tab2 = st.tabs(["📁 上传 .md 文件", "✍️ 粘贴 Markdown 表格"])
    
    parsed_data = None
    
    with tab1:
        st.info("💡 请直接上传由 OpenClaw 或 Obsidian 导出的 .md 单词表文件。")
        uploaded_file = st.file_uploader("选择一个 Markdown 文件", type=['md'])
        if st.button("🚀 从文件开始听写", type="primary", use_container_width=True, key="btn_file"):
            if uploaded_file is not None:
                content = uploaded_file.read().decode("utf-8")
                parsed_data = parse_markdown_table(content)
            else:
                st.warning("请先上传文件！")
                
    with tab2:
        md_input = st.text_area("将 Markdown 表格粘贴在此处：", height=150, 
                                placeholder="| 单词 | 中文释义 |\n|---|---|\n| extraction | 提取 |")
        if st.button("🚀 从文本开始听写", type="primary", use_container_width=True, key="btn_text"):
            if md_input:
                parsed_data = parse_markdown_table(md_input)
            else:
                st.warning("请先粘贴数据！")

    # 处理解析结果
    if parsed_data is not None:
        if parsed_data:
            st.session_state.vocab_list = parsed_data
            st.session_state.setup_done = True
            st.rerun()
        else:
            st.error("解析失败！请检查文件或内容中是否包含标准的 Markdown 表格（由 `|` 分隔）。")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- 视图 2：听写进行中 -----------------
elif st.session_state.current_index < len(st.session_state.vocab_list):
    total = len(st.session_state.vocab_list)
    curr = st.session_state.current_index
    current_word_data = st.session_state.vocab_list[curr]
    
    # 顶部状态栏：进度指示器与防中断导出
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress((curr) / total, text=f"当前进度: {curr + 1} / {total}")
    with col2:
        temp_md = generate_markdown_report()
        st.download_button("💾 暂存", temp_md, file_name="听写暂存记录.md", use_container_width=True)

    st.divider()
    
    # 回听模式提示条
    if st.session_state.is_reviewing:
        st.markdown(
            f"<div class='review-banner'>🔍 你正在修改第 {curr + 1} 个单词，表单已预填充你之前的内容</div>", 
            unsafe_allow_html=True
        )

    # 音频播放区 (自动播放)
    st.markdown("<div class='audio-area'>", unsafe_allow_html=True)
    st.markdown("<div class='audio-label'>🎧 正在听写...</div>", unsafe_allow_html=True)
    
    # 使用 replay_counter 确保每次重播都重新生成音频
    audio_html = get_autoplay_audio_html(current_word_data["word"])
    st.components.v1.html(audio_html, height=60)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 操作按钮组：重播 + 上一个
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
    with btn_col1:
        st.markdown("<div class='btn-replay'>", unsafe_allow_html=True)
        if st.button("🔁 重播", use_container_width=True, key="btn_replay"):
            replay_current()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with btn_col2:
        st.markdown("<div class='btn-back'>", unsafe_allow_html=True)
        if st.button("⏮️ 上一个", use_container_width=True, key="btn_prev", 
                     disabled=(curr == 0)):
            go_to_previous()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with btn_col3:
        pass  # 占位，保持布局平衡
    
    # 单词信息卡片
    st.markdown("<div class='word-info'>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-display'>{current_word_data['word']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='meaning-display'>{current_word_data['meaning']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 盲打输入表单
    with st.container():
        st.markdown("<div class='form-area'>", unsafe_allow_html=True)
        
        # 根据是否处于回听模式，预填充表单数据
        default_word = ""
        default_meaning = ""
        
        if st.session_state.is_reviewing and curr < len(st.session_state.records):
            # 处于回听模式，预填充之前记录的内容
            default_word = st.session_state.records[curr]["user_word"]
            if default_word == "—":
                default_word = ""
            default_meaning = st.session_state.records[curr]["user_meaning"]
            if default_meaning == "—":
                default_meaning = ""
        
        with st.form(key=f"dictation_form_{curr}_{st.session_state.replay_counter}", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                user_w = st.text_input("📝 拼写记录 (Word)", 
                                       value=default_word,
                                       autocomplete="off", 
                                       placeholder="记录你听到的英文")
            with c2:
                user_m = st.text_input("💡 释义记录 (Meaning)", 
                                       value=default_meaning,
                                       autocomplete="off", 
                                       placeholder="记录该词的中文意思")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 根据模式动态显示按钮文本
            if st.session_state.is_reviewing:
                submit_label = "📝 更新并继续 ⏭️"
            else:
                submit_label = "✅ 记录并进入下一个 ⏭️"
            
            submit_btn = st.form_submit_button(submit_label, use_container_width=True)
            
            if submit_btn:
                # 准备记录数据
                new_record = {
                    "std_word": current_word_data["word"],
                    "std_meaning": current_word_data["meaning"],
                    "user_word": user_w.strip() if user_w.strip() else "—",
                    "user_meaning": user_m.strip() if user_m.strip() else "—"
                }
                
                if st.session_state.is_reviewing:
                    # 回听模式：替换当前记录
                    if curr < len(st.session_state.records):
                        st.session_state.records[curr] = new_record
                    else:
                        st.session_state.records.append(new_record)
                    st.session_state.is_reviewing = False
                else:
                    # 正常模式：追加新记录
                    st.session_state.records.append(new_record)
                
                st.session_state.current_index += 1
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------- 视图 3：听写完成与导出 -----------------
else:
    st.balloons()
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.success("🎉 今日听写记录完成！你的专注力很棒。")
    
    # 结果数据看板
    col_a, col_b = st.columns(2)
    col_a.metric("完成词汇量", f"{len(st.session_state.records)} 个")
    col_b.metric("听写状态", "已全部记录")

    st.markdown("### 📊 本次记录对比对照表")
    df = pd.DataFrame(st.session_state.records)
    df.columns = ["标准拼写", "标准释义", "我的拼写", "我的释义"]
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # 导出与重新开始按钮组
    final_md = generate_markdown_report()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="⬇️ 导出 Markdown",
            data=final_md,
            file_name="今日听写对照记录.md",
            mime="text/markdown",
            use_container_width=True,
            type="primary"
        )
    with c2:
        if st.button("🔄 开启新一轮", use_container_width=True):
            reset_session()
    
    st.markdown("</div>", unsafe_allow_html=True)
