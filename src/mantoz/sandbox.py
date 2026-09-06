import argparse
import os

from harbor.environments.factory import EnvironmentFactory
from harbor.models.environment_type import EnvironmentType


def resolve_backend() -> EnvironmentType:
    name = os.environ.get("MANTOZ_SANDBOX", EnvironmentType.DOCKER.value)
    try:
        backend = EnvironmentType(name)
    except ValueError:
        raise ValueError(f"unknown sandbox backend: {name!r}") from None
    if backend is EnvironmentType.MODAL:
        EnvironmentFactory.run_preflight(backend)
    return backend


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    if parser.parse_args().show:
        try:
            print(resolve_backend().value)
        except ValueError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
