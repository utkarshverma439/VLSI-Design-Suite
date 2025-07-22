import streamlit as st
import requests
import json
import os
import subprocess
import tempfile
from datetime import datetime
import time
import random
import shutil
import base64

# Initialize session state
if 'current_file' not in st.session_state:
    st.session_state.current_file = {}
if 'conversation' not in st.session_state:
    st.session_state.conversation = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Home"

# Try to get API key from secrets
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        API_KEY = st.secrets["OPENROUTER_API_KEY"]
    else:
        API_KEY = None
except Exception:
    API_KEY = None

# Kimi API call function
def kimi_api_call(prompt, system_message="You are an expert VLSI engineer", model="moonshotai/kimi-k2:free", max_retries=5):
    if not API_KEY:
        st.error("API key not configured. Please configure your API key in secrets.toml.")
        return None
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 2048
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
                continue
            else:
                st.error(f"Processing Error (Attempt {attempt+1}): {response.status_code}")
                time.sleep(2)
                
        except requests.exceptions.RequestException as e:
            st.error(f"Network Error (Attempt {attempt+1}): {str(e)}")
            time.sleep(2)
    
    st.error("Processing failed after multiple attempts. Please try again later.")
    return None

# HDL Language Validation
def validate_hdl_code(code, language):
    if not code.strip():
        return False, "Empty code provided"
    
    tool_name = "iverilog" if language in ["v", "sv"] else "ghdl" if language == "vhd" else None
    if tool_name:
        tool_path = shutil.which(tool_name)
        if not tool_path:
            return False, f"Validation tool not found. Install it to enable this feature."
    
    if os.name == 'nt' and language in ["v", "sv"]:
        tool_name = "iverilog.exe"
    
    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix=f".{language}", delete=False) as tmpfile:
            tmpfile.write(code)
            tmpfile.flush()
            tmp_path = tmpfile.name
            
            if language == "v" or language == "sv":
                cmd = ["iverilog", "-t", "null", tmp_path] if os.name != 'nt' else ["iverilog.exe", "-t", "null", tmp_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    return False, result.stderr
                
            elif language == "vhd":
                result = subprocess.run(["ghdl", "-s", tmp_path], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    return False, result.stderr
            
            return True, "Syntax is valid"
        
    except subprocess.TimeoutExpired:
        return False, "Validation timed out"
    except Exception as e:
        return False, str(e)
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass

# File upload handler
def handle_file_upload(feature_name, allowed_types=["v", "sv", "vhd", "txt"]):
    uploaded_file = st.file_uploader(
        f"Upload HDL file", 
        type=allowed_types,
        key=f"upload_{feature_name}",
        help=f"Supported formats: {', '.join(allowed_types)}"
    )
    
    if uploaded_file:
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == 'v':
            language = "Verilog"
        elif ext == 'sv':
            language = "SystemVerilog"
        elif ext == 'vhd':
            language = "VHDL"
        else:
            language = "Verilog"
        
        st.session_state.current_file[feature_name] = {
            "name": uploaded_file.name,
            "content": uploaded_file.read().decode("utf-8"),
            "language": language
        }
        
        return True
    return False

# Create download link
def create_download_link(content, filename, text):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="color: #4dabf7; text-decoration: none; border: 1px solid #4dabf7; padding: 5px 15px; border-radius: 4px; display: inline-block; margin-top: 10px;">{text}</a>'
    return href

# Custom CSS for dark theme
def inject_custom_css():
    st.markdown("""
    <style>
    /* Header styling */
    .stApp .block-container {
        padding-top: 1rem;
    }
    
    .app-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4dabf7;
        letter-spacing: -0.5px;
    }
    
    /* Tab styling */
    div[role="radiogroup"] {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        width: 100%;
        margin-top: 12px;
    }
    
    div[role="radiogroup"] > label {
        background-color: #2a2a2a;
        border: 1px solid #343a40;
        padding: 0.5rem 1.2rem;
        border-radius: 4px;
        transition: all 0.3s ease;
        margin: 0;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    div[role="radiogroup"] > label:hover {
        background-color: #3a3a3a;
        color: #4dabf7;
        transform: translateY(-2px);
    }
    
    div[role="radiogroup"] > label[data-baseweb="radio"] {
        background-color: #4dabf7 !important;
        color: #121212 !important;
        border-color: #4dabf7 !important;
        box-shadow: 0 2px 8px rgba(77, 171, 247, 0.3);
    }
    
    /* Remove Streamlit's default radio button circles */
    div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    
    /* Add spacing between tabs and content */
    .stRadio > div:first-child {
        margin-bottom: 1.5rem;
    }
    
    /* Improve feature cards */
    .feature-card {
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 6px 24px rgba(0,0,0,0.3);
    }
    
    .section-title {
        font-size: 1.9rem;
        margin-bottom: 1.8rem;
        padding-bottom: 1rem;
    }
    
    /* Fix button styles */
    .stButton > button {
        border-radius: 8px !important;
        padding: 0.6rem 1.8rem !important;
        font-size: 1rem !important;
    }
    
    /* Add gap between columns */
    .stColumn {
        padding: 0 15px;
    }
    </style>
    """, unsafe_allow_html=True)
        
    # Keep the rest of your existing CSS
    st.markdown("""
    <style>
    :root {
        --primary: #4dabf7;
        --secondary: #5c7cfa;
        --background: #121212;
        --surface: #1e1e1e;
        --text-primary: #e9ecef;
        --text-secondary: #adb5bd;
        --success: #51cf66;
        --warning: #ffd43b;
        --danger: #ff6b6b;
        --border: #343a40;
    }
    /* ... rest of your existing CSS ... */
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    :root {
        --primary: #4dabf7;
        --secondary: #5c7cfa;
        --background: #121212;
        --surface: #1e1e1e;
        --text-primary: #e9ecef;
        --text-secondary: #adb5bd;
        --success: #51cf66;
        --warning: #ffd43b;
        --danger: #ff6b6b;
        --border: #343a40;
    }
    
    body {
        background-color: var(--background);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: var(--background);
    }
    
    /* Header styling */
    .header {
        background-color: var(--surface);
        padding: 0.5rem 2rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo {
        height: 50px;
    }
    
    .app-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary);
        letter-spacing: -0.5px;
    }
    
    .tabs {
        display: flex;
        gap: 1.5rem;
        overflow-x: auto;
        padding-bottom: 5px;
    }
    
    .tab {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 0;
        position: relative;
        transition: all 0.3s ease;
        white-space: nowrap;
    }
    
    .tab:hover {
        color: var(--primary);
    }
    
    .tab.active {
        color: var(--primary);
    }
    
    .tab.active::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: var(--primary);
    }
    
    /* Main content */
    .main-container {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 2rem;
    }
    
    .section-title {
        color: var(--primary);
        border-bottom: 2px solid var(--border);
        padding-bottom: 0.8rem;
        margin-bottom: 1.5rem;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .feature-card {
        background-color: var(--surface);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        margin-bottom: 2rem;
        border: 1px solid var(--border);
    }
    
    .card-title {
        color: var(--text-primary);
        font-size: 1.4rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    /* Form elements */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div,
    .stSlider>div>div>div>div {
        background-color: #2d2d2d !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }
    
    .stButton>button {
        background-color: var(--primary) !important;
        color: #121212 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #3b9ae1 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(77, 171, 247, 0.3) !important;
    }
    
    .stDownloadButton>button {
        background-color: var(--success) !important;
        color: #121212 !important;
    }
    
    .stCheckbox>div>div {
        color: var(--text-primary) !important;
    }
    
    /* Footer */
    .footer {
        background-color: var(--surface);
        border-top: 1px solid var(--border);
        padding: 1.5rem 0;
        text-align: center;
        margin-top: 3rem;
    }
    
    .copyright {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Status boxes */
    .info-box {
        background-color: rgba(77, 171, 247, 0.1);
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background-color: rgba(81, 207, 102, 0.1);
        border-left: 4px solid var(--success);
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .error-box {
        background-color: rgba(255, 107, 107, 0.1);
        border-left: 4px solid var(--danger);
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .file-name {
        font-weight: 600;
        color: var(--primary);
    }
    
    /* Code blocks */
    .stCodeBlock>div>div>div {
        background-color: #1a1a1a !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }
    
    /* Feature icons */
    .feature-icon {
        font-size: 1.5rem;
        margin-right: 10px;
        color: var(--primary);
    }
    
    /* Tab container */
    .tab-content {
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Home Page
def home_page():
    st.markdown("""
    <pre>
    <div class="feature-card">
        <h2 class="section-title">About VLSI Design Suite</h2>
        
        <div class="info-box">
            <p>VLSI Design Suite is a comprehensive toolkit for hardware engineers, providing a complete set of tools for modern hardware design and verification.</p>
        </div>
        
        <h3>Key Features</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">🚀 HDL Generator</h4>
                <p>Convert natural language descriptions into production-ready HDL code with syntax validation.</p>
            </div>
            
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">📝 Documentation</h4>
                <p>Automatically generate comprehensive documentation from your HDL code.</p>
            </div>
            
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">🔍 Code Analysis</h4>
                <p>Interactive Q&A to understand complex HDL implementations and identify potential issues.</p>
            </div>
            
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">🛠️ Debugging</h4>
                <p>Diagnose and fix errors using simulation/synthesis logs and expert suggestions.</p>
            </div>
            
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">✅ Code Review</h4>
                <p>Get professional code quality assessments with actionable improvement suggestions.</p>
            </div>
            
            <div style="background: #2a2a2a; padding: 1.5rem; border-radius: 8px; border: 1px solid #343a40;">
                <h4 style="color: var(--primary); margin-bottom: 1rem;">🧪 Testbench</h4>
                <p>Automatically generate comprehensive testbenches for your HDL modules.</p>
            </div>
        </div>
        
        <h3 style="margin-top: 2rem;">Getting Started</h3>
        <ol style="line-height: 2;">
            <li>Select a tool from the navigation tabs</li>
            <li>Enter your design requirements or upload existing HDL files</li>
            <li>Generate results and download them for your projects</li>
        </ol>
    </div>
    </pre>
    """, unsafe_allow_html=True)

# Feature 1: RTL Generator
def rtl_generator():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">🚀</span> HDL Generator</h2>', unsafe_allow_html=True)
        
        with st.expander("ℹ️ Syntax Validation Guide", expanded=False):
            st.markdown("""
            - For Verilog/SystemVerilog: Install [Icarus Verilog](http://bleyer.org/icarus/)
            - For VHDL: Install [GHDL](https://github.com/ghdl/ghdl/releases)
            - Add installation directory to your system PATH
            """)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            language = st.radio("HDL Language:", 
                               ["Verilog", "SystemVerilog", "VHDL"], 
                               index=0,
                               horizontal=True)
        
        with col2:
            with st.expander("Options"):
                validate = st.checkbox("Validate syntax", value=True)
                add_comments = st.checkbox("Include comments", value=True)
                optimize = st.checkbox("Optimization suggestions", value=False)
        
        example_prompts = {
            "4-bit up-down counter": f"Design a 4-bit up-down counter in {language}",
            "8-bit ALU": f"Design an 8-bit ALU in {language} with add, subtract, and, or, xor operations",
            "FIFO buffer": f"Design a parameterized FIFO buffer in {language} with configurable depth",
            "Shift register": f"Create an 8-bit shift register in {language} with parallel load"
        }
        
        selected_example = st.selectbox("Example designs:", list(example_prompts.keys()))
        design_prompt = st.text_area("Design specification:", example_prompts[selected_example], height=150)
        
        if st.button("Generate HDL Code", use_container_width=True):
            enhanced_prompt = (
                f"Generate strictly correct and synthesizable {language} code for: {design_prompt}\n"
                f"Requirements:\n"
                f"- Use efficient and synthesizable constructs\n"
                f"- Follow industry best practices\n"
                f"- Ensure no syntax errors\n"
                f"- Avoid latch inference and timing issues\n"
                f"{'- Include detailed comments' if add_comments else ''}\n"
                f"{'- Suggest optimization opportunities at the end' if optimize else ''}\n"
            )
            
            with st.spinner("Generating HDL code..."):
                system_msg = (
                    "You are an expert hardware design engineer. Generate strictly correct HDL code only. "
                    "Ensure the code follows all syntax rules and avoids common pitfalls."
                )
                
                result = kimi_api_call(enhanced_prompt, system_msg)
                
                if result:
                    code_start = result.find("```") + 3
                    code_end = result.find("```", code_start)
                    code = result[code_start:code_end].strip() if code_start > 2 and code_end > code_start else result
                    
                    if code.startswith("verilog") or code.startswith("vhdl"):
                        code = code.split("\n", 1)[1]
                    
                    st.subheader("Generated HDL Code")
                    st.code(code, language=language.lower())
                    
                    if validate:
                        lang_ext = "v" if language == "Verilog" else "sv" if language == "SystemVerilog" else "vhd"
                        valid, message = validate_hdl_code(code, lang_ext)
                        
                        if valid:
                            st.markdown('<div class="success-box">✅ Syntax validation passed!</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box">❌ Syntax validation failed: {message}</div>', unsafe_allow_html=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d")
                    design_name = selected_example.replace(" ", "_").replace("-", "_").lower()
                    filename = f"{design_name}_{timestamp}.{lang_ext if validate else 'v'}"
                    
                    st.markdown(create_download_link(code, filename, "Download HDL File"), unsafe_allow_html=True)
                    
                    if optimize and "```" not in result:
                        st.subheader("Optimization Suggestions")
                        st.markdown(result)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Feature 2: Documentation Generator
def documentation_generator():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">📝</span> Design Documentation</h2>', unsafe_allow_html=True)
        
        if handle_file_upload("doc"):
            file_info = st.session_state.current_file["doc"]
            st.markdown(f'<div class="info-box">Uploaded: <span class="file-name">{file_info["name"]}</span> ({file_info["language"]})</div>', unsafe_allow_html=True)
            code = st.text_area("HDL Code:", value=file_info["content"], height=300)
        else:
            code = st.text_area("Paste HDL Code:", height=300, key="doc_code_input")
        
        doc_options = st.columns(3)
        with doc_options[0]:
            include_ports = st.checkbox("Port descriptions", value=True)
        with doc_options[1]:
            include_signals = st.checkbox("Signal descriptions", value=True)
        with doc_options[2]:
            include_behavior = st.checkbox("Functional behavior", value=True)
        
        if st.button("Generate Documentation", use_container_width=True) and code:
            with st.spinner("Creating documentation..."):
                prompt = (
                    f"Generate comprehensive documentation for this HDL code:\n\n{code}\n\n"
                    "Documentation should include:\n"
                    f"{'- Module/entity description'}\n"
                    f"{'- Port list with direction, width, and purpose' if include_ports else ''}\n"
                    f"{'- Signal declarations and their roles' if include_signals else ''}\n"
                    f"{'- Functional behavior description' if include_behavior else ''}\n"
                    "- Timing characteristics if any\n"
                    "- Implementation notes\n"
                    "Format the output in Markdown with appropriate headings."
                )
                
                system_msg = (
                    "You are a technical documentation expert. Generate accurate, detailed documentation for HDL code."
                )
                
                result = kimi_api_call(prompt, system_msg)
                
                if result:
                    st.subheader("Design Documentation")
                    st.markdown(result, unsafe_allow_html=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d")
                    filename = f"design_documentation_{timestamp}.md"
                    
                    st.markdown(create_download_link(result, filename, "Download Documentation"), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Feature 3: Code Explainer
def code_explainer():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">🔍</span> Code Analysis</h2>', unsafe_allow_html=True)
        
        if handle_file_upload("explainer"):
            file_info = st.session_state.current_file["explainer"]
            st.markdown(f'<div class="info-box">Uploaded: <span class="file-name">{file_info["name"]}</span> ({file_info["language"]})</div>', unsafe_allow_html=True)
            code = st.text_area("HDL Code:", value=file_info["content"], height=200, key="explainer_code")
        else:
            code = st.text_area("Paste HDL Code:", height=200, key="explainer_code")
        
        if code:
            code_hash = hash(code)
            if code_hash not in st.session_state.conversation:
                st.session_state.conversation[code_hash] = []
        
        suggested_questions = [
            "Why is there an inferred latch?",
            "Explain the functionality of this module",
            "What does this always block do?",
            "Are there any timing issues?",
            "How could this code be optimized?"
        ]
        
        st.caption("Suggested questions:")
        cols = st.columns(3)
        for i, question in enumerate(suggested_questions):
            with cols[i % 3]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    st.session_state.selected_question = question
        
        if 'selected_question' in st.session_state:
            question = st.text_input("Your question:", value=st.session_state.selected_question)
        else:
            question = st.text_input("Your question:", value="Explain this code")
        
        if st.button("Analyze Code", use_container_width=True) and code and question:
            code_hash = hash(code)
            with st.spinner("Analyzing..."):
                prompt = (
                    f"Analyze this HDL code:\n\n{code}\n\n"
                    f"Question: {question}"
                )
                
                system_msg = (
                    "You are a hardware design expert. Analyze the provided code and answer questions technically. "
                    "Identify potential issues and explain concepts clearly."
                )
                
                result = kimi_api_call(prompt, system_msg)
                
                if result:
                    if code_hash not in st.session_state.conversation:
                        st.session_state.conversation[code_hash] = []
                    
                    st.session_state.conversation[code_hash].append(("user", question))
                    st.session_state.conversation[code_hash].append(("assistant", result))
                    
                    st.markdown(f'<div class="info-box"><strong>Analysis:</strong></div>', unsafe_allow_html=True)
                    st.markdown(result)
        
        if code:
            code_hash = hash(code)
            if code_hash in st.session_state.conversation and st.session_state.conversation[code_hash]:
                st.subheader("Conversation History")
                for role, msg in st.session_state.conversation[code_hash]:
                    if role == "user":
                        st.markdown(f'**You:** {msg}')
                    else:
                        st.markdown(f'**Analysis:**')
                        st.markdown(msg)
                
                if st.button("Clear History", use_container_width=True):
                    st.session_state.conversation[code_hash] = []
                    st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Feature 4: Bug Fixer
def bug_fixer():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">🛠️</span> Debugging Assistant</h2>', unsafe_allow_html=True)
        
        if handle_file_upload("bugfix"):
            file_info = st.session_state.current_file["bugfix"]
            st.markdown(f'<div class="info-box">Uploaded: <span class="file-name">{file_info["name"]}</span> ({file_info["language"]})</div>', unsafe_allow_html=True)
            code = st.text_area("HDL Code:", value=file_info["content"], height=200)
        else:
            code = st.text_area("Paste HDL Code:", height=200, key="bugfix_code_input")
        
        error_log = st.text_area("Error Logs:", height=100, 
                               placeholder="Paste simulation/synthesis errors here", key="bugfix_code_input")
        
        common_errors = {
            "Latch Inference": "Warning: Inferring latch for variable",
            "Blocking/Non-blocking": "Warning: Use of blocking assignment in sequential block",
            "Syntax Error": "Syntax error near",
            "Undefined Signal": "Error: Undefined signal"
        }
        
        st.caption("Common error patterns:")
        cols = st.columns(4)
        for i, (name, pattern) in enumerate(common_errors.items()):
            with cols[i]:
                if st.button(name, key=f"e_{i}", use_container_width=True):
                    st.session_state.error_log = pattern
        
        if 'error_log' in st.session_state:
            error_log = st.text_area(" ", value=st.session_state.error_log, height=100)
        
        if st.button("Diagnose and Fix", use_container_width=True) and code:
            with st.spinner("Analyzing issues..."):
                prompt = (
                    f"Analyze and fix this HDL code based on error logs:\n\n"
                    f"Code:\n{code}\n\n"
                    f"Errors:\n{error_log if error_log else 'No error logs provided'}\n\n"
                    "Provide:\n"
                    "1. Fixed code in a code block\n"
                    "2. Explanation of the issues\n"
                    "3. List of changes made\n"
                    "4. Prevention suggestions"
                )
                
                system_msg = (
                    "You are a hardware debugging expert. Identify and fix HDL code issues. "
                    "Explain the root cause and how your solution addresses it."
                )
                
                result = kimi_api_call(prompt, system_msg)
                
                if result:
                    code_start = result.find("```") + 3
                    code_end = result.find("```", code_start)
                    fixed_code = result[code_start:code_end].strip() if code_start > 2 and code_end > code_start else result
                    
                    explanation = result
                    if code_start > 2 and code_end > code_start:
                        explanation = result[:code_start-3] + result[code_end+3:]
                    
                    st.subheader("Fixed Code")
                    st.code(fixed_code)
                    
                    st.subheader("Analysis")
                    st.markdown(explanation)
                    
                    if fixed_code and "```" not in fixed_code:
                        timestamp = datetime.now().strftime("%Y%m%d")
                        filename = f"fixed_design_{timestamp}.v"
                        st.markdown(create_download_link(fixed_code, filename, "Download Fixed Code"), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Feature 5: Code Reviewer
def code_reviewer():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">✅</span> Code Review</h2>', unsafe_allow_html=True)
        
        if handle_file_upload("review"):
            file_info = st.session_state.current_file["review"]
            st.markdown(f'<div class="info-box">Uploaded: <span class="file-name">{file_info["name"]}</span> ({file_info["language"]})</div>', unsafe_allow_html=True)
            code = st.text_area("HDL Code:", value=file_info["content"], height=300)
        else:
            code = st.text_area("Paste HDL Code:", height=300)
        
        focus_areas = st.multiselect(
            "Review Focus:",
            ["Linting", "Optimization", "Style", "Synthesis", "Testability", "CDC"],
            ["Linting", "Optimization", "Style"]
        )
        
        severity_level = st.select_slider(
            "Review Strictness:",
            options=["Informational", "Moderate", "Strict"],
            value="Moderate"
        )
        
        if st.button("Perform Code Review", use_container_width=True) and code:
            with st.spinner("Reviewing code..."):
                prompt = (
                    f"Review this HDL code with {severity_level.lower()} strictness:\n{code}\n\n"
                    f"Focus on: {', '.join(focus_areas)}\n\n"
                    "Provide a code review with:\n"
                    "- Categorized findings (Critical, Warning, Suggestion)\n"
                    "- Specific code locations\n"
                    "- Explanation of issues\n"
                    "- Suggested improvements\n"
                    "- Overall quality assessment"
                )
                
                system_msg = (
                    "You are an experienced code reviewer. Provide professional, actionable suggestions. "
                    "Use a structured format with clear severity levels."
                )
                
                result = kimi_api_call(prompt, system_msg)
                
                if result:
                    st.subheader("Code Review Report")
                    st.markdown(result)
                    
                    timestamp = datetime.now().strftime("%Y%m%d")
                    filename = f"code_review_{timestamp}.md"
                    st.markdown(create_download_link(result, filename, "Download Review Report"), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Feature 6: Testbench Generator
def testbench_generator():
    with st.container():
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title"><span class="feature-icon">🧪</span> Testbench Creation</h2>', unsafe_allow_html=True)
        
        if handle_file_upload("testbench"):
            file_info = st.session_state.current_file["testbench"]
            st.markdown(f'<div class="info-box">Uploaded: <span class="file-name">{file_info["name"]}</span> ({file_info["language"]})</div>', unsafe_allow_html=True)
            code = st.text_area("Module Code:", value=file_info["content"], height=300)
            language = file_info["language"]
        else:
            code = st.text_area("Paste Module Code:", height=300)
            language = st.radio("HDL Language:", 
                              ["Verilog", "SystemVerilog"], 
                              index=0,
                              horizontal=True)
        
        with st.expander("Configuration Options"):
            col1, col2 = st.columns(2)
            with col1:
                test_type = st.selectbox("Test Type:", 
                                        ["Basic Functional", "Randomized", "Corner Case", "Assertion-Based"],
                                        index=0)
                clock_period = st.slider("Clock Period (ns):", 1, 100, 10)
            with col2:
                num_tests = st.slider("Test Cases:", 10, 1000, 50)
                include_coverage = st.checkbox("Functional Coverage", value=False)
                include_waves = st.checkbox("Waveform Dumping", value=True)
        
        if st.button("Generate Testbench", use_container_width=True) and code:
            with st.spinner("Creating testbench..."):
                prompt = (
                    f"Write a comprehensive {language} testbench for this module:\n\n{code}\n\n"
                    f"Requirements:\n"
                    f"- Test Type: {test_type}\n"
                    f"- Clock Period: {clock_period}ns\n"
                    f"- Test Cases: {num_tests}\n"
                    f"{'- Functional Coverage' if include_coverage else ''}\n"
                    f"{'- Waveform Dumping' if include_waves else ''}\n"
                    f"- Self-checking mechanisms\n"
                    f"- Detailed comments\n"
                    f"- Modern verification techniques"
                )
                
                system_msg = (
                    "You are a verification engineer. Create a professional testbench."
                )
                
                result = kimi_api_call(prompt, system_msg)
                
                if result:
                    code_start = result.find("```") + 3
                    code_end = result.find("```", code_start)
                    tb_code = result[code_start:code_end].strip() if code_start > 2 and code_end > code_start else result
                    
                    st.subheader("Testbench Code")
                    st.code(tb_code, language=language.lower())
                    
                    timestamp = datetime.now().strftime("%Y%m%d")
                    ext = "sv" if language == "SystemVerilog" else "v"
                    filename = f"testbench_{timestamp}.{ext}"
                    st.markdown(create_download_link(tb_code, filename, "Download Testbench"), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
def footer():
    st.markdown("""
    <div class="footer">
        <p class="copyright">© 2025 VLSI Design Suite. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Main App
def main():
    st.set_page_config(
        page_title="VLSI Design Suite",
        # page_icon="🔌",
        page_icon="logo.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    inject_custom_css()

    # Initialize session state for tab tracking
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Home"

    # Define tab names
    tab_names = [
        "Home", "HDL Generator", "Documentation", "Code Analysis",
        "Debugging", "Code Review", "Testbench"
    ]

    # Create header container
    header = st.container()
    with header:
        col_title, col_tabs = st.columns([1, 3])

        with col_title:
            # App name only, no logo
            st.markdown("""
            <div style="font-size: 24px; font-weight: bold; margin-left: 10px;">
                VLSI Design Suite
            </div>
            """, unsafe_allow_html=True)

        with col_tabs:
            selected_tab = st.radio(
                "Navigation:",
                tab_names,
                index=tab_names.index(st.session_state.current_tab),
                horizontal=True,
                label_visibility="collapsed",
                key="nav_radio"
            )

    # Add spacing between header and content
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    # Update selected tab in session
    st.session_state.current_tab = selected_tab

    # Render selected tab's content
    if selected_tab == "Home":
        home_page()
    elif selected_tab == "HDL Generator":
        rtl_generator()
    elif selected_tab == "Documentation":
        documentation_generator()
    elif selected_tab == "Code Analysis":
        code_explainer()
    elif selected_tab == "Debugging":
        bug_fixer()
    elif selected_tab == "Code Review":
        code_reviewer()
    elif selected_tab == "Testbench":
        testbench_generator()

    # Footer
    footer()


if __name__ == "__main__":
    main()