from app.schemas.analysis import Finding
from app.services.agents.remediation_agent import remediation_agent


finding = Finding(
    type="security_vulnerability",
    title="Cross-Site Scripting (XSS)",
    severity="high",
    line=2,
    description=(
        "Untrusted user input is directly inserted into an HTML response "
        "without proper output encoding."
    ),
    recommendation=(
        "Escape or sanitize user-controlled data before rendering it in HTML."
    ),
    code_snippet='return "<h1>" + username + "</h1>"',
)

code = """
from flask import Flask, request

app = Flask(__name__)

@app.route("/hello")
def hello():
    username = request.args.get("name")
    return "<h1>" + username + "</h1>"
"""

result = remediation_agent.remediate(
    finding=finding,
    code=code,
    language="python",
)

print("=== REMEDIATION RESULT ===")
print("Recommendation:")
print(result["recommendation"])

print("\nCorrected Code:")
print(result["corrected_code"])

print("\nExplanation:")
print(result["explanation"])

print("\nWhy It Works:")
print(result["why_it_works"])