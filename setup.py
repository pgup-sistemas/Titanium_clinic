from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="titanium-clinica",
    version="2.0.0",
    description="Sistema Seguro de Confirmação Humanizada no WhatsApp",
    author="Titanium Clinic",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'titanium-clinica=app:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)