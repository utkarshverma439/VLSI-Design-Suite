# VLSI-Design-Suite

A powerful AI-driven platform designed for hardware engineers and students to simplify and accelerate HDL-based design workflows.

![Home Page](https://drive.google.com/uc?id=1y0Iq4qDmUGAgSaHKif-d2Qk7X0BFWaYV)

---

## 🧩 Features

### 🚀 1. HDL Generator
Converts natural language descriptions into syntactically correct, synthesizable Verilog/SystemVerilog/VHDL code with optional syntax validation and optimization suggestions.

![Feature 1](https://drive.google.com/uc?id=1Hk9f0p_Z0cMtgOKaNN9xpkwWO90sOOty)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Feature 1 Output](https://drive.google.com/uc?id=1ERcCVOxncEs0JQxdZPPZlLlBjBk4yPmF)
</details>

---

### 📝 2. Documentation Generator
Generates clean and structured markdown documentation from HDL files, including ports, signals, functionality, and timing behavior.

![Feature 2](https://drive.google.com/uc?id=1po5b_TjnW6RYuQVmhyGaHllfO_7VfJkA)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Feature 2 Output](https://drive.google.com/uc?id=1pq26yg0vmRQTmoxThsD2wNoIQxkjt8dv)
</details>

---

### 🔍 3. Code Explainer
Interactive code analysis that allows users to ask technical questions and get AI-powered HDL design insights.

![Feature 3](https://drive.google.com/uc?id=1s1bSsProXzyf-zy-FWA6Wrnv6Ov_SfHj)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Feature 3 Output](https://drive.google.com/uc?id=1g0CXhWKXe-wng9GLVebf11Pg8MvEBRa4)
</details>

---

### 🛠️ 4. Bug Fix Assistant
Automatically detects and fixes syntax/simulation errors in HDL code by analyzing log outputs and providing corrected versions with explanations.

![Feature 4](https://drive.google.com/uc?id=1IdN5aN3T51WK5zfglPon5rvx097KcfHi)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Feature 4 Output](https://drive.google.com/uc?id=1AYnnGLIPc47FT7g_TwbJoFQIcEjdqz-9)
</details>

---

### ✅ 5. Code Review
Performs automated reviews of HDL code for linting, optimization, synthesis compatibility, coding style, and testability, with severity levels and suggestions.

![Feature 5](https://drive.google.com/uc?id=17548gbvMbjzRQDZ38VI4rDheO3otYJ_3)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Review Output](https://drive.google.com/uc?id=1Bz2gfo4yM4A3AUHWbp_5JLk6x_yloS36)
</details>

---

### 🧪 6. Testbench Generator
Creates comprehensive and configurable testbenches with waveform dumping, self-checking, corner case coverage, and assertions for any uploaded HDL module.

![Feature 6](https://drive.google.com/uc?id=1IXsaKAxWN-9WYWrJZAhMpSkqIbkYW139)

<details>
  <summary>➡️ View Output Sample</summary>

  ![Feature 6 Output](https://drive.google.com/uc?id=1H84WIvpra_m5shtH6St_wUCCw3EKd9nn)
</details>

---

## 📦 Installation

```bash
pip install streamlit
pip install requests
````

Also install the following tools for local HDL validation:

* [Icarus Verilog](http://bleyer.org/icarus/) – for Verilog/SystemVerilog
* [GHDL](https://github.com/ghdl/ghdl) – for VHDL

---

## 🚀 Run the App

```bash
streamlit run app.py
```

Ensure you have your API key set up in `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "your-api-key-here"
```

---

## 📁 Project Structure

```
├── app.py                      # Main Streamlit application
├── README.md                   # Project overview and documentation
└── .streamlit/secrets.toml     # API key config (user-provided)
```

---

## 👨‍💻 Developed By

* **Utkarsh Verma**
* Powered by **OpenRouter + Moonshot AI**
* Inspired by real-world VLSI & FPGA design/debugging challenges

---

## 📜 License

**[Apache License 2.0](LICENSE)** – Free to use, modify, and distribute with attribution and patent protection.

---


