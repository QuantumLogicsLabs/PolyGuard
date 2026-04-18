from setuptools import setup, find_packages

setup(
    name="polyguard",
    version="0.1.0",
    description="AI-Powered Code Security Analyzer",
    author="QuantumLogics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "torch>=2.0.0",
        "transformers>=4.38.0",
        "tree-sitter==0.21.3",
        "scikit-learn>=1.4.0",
        "numpy>=1.26.0",
        "pydantic>=2.6.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "lightgbm>=4.3.0",
        "tqdm>=4.66.2",
    ],
)
