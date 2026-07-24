"""Load secrets from GCP Secret Manager when env vars are unset (local dev with gcloud auth)."""
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

GCP_PROJECT = os.environ.get('GCP_PROJECT', 'matheus-cloud-pessoal')
_CACHE: dict[str, str] = {}


def get_secret(secret_name: str, *, project: str | None = None) -> str:
    """Fetch secret from env, cache, or `gcloud secrets versions access`."""
    env_key = secret_name.upper().replace('-', '_')
    from_env = os.environ.get(env_key, '')
    if from_env:
        return from_env

    if secret_name in _CACHE:
        return _CACHE[secret_name]

    if os.environ.get('GCP_LOAD_SECRETS', 'True').lower() != 'true':
        return ''

    project = project or GCP_PROJECT
    try:
        result = subprocess.run(
            [
                'gcloud', 'secrets', 'versions', 'access', 'latest',
                f'--secret={secret_name}',
                f'--project={project}',
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        value = result.stdout.strip()
        if value:
            _CACHE[secret_name] = value
        return value
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        logger.debug('GCP secret %s unavailable: %s', secret_name, exc)
        return ''
