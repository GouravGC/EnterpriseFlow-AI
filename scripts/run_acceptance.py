
"""Cross-environment acceptance tests for EnterpriseFlow AI.

Run from the project root:
    python scripts/run_acceptance.py --base-url http://127.0.0.1:8000

Render:
    python scripts/run_acceptance.py --base-url https://YOUR-API.onrender.com

GCP:
    python scripts/run_acceptance.py --base-url https://YOUR-CLOUD-RUN-URL
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "knowledge_base" / "it_support_sop.md"

GROUNDED_QUESTION = (
    "What should an employee do if their account is locked "
    "after repeated failed login attempts?"
)

UNKNOWN_QUESTION = (
    "What is the company's travel reimbursement limit? "
    "Give the exact amount."
)

GROUNDING_TERMS = ("account", "recovery")

ABSTENTION_TERMS = (
    "not provide enough information",
    "does not provide enough information",
    "not specified",
    "not available in",
    "cannot determine",
    "can't determine",
    "do not contain",
    "don't contain",
    "no information",
    "not mentioned",
    "not found in",
    "unable to determine",
)


class AcceptanceError(RuntimeError):
    """Raised when an acceptance check fails."""


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AcceptanceError(message)
    print(f"PASS  {message}")


def request_json(url, method="GET", payload=None, timeout=90):
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(raw) if raw else {}

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        return exc.code, body

    except (urllib.error.URLError, TimeoutError) as exc:
        raise AcceptanceError(
            f"Request failed for {url}: {exc}"
        ) from exc


def upload_document(url, document_path, timeout=90):
    boundary = "----EnterpriseFlowAcceptanceBoundary7MA4YWxkTrZu0gW"
    filename = document_path.name
    content = document_path.read_bytes()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: text/markdown; charset=utf-8\r\n\r\n"
    ).encode("utf-8")

    body += content
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            result = json.loads(raw) if raw else {}

            if response.status not in (200, 201):
                raise AcceptanceError(
                    f"Upload failed ({response.status}): {result}"
                )

            return result

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise AcceptanceError(
            f"Upload failed ({exc.code}): {raw}"
        ) from exc

    except (urllib.error.URLError, TimeoutError) as exc:
        raise AcceptanceError(
            f"Upload request failed: {exc}"
        ) from exc


def main():
    parser = argparse.ArgumentParser(
        description="EnterpriseFlow AI cross-environment acceptance tests"
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the FastAPI service",
    )
    parser.add_argument(
        "--document",
        type=Path,
        default=DEFAULT_DOCUMENT,
        help="Canonical SOP document to upload",
    )
    parser.add_argument(
        "--skip-unknown-question",
        action="store_true",
        help="Skip the LLM abstention check",
    )

    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    document = args.document.resolve()

    if not document.is_file():
        print(f"FAIL  Document not found: {document}", file=sys.stderr)
        return 2

    print("\nEnterpriseFlow AI acceptance tests")
    print(f"Target: {base_url}")
    print(f"Document: {document}\n")

    try:
        code, root = request_json(f"{base_url}/")
        check(code == 200, "API root returns HTTP 200")
        check("message" in root, "API root response has the expected structure")

        code, health = request_json(f"{base_url}/health")
        check(code == 200, "Health endpoint returns HTTP 200")
        check(health.get("status") == "healthy", "Application health is healthy")

        uploaded = upload_document(
            f"{base_url}/documents",
            document,
        )

        check(
            int(uploaded.get("chunks_indexed", 0)) > 0,
            "Canonical SOP produces indexed chunks",
        )
        check(
            uploaded.get("filename") == document.name,
            "Upload response reports the correct filename",
        )

        print(f"      Chunks indexed in this upload: {uploaded['chunks_indexed']}")

        code, document_status = request_json(
            f"{base_url}/documents/status"
        )

        check(code == 200, "Document status endpoint returns HTTP 200")
        check(
            int(document_status.get("indexed_chunks", 0)) > 0,
            "Knowledge base contains indexed chunks",
        )

        code, result = request_json(
            f"{base_url}/ask",
            method="POST",
            payload={"question": GROUNDED_QUESTION},
            timeout=120,
        )

        check(code == 200, "Grounded question returns HTTP 200")

        answer = str(result.get("answer", "")).casefold()

        check(bool(answer.strip()), "Grounded answer is not empty")
        check(
            all(term in answer for term in GROUNDING_TERMS),
            "Grounded answer mentions the account recovery process",
        )

        sources = result.get("sources", [])

        check(
            isinstance(sources, list),
            "Answer includes a sources list",
        )
        check(
            any(
                isinstance(source, dict)
                and source.get("filename") == document.name
                for source in sources
            ),
            "Answer cites the canonical SOP filename",
        )

        if not args.skip_unknown_question:
            code, unknown_result = request_json(
                f"{base_url}/ask",
                method="POST",
                payload={"question": UNKNOWN_QUESTION},
                timeout=120,
            )

            check(
                code == 200,
                "Out-of-scope question returns HTTP 200",
            )

            unknown_answer = str(
                unknown_result.get("answer", "")
            ).casefold()

            check(
                bool(unknown_answer.strip()),
                "Out-of-scope question returns a response",
            )

            check(
                any(term in unknown_answer for term in ABSTENTION_TERMS),
                "Out-of-scope answer acknowledges missing information",
            )

        print("\nALL SELECTED ACCEPTANCE CHECKS PASSED.")
        print(
            "Note: LLM wording can vary. These checks validate key facts, "
            "not identical wording."
        )
        return 0

    except AcceptanceError as exc:
        print(f"\nACCEPTANCE TEST FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
