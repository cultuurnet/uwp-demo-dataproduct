"""
Python Version Buildpack Validation

Checks if the Python version specified in .python-version is supported
by the Paketo buildpack (io.buildpacks.stacks.jammy).

This check should run before any transformation code executes.
"""

import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# Configuration
GITHUB_API_URL = "https://api.github.com/repos/paketo-buildpacks/cpython/contents/buildpack.toml"
CACHE_FILE = Path.home() / ".paketo_python_versions_cache.json"
CACHE_DURATION = 3600  # 1 hour


def _parse_buildpack_toml(content: str) -> List[str]:
    """Parse buildpack.toml to extract Python versions from dependency blocks."""
    versions = []
    for block in re.findall(r'\[\[metadata\.dependencies\]\](.*?)(?=\[\[|\Z)', content, re.DOTALL):
        match = re.search(r'version\s*=\s*["\']([\d.]+)["\']', block)
        if match:
            versions.append(match.group(1))
    return sorted(set(versions), key=lambda v: tuple(map(int, v.split('.'))))


def _query_versions() -> List[str]:
    """Query supported Python versions from Paketo buildpack via GitHub API."""
    try:
        req = Request(GITHUB_API_URL, headers={"Accept": "application/vnd.github.v3+json"})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
                return _parse_buildpack_toml(content)
    except (HTTPError, URLError) as e:
        logger.debug(f"Error querying buildpack versions: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error: {type(e).__name__}: {e}")
    return []


def _get_supported_versions() -> List[str]:
    """Get supported versions, using cache if available."""
    # Try cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
                if time.time() - cache.get('timestamp', 0) < CACHE_DURATION:
                    return cache.get('versions', [])
        except Exception:
            pass
    
    # Query and cache
    versions = _query_versions()
    if versions:
        try:
            CACHE_FILE.write_text(json.dumps({'timestamp': time.time(), 'versions': versions}))
        except Exception:
            pass
    
    return versions


def check_python_version(python_version_file: str = ".python-version") -> None:
    """
    Check if Python version is supported by Paketo buildpack.
    
    Called at the start of main.py before any transformation code executes.
    """
    # Read Python version
    version_path = Path(__file__).parent.parent / python_version_file
    try:
        specified_version = version_path.read_text().strip()
    except Exception:
        logger.warning(f"Could not read {python_version_file}. Skipping validation.")
        return
    
    logger.info(f"Checking if Python version {specified_version} is supported by Paketo buildpack...")
    
    # Get supported versions
    supported_versions = _get_supported_versions()
    if not supported_versions:
        logger.warning("Could not query supported versions. Skipping validation.")
        return
    
    # Check compatibility
    if specified_version in supported_versions:
        logger.info(f"✓ Python version {specified_version} is supported.")
        return
    
    # Version not supported - log warning
    logger.warning("=" * 80)
    logger.warning("⚠️  WARNING: Python version is NOT supported by Paketo buildpack!")
    logger.warning(f"   Specified version: {specified_version}")
    logger.warning(f"   Supported versions: {', '.join(supported_versions)}")
    logger.warning("")
    logger.warning("   Building this dataproduct will FAIL in production environment.")
    logger.warning("")
    logger.warning("   To fix this issue:")
    logger.warning("   1. Delete the virtual environment folder: rm -rf venv")
    logger.warning("   2. Update .python-version to a supported version (e.g., 3.11.14)")
    logger.warning("=" * 80)

