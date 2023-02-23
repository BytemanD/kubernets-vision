import nox


@nox.session
def flake8(session):
    session.install("flake8")
    session.run("flake8", "kubevision", 'noxfile.py', 'install')
