import unittest
import asyncio
import io

from app.schemas.code import CodeSubmitRequest
from app.services.agent_orchestrator import agent_orchestrator
from app.services.storage_service import storage_service
from app.services.agents.pr_summary_agent import pr_summary_agent
from app.services.agents.remediation_agent import remediation_agent
from app.services.agents.assistant_agent import assistant_agent
from app.services.pdf_report_service import pdf_report_service


class TestMilestone4E2E(unittest.TestCase):

    def setUp(self):
        # -------------------------------------------------------------
        # Sample 1: Simple Python Script (SQLi + Docstring)
        # -------------------------------------------------------------
        self.sample_python_simple = """
import sqlite3

def get_user_data(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    return cursor.fetchall()
"""

        # -------------------------------------------------------------
        # Sample 2: Complex Python Web App (Command Inj + Secret + Smells)
        # -------------------------------------------------------------
        self.sample_python_complex = """
import os
import hashlib
import subprocess

API_SECRET_KEY = "sk_live_9923812938192831293812"

def execute_user_ping(host_ip, config_dict={}):
    # Ping host using shell system call
    os.system("ping -c 1 " + host_ip)
    
def generate_user_token(username):
    try:
        token = hashlib.md5(username.encode()).hexdigest()
        return token
    except:
        return None
"""

        # -------------------------------------------------------------
        # Sample 3: Enterprise Java Class (JDBC SQLi + Hardcoded Pass)
        # -------------------------------------------------------------
        self.sample_java_enterprise = """
package com.security.service;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class UserAuthenticationService {
    private static final String DB_PASSWORD = "SuperSecretPassword123!";

    public boolean authenticateUser(String username, String pass) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/db", "admin", DB_PASSWORD);
            Statement stmt = conn.createStatement();
            String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + pass + "'";
            return stmt.executeQuery(sql).next();
        } catch (Exception e) {
            return false;
        }
    }
}
"""

    def test_e2e_sample_1_python_simple(self):
        print("\n=== Testing E2E Sample 1: Simple Python Script ===")
        findings = asyncio.run(agent_orchestrator.analyze(self.sample_python_simple, "python"))
        self.assertTrue(len(findings) > 0, "Should detect vulnerabilities in Sample 1")

        # Verify SQL Injection detected
        titles = [f.title for f in findings]
        self.assertTrue(any("SQL Injection" in t for t in titles), "Should detect SQL Injection")

        # Test PR Summary & Health Score
        summary = pr_summary_agent.generate_summary("sample1_id", findings, self.sample_python_simple, "python")
        self.assertTrue(summary.health_score < 100)
        self.assertIn("Blocked", summary.verdict)

        # Test PDF Report Generation
        pdf_bytes = pdf_report_service.generate_pdf("sample1_id", "login_simple.py", "python", self.sample_python_simple, findings)
        self.assertTrue(len(pdf_bytes) > 500, "PDF binary should be successfully generated")
        print(f"[OK] Sample 1 PASSED | Health Score: {summary.health_score} | PDF Size: {len(pdf_bytes)} bytes")

    def test_e2e_sample_2_python_complex(self):
        print("\n=== Testing E2E Sample 2: Complex Python Web App ===")
        findings = asyncio.run(agent_orchestrator.analyze(self.sample_python_complex, "python"))
        self.assertTrue(len(findings) >= 3, "Should detect multiple vulnerabilities in Sample 2")

        titles = [f.title for f in findings]
        self.assertTrue(any("Command Injection" in t for t in titles), "Should detect Command Injection")
        self.assertTrue(any("Secret" in t or "Credential" in t or "Hardcoded" in t for t in titles), "Should detect Hardcoded Secret")

        # Test Remediation Agent
        remediations = remediation_agent.remediate_batch(findings, self.sample_python_complex, "python")
        self.assertTrue(len(remediations) > 0)

        # Test PDF Generation with Remediations
        pdf_bytes = pdf_report_service.generate_pdf("sample2_id", "app_service.py", "python", self.sample_python_complex, findings, remediations)
        self.assertTrue(len(pdf_bytes) > 1000)
        print(f"[OK] Sample 2 PASSED | Remediations Generated: {len(remediations)} | PDF Size: {len(pdf_bytes)} bytes")

    def test_e2e_sample_3_java_enterprise(self):
        print("\n=== Testing E2E Sample 3: Enterprise Java Class ===")
        findings = asyncio.run(agent_orchestrator.analyze(self.sample_java_enterprise, "java"))
        self.assertTrue(len(findings) > 0, "Should detect vulnerabilities in Java sample")

        titles = [f.title for f in findings]
        self.assertTrue(any("SQL Injection" in t for t in titles), "Should detect Java JDBC SQL Injection")

        # Test Conversational Assistant RAG grounding for Java
        chat_res = assistant_agent.ask("How can I fix SQL injection in Java JDBC?", "sample3_id", "java")
        self.assertTrue(len(chat_res.response) > 50)
        self.assertTrue(len(chat_res.sources) > 0)
        print(f"[OK] Sample 3 PASSED | Java SQLi Detected | RAG Citations: {[s.title for s in chat_res.sources]}")


if __name__ == "__main__":
    unittest.main()
