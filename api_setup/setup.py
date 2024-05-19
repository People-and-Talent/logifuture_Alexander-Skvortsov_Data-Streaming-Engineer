from setuptools import setup, find_packages

setup(
    name="betting_app",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "cassandra-driver",

    ],
    entry_points={
        "console_scripts": [
            "runserver=app.main:run"
        ],
    },
    extras_requires={
        'dev': [
            'pip-tools',
        ],
    },
    python_requires='>=3.8',
)

def run():
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
