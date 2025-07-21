from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rj-ai-toolkit",
    version="0.1.0",
    author="Renjie Wang",
    author_email="renjiewang31@gmail.com",
    description="RJ的AI工具包集合，包含Agent、RAG、Redis等企业级AI开发工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Wang-Theo/rj-ai-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords=[
        "langchain", 
        "agent", 
        "ai", 
        "chatbot", 
        "qwen", 
        "dashscope", 
        "nlp",
        "enterprise",
        "tools",
        "automation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Wang-Theo/rj-ai-toolkit/issues",
        "Source": "https://github.com/Wang-Theo/rj-ai-toolkit",
        "Documentation": "https://github.com/Wang-Theo/rj-ai-toolkit/wiki",
    },
    entry_points={
        "console_scripts": [
            "agent-rj-demo=examples.basic_usage:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
