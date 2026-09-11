# Contributing to IPL Performance Analytics

Thank you for your interest in contributing to the **IPL Performance Analytics Using Data Science and Analytics** project!

## 🚀 Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all community interactions.

## 🛠️ Development Workflow
1. **Fork the Repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/IPL-Performance-Analytics.git
   cd IPL-Performance-Analytics
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/awesome-analytics-enhancement
   ```
4. **Set Up Environment & Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Run Tests before Committing**:
   ```bash
   pytest -v tests/
   python evaluation/evaluate_data_quality.py
   python evaluation/evaluate_statistics.py
   ```
6. **Submit a Pull Request** with a descriptive summary of your changes.

## 📐 Coding Standards
- Follow **PEP 8** style conventions.
- Maintain comprehensive docstrings for all mathematical functions.
- Do NOT hard-code statistical metrics; all calculations must stem from data.
- Avoid speculative or guaranteed match predictions.
