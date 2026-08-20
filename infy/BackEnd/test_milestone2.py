import unittest
from app.services.code_analysis_service import code_analysis_service

class TestMilestone2Detection(unittest.TestCase):
    def test_python_mutable_default(self):
        code = """
def process_data(items=[]):
    items.append(1)
    return items
"""
        findings = code_analysis_service.analyze_code(code, "python")
        titles = [f.title for f in findings]
        self.assertIn("Mutable Default Argument", titles)

    def test_python_sql_injection(self):
        code = """
def get_user(db, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return db.execute(query)
"""
        findings = code_analysis_service.analyze_code(code, "python")
        titles = [f.title for f in findings]
        self.assertIn("SQL Injection Risk", titles)

    def test_java_command_injection(self):
        code = """
public class Commander {
    public void run(String cmd) throws Exception {
        Runtime.getRuntime().exec("ping " + cmd);
    }
}
"""
        findings = code_analysis_service.analyze_code(code, "java")
        titles = [f.title for f in findings]
        self.assertIn("Command Injection Risk", titles)

    def test_javascript_dom_xss(self):
        code = """
function updateDOM(userInput) {
    document.getElementById("output").innerHTML = userInput;
}
"""
        findings = code_analysis_service.analyze_code(code, "javascript")
        titles = [f.title for f in findings]
        self.assertIn("Cross-Site Scripting (XSS) Risk", titles)

if __name__ == "__main__":
    unittest.main()
